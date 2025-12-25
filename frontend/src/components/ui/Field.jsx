export function Field({ label, hint, children, className = "" }) {
  return (
    <div className={`space-y-2 ${className}`}>
      {label && <label className="text-lg font-semibold text-slate-900">{label}</label>}
      {children}
      {hint && <p className="text-sm text-slate-600">{hint}</p>}
    </div>
  );
}

export function FieldRow({ children, className = "" }) {
  return <div className={`flex gap-3 ${className}`}>{children}</div>;
}

export function TextInput(props) {
  const { className = "", ...rest } = props;
  return (
    <input
      {...rest}
      className={`w-full rounded-xl border bg-white px-4 py-3 text-lg outline-none focus:ring-2 ${className}`}
    />
  );
}

export function Select(props) {
  const { className = "", children, ...rest } = props;
  return (
    <select
      {...rest}
      className={`rounded-xl border bg-white px-4 py-3 text-lg outline-none focus:ring-2 ${className}`}
    >
      {children}
    </select>
  );
}
