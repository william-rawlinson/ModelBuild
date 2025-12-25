export default function Card({ children, className = "" }) {
  return (
    <div className={`rounded-2xl border bg-white p-8 shadow-sm ${className}`}>
      {children}
    </div>
  );
}
