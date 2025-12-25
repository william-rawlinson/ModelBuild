import React from "react";
import SegmentedControl from "./SegmentedControl";
import MultiSelectPills from "./MultiSelectPills";

export default function ResultsFiltersBar({ settings, options, onSettingsChange }) {
  const update = (patch) => onSettingsChange({ ...settings, ...patch });

  return (
    <div className="flex flex-col gap-3">
      {/* Top controls */}
      <div className="flex flex-wrap items-center gap-3">
        <SegmentedControl
          value={settings.discounting}
          onChange={(v) => update({ discounting: v })}
          options={[
            { label: "Discounted", value: "discounted" },
            { label: "Undiscounted", value: "undiscounted" },
          ]}
        />

        <SegmentedControl
          value={settings.measure}
          onChange={(v) => update({ measure: v })}
          options={[
            { label: "Costs + QALYs", value: "cost_qaly" },
            { label: "Costs", value: "cost" },
            { label: "QALYs", value: "qaly" },
            { label: "Time spent", value: "time_spent" },
          ]}
        />

        <SegmentedControl
          value={settings.breakdown}
          onChange={(v) => update({ breakdown: v })}
          options={[
            { label: "By state", value: "by_state" },
            { label: "By event", value: "by_event" },
            { label: "State × event", value: "by_state_event" },
          ]}
        />

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={settings.showDeltas}
            onChange={(e) => update({ showDeltas: e.target.checked })}
          />
          Show deltas vs intervention
        </label>
      </div>

      {/* Comparators */}
      <div className="flex flex-col gap-2">
        <div className="text-sm text-gray-600">Comparators:</div>
        <MultiSelectPills
          options={options.comparators}
          selected={settings.comparators}
          onToggle={(t) => {
            const set = new Set(settings.comparators || []);
            set.has(t) ? set.delete(t) : set.add(t);
            update({ comparators: Array.from(set) });
          }}
        />
      </div>
    </div>
  );
}

