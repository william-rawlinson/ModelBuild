// src/components/model_view/EventTile.jsx

const IMPACT_STYLES = {
  cost: {
    border: "border-red-600",
    hover: "hover:border-red-700",
  },
  utility: {
    border: "border-green-600",
    hover: "hover:border-green-700",
  },
  both: {
    border: "border-orange-500",
    hover: "hover:border-orange-600",
  },
  other: {
    border: "border-slate-200",
    hover: "hover:border-slate-300",
  },
};

export default function EventTile({ event, onClick }) {
  const impact = event?.metadata?.impact_type ?? "other";
  const style = IMPACT_STYLES[impact] ?? IMPACT_STYLES.other;

  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "w-full text-left rounded-xl border px-3 py-2",
        "bg-white transition-colors",
        style.border,
        style.hover,
      ].join(" ")}
    >
      <div className="text-sm font-semibold text-slate-900 truncate">
        {event.event_name}
      </div>
    </button>
  );
}


