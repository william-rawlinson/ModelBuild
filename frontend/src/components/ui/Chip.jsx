export default function Chip({ children, onRemove }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full border bg-slate-50 px-4 py-2 text-lg">
      <span className="text-slate-900">{children}</span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="rounded-full px-2 py-1 text-slate-600 hover:bg-slate-200"
          aria-label="Remove"
        >
          ✕
        </button>
      )}
    </span>
  );
}
