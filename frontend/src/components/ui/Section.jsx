export default function Section({ title, description, right, children, className = "" }) {
  return (
    <section className={`space-y-4 ${className}`}>
      {(title || description || right) && (
        <div className="flex items-end justify-between gap-4">
          <div className="space-y-1">
            {title && <h2 className="text-2xl font-semibold text-slate-900">{title}</h2>}
            {description && <p className="text-slate-600">{description}</p>}
          </div>
          {right && <div>{right}</div>}
        </div>
      )}
      {children}
    </section>
  );
}
