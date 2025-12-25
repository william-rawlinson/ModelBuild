// src/components/model_view/ModelDiagram.jsx
import { useMemo } from "react";
import StateNode from "./StateNode";
import { indexById } from "./diagramUtils";
import { generateStateColorMap } from "./stateColors";

function estimateNodeHeight(eventCount) {
  const header = 66;
  const padding = 32;
  const tile = 54;
  const gap = 8;
  const empty = 24;

  if (eventCount === 0) return header + padding + empty;
  return header + padding + eventCount * tile + (eventCount - 1) * gap;
}

export default function ModelDiagram({ model, onSelectEvent }) {
  const statesById = useMemo(() => indexById(model.states), [model.states]);
  const eventsById = useMemo(() => indexById(model.events), [model.events]);

  const stateColorMap = useMemo(
    () => generateStateColorMap(model.states),
    [model.states]
  );

  const nodeW = 280;

  const stateHeights = useMemo(() => {
    const m = new Map();
    for (const s of model.states) {
      const n = model.state_event_tiles?.[s.id]?.length ?? 0;
      m.set(s.id, estimateNodeHeight(n));
    }
    return m;
  }, [model.states, model.state_event_tiles]);

  const canvas = useMemo(() => {
    const margin = 200;

    const maxX = Math.max(...model.states.map((s) => s.layout.x + nodeW), 0);

    const maxY = Math.max(
      ...model.states.map((s) => s.layout.y + (stateHeights.get(s.id) ?? 300)),
      0
    );

    return { width: maxX + margin, height: maxY + margin };
  }, [model.states, stateHeights]);

  return (
    <div className="relative overflow-visible rounded-2xl border bg-white">
      <div
        className="relative"
        style={{ width: canvas.width, height: canvas.height }}
      >
        {/* Arrows */}
        <svg
          className="absolute inset-0"
          width={canvas.width}
          height={canvas.height}
        >
          <defs>
              {Array.from(stateColorMap.entries()).map(([stateId, colors]) => (
                <marker
                  key={stateId}
                  id={`arrow-${stateId}`}
                  markerWidth="10"
                  markerHeight="10"
                  refX="9"
                  refY="5"
                  orient="auto"
                  markerUnits="strokeWidth"
                >
                  <path
                    d="M 0 0 L 10 5 L 0 10 z"
                    fill={colors.arrowHex}   // 🔑 explicit colour
                  />
                </marker>
              ))}
            </defs>


          {model.transitions.map((t) => {
            const from = statesById.get(t.from);
            const to = statesById.get(t.to);
            if (!from || !to) return null;

            const fromH = stateHeights.get(from.id) ?? 300;
            const toH = stateHeights.get(to.id) ?? 300;

            const x1 = from.layout.x + nodeW;
            const y1 = from.layout.y + fromH / 2;
            const x2 = to.layout.x;
            const y2 = to.layout.y + toH / 2;

            const dx = Math.max(60, (x2 - x1) / 2);
            const path = `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${
              x2 - dx
            } ${y2}, ${x2} ${y2}`;

            const arrowColor =
            stateColorMap.get(from.id)?.arrowHex ?? "#94a3b8"; // slate-400 fallback

            return (
              <path
                key={t.id}
                d={path}
                stroke={arrowColor}        // 🔑 explicit colour
                strokeWidth="2"
                fill="none"
                markerEnd={`url(#arrow-${from.id})`}
              />
            );
          })}
        </svg>

        {/* State nodes */}
        {model.states.map((s) => (
          <StateNode
            key={s.id}
            state={s}
            events={eventsById}
            eventIds={model.state_event_tiles?.[s.id] ?? []}
            onSelectEvent={onSelectEvent}
            width={nodeW}
            colors={stateColorMap.get(s.id)}
          />
        ))}
      </div>
    </div>
  );
}
