import React from "react";

export default function MultiSelectPills({ options, selected, onToggle }) {
  const sel = new Set(selected || []);
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((opt) => {
        const active = sel.has(opt);
        return (
          <button
            key={opt}
            type="button"
            onClick={() => onToggle(opt)}
            className={[
              "px-3 py-1.5 rounded-full text-sm border",
              active ? "bg-blue-600 text-white border-blue-600" : "bg-white text-gray-800 border-gray-300 hover:bg-gray-50",
            ].join(" ")}
          >
            {opt}
          </button>
        );
      })}
    </div>
  );
}
