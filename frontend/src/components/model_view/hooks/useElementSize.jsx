import { useLayoutEffect, useState } from "react";

export function useElementSize(ref) {
  const [size, setSize] = useState({ width: 0, height: 0 });

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;

    const ro = new ResizeObserver((entries) => {
      const rect = entries?.[0]?.contentRect;
      if (!rect) return;
      setSize({ width: rect.width, height: rect.height });
    });

    ro.observe(el);
    return () => ro.disconnect();
  }, [ref]);

  return size;
}
