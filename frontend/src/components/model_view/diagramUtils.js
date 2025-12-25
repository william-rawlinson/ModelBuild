export function indexById(items) {
  const m = new Map();
  for (const it of items) m.set(it.id, it);
  return m;
}

export function clamp(n, min, max) {
  return Math.max(min, Math.min(max, n));
}
