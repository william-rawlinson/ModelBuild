// src/components/model_view/DiagramEdges.jsx
import React, { useMemo } from "react";

const PORT_SPACING = 10;
const PORT_MAX_OFFSET = 50;

function nodeDims(state, stateHeights) {
  const x = state.layout?.x ?? 0;
  const y = state.layout?.y ?? 0;
  const h = stateHeights.get(state.name) ?? 300;
  return { x, y, h };
}

function centerOf(state, stateHeights, nodeWidth) {
  const { x, y, h } = nodeDims(state, stateHeights);
  return { x: x + nodeWidth / 2, y: y + h / 2 };
}

function getPorts(state, stateHeights, nodeWidth) {
  const { x, y, h } = nodeDims(state, stateHeights);
  return {
    L: { x, y: y + h / 2 },
    R: { x: x + nodeWidth, y: y + h / 2 },
    T: { x: x + nodeWidth / 2, y },
    B: { x: x + nodeWidth / 2, y: y + h },
  };
}

function oppositePort(p) {
  if (p === "L") return "R";
  if (p === "R") return "L";
  if (p === "T") return "B";
  return "T";
}

// simple relative-position port choice
function chooseFromPort(fromState, toState, stateHeights, nodeWidth) {
  const fc = centerOf(fromState, stateHeights, nodeWidth);
  const tc = centerOf(toState, stateHeights, nodeWidth);
  const dx = tc.x - fc.x;
  const dy = tc.y - fc.y;

  if (Math.abs(dx) >= Math.abs(dy)) return dx >= 0 ? "R" : "L";
  return dy >= 0 ? "B" : "T";
}

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function offsetForIndex(idx, total) {
  const mid = (total - 1) / 2;
  return clamp((idx - mid) * PORT_SPACING, -PORT_MAX_OFFSET, PORT_MAX_OFFSET);
}

function applyPortOffset(pt, port, offset) {
  // L/R -> shift y ; T/B -> shift x
  if (port === "L" || port === "R") return { x: pt.x, y: pt.y + offset };
  return { x: pt.x + offset, y: pt.y };
}

function controlPoints(p1, p2, fromPort, toPort) {
  const dx = p2.x - p1.x;
  const dy = p2.y - p1.y;

  const hx = Math.max(60, Math.min(260, Math.abs(dx) * 0.5));
  const hy = Math.max(60, Math.min(260, Math.abs(dy) * 0.5));

  const c1 = { ...p1 };
  const c2 = { ...p2 };

  if (fromPort === "R") c1.x += hx;
  if (fromPort === "L") c1.x -= hx;
  if (fromPort === "B") c1.y += hy;
  if (fromPort === "T") c1.y -= hy;

  if (toPort === "L") c2.x -= hx;
  if (toPort === "R") c2.x += hx;
  if (toPort === "T") c2.y -= hy;
  if (toPort === "B") c2.y += hy;

  return { c1, c2 };
}

function renderSelfLoop(e, stateByName) {
  const state = stateByName.get(e.from);
  if (!state) return null;

  const x = state.layout.x;
  const y = state.layout.y;

  const r = 12;
  const padX = 18;
  const padY = 8;

  const cx = x + padX + r;
  const cy = y - padY - r;

  // chevron position
  const thetaDeg = 320;
  const theta = (thetaDeg * Math.PI) / 180;

  const tipX = cx + r * Math.cos(theta);
  const tipY = cy + r * Math.sin(theta);

  // unit tangent at theta (clockwise) is (sin, -cos)
  const tx = Math.sin(theta);
  const ty = -Math.cos(theta);

  const tLen = Math.hypot(tx, ty) || 1;
  const ux = tx / tLen;
  const uy = ty / tLen;

  const rot = (vx, vy, deg) => {
    const a = (deg * Math.PI) / 180;
    const ca = Math.cos(a);
    const sa = Math.sin(a);
    return { x: vx * ca - vy * sa, y: vx * sa + vy * ca };
  };

  // chevron arms ±60° from tangent
  const L = 5;
  const d1 = rot(ux, uy, +60);
  const d2 = rot(ux, uy, -60);

  const xA = tipX - d1.x * L;
  const yA = tipY - d1.y * L;
  const xB = tipX - d2.x * L;
  const yB = tipY - d2.y * L;

  return (
    <g key={e.key}>
      <circle cx={cx} cy={cy} r={r} stroke="#000" strokeWidth="2" fill="none" />
      <line x1={tipX} y1={tipY} x2={xA} y2={yA} stroke="#000" strokeWidth="2" strokeLinecap="round" />
      <line x1={tipX} y1={tipY} x2={xB} y2={yB} stroke="#000" strokeWidth="2" strokeLinecap="round" />
    </g>
  );
}

export default function DiagramEdges({
  edges,
  stateByName,
  stateHeights,
  canvas,
  nodeWidth,
}) {
  if (!edges?.length) return null;

  const routing = useMemo(() => {
    const info = new Map();
    const groups = new Map(); // from|port → edges[]

    for (const e of edges) {
      if (e.isLoop) continue;

      const from = stateByName.get(e.from);
      const to = stateByName.get(e.to);
      if (!from || !to) continue;

      const fromPort = chooseFromPort(from, to, stateHeights, nodeWidth);
      const toPort = oppositePort(fromPort);

      const key = `${e.from}|${fromPort}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(e);

      info.set(e.key, { fromPort, toPort, offset: 0 });
    }

    // Order edges out of the same port by DESTINATION coordinate:
    // - L/R ports => sort by destination Y
    // - T/B ports => sort by destination X
    for (const list of groups.values()) {
      list.sort((a, b) => {
        const ta = stateByName.get(a.to);
        const tb = stateByName.get(b.to);
        if (!ta || !tb) return a.key.localeCompare(b.key);

        const ca = centerOf(ta, stateHeights, nodeWidth);
        const cb = centerOf(tb, stateHeights, nodeWidth);

        const { fromPort } = info.get(a.key) || { fromPort: "R" };

        if (fromPort === "L" || fromPort === "R") return ca.y - cb.y;
        return ca.x - cb.x;
      });

      const total = list.length;
      list.forEach((e, i) => {
        const base = info.get(e.key);
        if (!base) return;
        info.set(e.key, { ...base, offset: offsetForIndex(i, total) });
      });
    }

    return info;
  }, [edges, stateByName, stateHeights, nodeWidth]);

  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      width={canvas.width}
      height={canvas.height}
    >
      <defs>
        <marker
          id="arrow-black"
          markerWidth="10"
          markerHeight="10"
          refX="9"
          refY="5"
          orient="auto"
          markerUnits="strokeWidth"
        >
          <path d="M 0 0 L 10 5 L 0 10 z" fill="#000" />
        </marker>
      </defs>

      {edges.map((e) => {
        // ✅ restore remain arrows (self loops)
        if (e.isLoop) return renderSelfLoop(e, stateByName);

        const from = stateByName.get(e.from);
        const to = stateByName.get(e.to);
        const r = routing.get(e.key);
        if (!from || !to || !r) return null;

        const portsA = getPorts(from, stateHeights, nodeWidth);
        const portsB = getPorts(to, stateHeights, nodeWidth);

        // single offset applied to both endpoints
        const p1 = applyPortOffset(portsA[r.fromPort], r.fromPort, r.offset);
        const p2 = applyPortOffset(portsB[r.toPort], r.toPort, r.offset);

        const { c1, c2 } = controlPoints(p1, p2, r.fromPort, r.toPort);

        return (
          <path
            key={e.key}
            d={`M ${p1.x} ${p1.y} C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${p2.x} ${p2.y}`}
            stroke="#000"
            strokeWidth="2"
            fill="none"
            markerEnd="url(#arrow-black)"
          />
        );
      })}
    </svg>
  );
}


