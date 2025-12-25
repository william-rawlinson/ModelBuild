// src/components/model_view/StateNode.jsx
import EventTile from "./EventTile";

export default function StateNode({
  state,
  events,
  eventIds,
  onSelectEvent,
  colors,
  width = 280,
}) {
  const headerStyle = colors?.headerStyle ?? {
      backgroundColor: "#f8fafc",
      borderColor: "#e2e8f0",
      color: "#0f172a",
    };


  return (
    <div
      className="absolute"
      style={{ left: state.layout.x, top: state.layout.y, width }}
    >
      <div className="rounded-2xl border bg-white shadow-sm">
        <div className="px-4 py-3 border-b" style={headerStyle}>
          <div className="text-xl font-bold">{state.label}</div>
          <div className="text-sm opacity-80">
            {eventIds.length} event{eventIds.length === 1 ? "" : "s"}
          </div>
        </div>

        <div className="p-4 space-y-2">
          {eventIds.length === 0 ? (
            <div className="text-sm text-slate-500">No events.</div>
          ) : (
            eventIds.map((id) => {
              const ev = events.get(id);
              if (!ev) return null;
              return (
                <EventTile
                  key={id}
                  event={ev}
                  onClick={() => onSelectEvent(ev)}
                />
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

