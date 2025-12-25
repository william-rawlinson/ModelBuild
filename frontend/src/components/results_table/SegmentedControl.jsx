import React from "react";

export default function SegmentedControl({ options, value, onChange }) {
  return (
    <div className="inline-flex rounded-xl border border-gray-200 overflow-hidden">
      {options.map((opt) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={[
              "px-3 py-2 text-sm",
              active ? "bg-gray-900 text-white" : "bg-white text-gray-800 hover:bg-gray-50",
            ].join(" ")}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}
