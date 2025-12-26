// src/components/model_view/StateNode.jsx
import EventTile from "./EventTile";

export default function StateNode({
  state,
  eventsByName,
  eventNames,
  onSelectEvent,
  onSelectState,      // ✅ NEW
  isSelected = false, // ✅ NEW (optional)
  colors,
  width = 280,
}) {
  const headerStyle = colors?.headerStyle ?? {
    backgroundColor: "#f8fafc",
    borderColor: "#e2e8f0",
  };

  const ringClass = isSelected ? "ring-2 ring-slate-400" : "";

  return (
    <div style={{ width }}>
      <div
        className={`rounded-2xl border bg-white shadow-sm overflow-hidden ${ringClass}`}
        onMouseDown={(e) => {
          // Selecting the state should not bubble to the canvas (which clears selection)
          e.stopPropagation();
          onSelectState?.(state.name);
        }}
      >
        {/* Header */}
        <div
          className="px-4 py-3 border-b rounded-t-2xl cursor-pointer"
          style={headerStyle}
        >
          <div
            className="
              text-xl font-bold text-slate-900
              break-words whitespace-normal leading-snug
            "
          >
            {state.label}
          </div>
        </div>

        {/* Event tiles */}
        <div className="p-4 space-y-2">
          {eventNames.length === 0 ? (
            <div className="text-sm text-slate-500">No events.</div>
          ) : (
            eventNames.map((name, i) => {
              const ev = eventsByName.get(name);
              if (!ev) return null;

              const domId = `event-tile-${state.name}-${i === 0 ? "anchor" : name}`;

              return (
                <div
                  key={name}
                  id={domId}
                  onMouseDown={(e) => {
                    // Prevent state-selection handler above from firing when clicking tiles
                    e.stopPropagation();
                  }}
                >
                  <EventTile event={ev} onClick={() => onSelectEvent?.(ev)} />
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}



