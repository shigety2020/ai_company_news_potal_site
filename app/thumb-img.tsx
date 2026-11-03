"use client";

import { useEffect, useRef } from "react";

/** TOC thumbnail: if it fails to load, swap to the fallback once (no loop). */
export default function ThumbImg({ src, fallback }: { src: string; fallback: string }) {
  const ref = useRef<HTMLImageElement>(null);
  const swap = () => {
    const img = ref.current;
    if (!img || img.dataset.fallback === "1" || src === fallback) return;
    img.dataset.fallback = "1";
    img.src = fallback;
  };
  // Error may fire before hydration; check once on mount.
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete && img.naturalWidth === 0) swap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  // eslint-disable-next-line @next/next/no-img-element
  return <img ref={ref} src={src} alt="" onError={swap} />;
}
