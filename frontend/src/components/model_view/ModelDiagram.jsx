// src/components/model_view/ModelDiagram.jsx
import { useMemo, useRef, useState, useCallback } from "react";
import StateNode from "./StateNode";
import DiagramEdges from "./DiagramEdges";
import { generateStateColorMap } from "./stateColors";

import { estimateNodeHeight } from "./layout/estimateNodeHeight";
import { computeStateLayout } from "./layout/computeStateLayout";
import { useElementSize } from "./hooks/useElementSize";

import {
  buildEventsByName,
  computeStateEventTiles,
  transitionsDictToEdges,
} from "./utils/modelDiagramUtils";

export default function ModelDiagram({ model, onSelectEvent }) {
  const eventData = model.event_data ?? [];
  const transitionsDict =
    model.transition_matrix_data?.metadata?.transitions ?? {};
  const stateDiagram =
    model.transition_matrix_data?.metadata?.state_diagram ?? [];

  // selected state controls which arrows are visible
  const [selectedState, setSelectedState] = useState(null);

  // Measure the visible viewport width
  const viewportRef = useRef(null);
  const { width: viewportWidth } = useElementSize(viewportRef);

  // Flatten state_diagram into a single ordered list (row-major)
  const orderedStateNames = useMemo(
    () => (stateDiagram ?? []).flat().filter(Boolean),
    [stateDiagram]
  );

  // Compute max columns in any row (for dynamic node sizing)
  const maxCols = useMemo(() => {
    const rows = stateDiagram ?? [];
    const counts = rows.map((r) => (r ?? []).filter(Boolean).length);
    return Math.max(1, ...counts);
  }, [stateDiagram]);

  // Dynamic node width: expands when there's space, but stays reasonable when many cols
  const nodeWidth = useMemo(() => {
      const minNodeW = 260;
      const maxNodeW = 420;

      // This is the only padding you’ll “guarantee” to the card edges
      const sidePad = 24 * 2;

      // Small minimum gap between nodes (still readable)
      const minGap = 40;

      const vw = viewportWidth ?? 0;
      if (!vw) return minNodeW;

      // Allocate as much width as possible to nodes, leaving only min gaps + side padding
      const usableForNodes = vw - sidePad - (maxCols - 1) * minGap;

      const ideal = usableForNodes / maxCols;

      return Math.max(minNodeW, Math.min(maxNodeW, ideal));
    }, [viewportWidth, maxCols]);


  const eventsByName = useMemo(() => buildEventsByName(eventData), [eventData]);

  // Tiles only for states we actually render
  const stateEventTiles = useMemo(
    () =>
      computeStateEventTiles({
        ordered_state_names: orderedStateNames,
        event_data: eventData,
      }),
    [orderedStateNames, eventData]
  );

  // Estimated heights (fallback)
  const estimatedHeights = useMemo(() => {
    const m = new Map();
    for (const s of orderedStateNames) {
      const n = stateEventTiles?.[s]?.length ?? 0;
      m.set(s, estimateNodeHeight(n));
    }
    return m;
  }, [orderedStateNames, stateEventTiles]);

  // Measured heights from the DOM (authoritative once available)
  const [measuredHeights, setMeasuredHeights] = useState(() => new Map());

  // callback ref factory: one per state name
  const makeMeasureRef = useCallback(
    (stateName) => (el) => {
      if (!el) return;

      const h = el.offsetHeight || 0;
      if (!h) return;

      setMeasuredHeights((prev) => {
        const prevH = prev.get(stateName);
        if (prevH === h) return prev; // no change
        const next = new Map(prev);
        next.set(stateName, h);
        return next;
      });
    },
    []
  );

  // Effective heights: measured if available, otherwise estimated
  const effectiveHeights = useMemo(() => {
    const m = new Map();
    for (const s of orderedStateNames) {
      m.set(s, measuredHeights.get(s) ?? estimatedHeights.get(s) ?? 300);
    }
    return m;
  }, [orderedStateNames, measuredHeights, estimatedHeights]);

  // Layout AFTER we know heights, viewport width, and node width
  const layoutByState = useMemo(
    () =>
      computeStateLayout({
        stateDiagram,
        stateHeights: effectiveHeights,
        viewportWidth,
        nodeWidth,
      }),
    [stateDiagram, effectiveHeights, viewportWidth, nodeWidth]
  );

  // Minimal “state objects” in diagram order
  const states = useMemo(() => {
    return orderedStateNames.map((name) => ({
      name,
      label: name,
      layout: layoutByState.get(name) ?? { x: 80, y: 80 }, // safe fallback
    }));
  }, [orderedStateNames, layoutByState]);

  // For faster lookups when drawing arrows
  const stateByName = useMemo(() => {
    const m = new Map();
    for (const s of states) m.set(s.name, s);
    return m;
  }, [states]);

  const stateColorMap = useMemo(
    () =>
      generateStateColorMap(states.map((s) => ({ id: s.name, label: s.label }))),
    [states]
  );

  const edges = useMemo(
    () => transitionsDictToEdges(transitionsDict),
    [transitionsDict]
  );

  // only show edges for the selected state (outgoing only)
  const visibleEdges = useMemo(() => {
    if (!selectedState) return [];
    return edges.filter((e) => e.from === selectedState);
  }, [edges, selectedState]);

  const canvas = useMemo(() => {
    const margin = 200;

    const maxX = Math.max(
      ...states.map((s) => (s.layout?.x ?? 0) + nodeWidth),
      0
    );

    const maxY = Math.max(
      ...states.map(
        (s) => (s.layout?.y ?? 0) + (effectiveHeights.get(s.name) ?? 300)
      ),
      0
    );

    // Ensure canvas is at least as wide as the viewport, so expansion is visible
    const minW = (viewportWidth ?? 0) + 40;

    return { width: Math.max(maxX + margin, minW), height: maxY + margin };
  }, [states, effectiveHeights, viewportWidth, nodeWidth]);

  return (
    <div className="rounded-2xl border bg-white">
      {/* Scrollable viewport */}
      <div
        ref={viewportRef}
        className="relative overflow-auto rounded-2xl max-h-[70vh]"
      >
        {/* Full canvas */}
        <div
          className="relative"
          style={{ width: canvas.width, height: canvas.height }}
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) setSelectedState(null);
          }}
        >
          <DiagramEdges
            edges={visibleEdges}
            stateByName={stateByName}
            stateHeights={effectiveHeights}
            stateColorMap={stateColorMap}
            canvas={canvas}
            nodeWidth={nodeWidth}
          />

          {/* State nodes (wrapped so we can measure the real DOM height) */}
          {states.map((s) => (
            <div
              key={s.name}
              ref={makeMeasureRef(s.name)}
              className="absolute"
              style={{
                left: s.layout.x,
                top: s.layout.y,
                width: nodeWidth,
              }}
              onMouseDown={(e) => e.stopPropagation()}
            >
              <StateNode
                state={s}
                eventsByName={eventsByName}
                eventNames={stateEventTiles?.[s.name] ?? []}
                onSelectEvent={onSelectEvent}
                onSelectState={(name) =>
                  setSelectedState((prev) => (prev === name ? null : name))
                }
                isSelected={selectedState === s.name}
                width={nodeWidth}
                colors={stateColorMap.get(s.name)}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


