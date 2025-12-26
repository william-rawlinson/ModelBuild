// src/components/model_view/stateColors.js
const PALETTE = [
  { name: "emerald",  hex: "#34d399", bg: "#ecfdf5", border: "#a7f3d0" },
  { name: "amber",    hex: "#fbbf24", bg: "#fffbeb", border: "#fde68a" },
  { name: "rose",     hex: "#fb7185", bg: "#fff1f2", border: "#fecdd3" },
  { name: "sky",      hex: "#38bdf8", bg: "#f0f9ff", border: "#bae6fd" },
  { name: "violet",   hex: "#a78bfa", bg: "#f5f3ff", border: "#ddd6fe" },
  { name: "teal",     hex: "#2dd4bf", bg: "#f0fdfa", border: "#99f6e4" },
  { name: "fuchsia",  hex: "#e879f9", bg: "#fdf4ff", border: "#f5d0fe" },
  { name: "lime",     hex: "#a3e635", bg: "#f7fee7", border: "#d9f99d" },

  { name: "indigo",   hex: "#6366f1", bg: "#eef2ff", border: "#c7d2fe" },
  { name: "orange",   hex: "#fb923c", bg: "#fff7ed", border: "#fed7aa" },
  { name: "cyan",     hex: "#22d3ee", bg: "#ecfeff", border: "#a5f3fc" },
  { name: "pink",     hex: "#f472b6", bg: "#fdf2f8", border: "#fbcfe8" },
  { name: "green",    hex: "#4ade80", bg: "#f0fdf4", border: "#bbf7d0" },
  { name: "purple",   hex: "#c084fc", bg: "#faf5ff", border: "#e9d5ff" },
  { name: "yellow",   hex: "#fde047", bg: "#fefce8", border: "#fef08a" },

  { name: "blue",     hex: "#60a5fa", bg: "#eff6ff", border: "#bfdbfe" },
  { name: "red",      hex: "#f87171", bg: "#fef2f2", border: "#fecaca" },
  { name: "mint",     hex: "#5eead4", bg: "#f0fdfa", border: "#99f6e4" },
  { name: "grape",    hex: "#8b5cf6", bg: "#f5f3ff", border: "#ddd6fe" },
  { name: "gold",     hex: "#facc15", bg: "#fefce8", border: "#fef08a" },
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
