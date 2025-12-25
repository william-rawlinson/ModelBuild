// src/components/model_view/stateColors.js
const PALETTE = [
  { name: "emerald", hex: "#34d399", bg: "#ecfdf5", border: "#a7f3d0" },
  { name: "amber",   hex: "#fbbf24", bg: "#fffbeb", border: "#fde68a" },
  { name: "rose",    hex: "#fb7185", bg: "#fff1f2", border: "#fecdd3" },
  { name: "sky",     hex: "#38bdf8", bg: "#f0f9ff", border: "#bae6fd" },
  { name: "violet",  hex: "#a78bfa", bg: "#f5f3ff", border: "#ddd6fe" },
  { name: "teal",    hex: "#2dd4bf", bg: "#f0fdfa", border: "#99f6e4" },
  { name: "fuchsia", hex: "#e879f9", bg: "#fdf4ff", border: "#f5d0fe" },
  { name: "lime",    hex: "#a3e635", bg: "#f7fee7", border: "#d9f99d" },
];

export function generateStateColorMap(states) {
  const map = new Map();

  states.forEach((state, index) => {
    const c = PALETTE[index % PALETTE.length];

    map.set(state.id, {
      arrowHex: c.hex,
      headerStyle: {
        backgroundColor: c.bg,
        borderColor: c.border,
        color: c.hex,
      },
    });
  });

  return map;
}
