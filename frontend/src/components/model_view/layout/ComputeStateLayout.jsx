// src/components/model_view/layout/computeStateLayout.js
export function computeStateLayout({ stateDiagram, stateHeights, viewportWidth, nodeWidth }) {
  const layoutByState = new Map();

  const rows = stateDiagram ?? [];
  const safeViewportW = Math.max(0, viewportWidth ?? 0);

  const marginY = 48;
  const minRowGap = 50;

  const minColGap = 200;   // ⬅ wider minimum horizontal spacing
  const maxColGap = 200; // optional: allow more breathing room
  const sidePadMin = 32;

  const rowCols = rows.map((r) => (r ?? []).filter(Boolean).length);
  const maxCols = Math.max(1, ...rowCols);

  // bounded gap
  let colGap = minColGap;
  if (maxCols > 1 && safeViewportW > 0) {
    const usableW = safeViewportW - sidePadMin * 2;
    const ideal = (usableW - maxCols * nodeWidth) / (maxCols - 1);
    colGap = Math.max(minColGap, Math.min(maxColGap, ideal));
  }

  const contentW = maxCols * nodeWidth + (maxCols - 1) * colGap;

  // center if fits, else pin left (scroll)
  const startX =
    safeViewportW > 0 ? Math.max(sidePadMin, (safeViewportW - contentW) / 2) : sidePadMin;

  // row heights
  const rowHeights = rows.map((r) => {
    const names = (r ?? []).filter(Boolean);
    let maxH = 0;
    for (const name of names) maxH = Math.max(maxH, stateHeights?.get(name) ?? 300);
    return maxH || 300;
  });

  let y = marginY;

  for (let rowIdx = 0; rowIdx < rows.length; rowIdx++) {
    const names = (rows[rowIdx] ?? []).filter(Boolean);

    for (let colIdx = 0; colIdx < names.length; colIdx++) {
      const name = names[colIdx];
      layoutByState.set(name, {
        x: startX + colIdx * (nodeWidth + colGap),
        y,
      });
    }

    y += rowHeights[rowIdx] + minRowGap;
  }

  return layoutByState;
}



