export function estimateNodeHeight(eventCount) {
  const header = 66;
  const padding = 32;
  const tile = 54;
  const gap = 8;
  const empty = 24;

  if (eventCount === 0) return header + padding + empty;
  return header + padding + eventCount * tile + (eventCount - 1) * gap;
}
