export default function EventTile({ event, onClick }) {

  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "w-full text-left rounded-xl border px-3 py-2",
        "bg-white hover:bg-slate-50 transition-colors",
      ].join(" ")}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm font-semibold text-slate-900 truncate">
          {event.label}
        </div>
      </div>

      <div className="mt-1 text-xs text-slate-500">
        {event.qc_status === "needs_qc" ? "Needs QC" : "QC OK"} ·{" "}
        {event.spec_used ? "Spec used" : "No spec"}
      </div>
    </button>
  );
}
