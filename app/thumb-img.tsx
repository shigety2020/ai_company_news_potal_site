"use client";

import { useEffect, useRef } from "react";

/**
 * External (https) thumbnails go through Vercel / Next image optimization at
 * about display size (48px SP, 64px PC; 1x–2x), instead of the full original
 * (e.g. a 1.85 MB PNG in a 48px box). Widths must be in images.imageSizes.
 */
const OPT_WIDTHS = [64, 96, 128] as const;
const OPT_SIZES = "(min-width: 1024px) 64px, 48px";

function optimized(src: string, w: number): string {
  return `/_next/image?url=${encodeURIComponent(src)}&w=${w}&q=75`;
}

/**
 * TOC thumbnail. If loading fails, step down once each (no loop):
 * resized → original URL (optimizer may not reach some hosts) → local fallback.
 */
export default function ThumbImg({ src, fallback }: { src: string; fallback: string }) {
  const ref = useRef<HTMLImageElement>(null);
  const canOptimize = src.startsWith("https://");
  const swap = () => {
    const img = ref.current;
    if (!img) return;
    if (canOptimize && !img.dataset.step) {
      img.dataset.step = "orig";
      img.removeAttribute("srcset");
      img.removeAttribute("sizes");
      img.src = src;
      return;
    }
    if (img.dataset.fallback === "1" || src === fallback) return;
    img.dataset.fallback = "1";
    img.removeAttribute("srcset");
    img.removeAttribute("sizes");
    img.src = fallback;
  };
  // Error may fire before hydration; check once on mount.
  useEffect(() => {
    const img = ref.current;
    if (img && img.complete && img.naturalWidth === 0) swap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  if (canOptimize) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        ref={ref}
        src={optimized(src, 96)}
        srcSet={OPT_WIDTHS.map((w) => `${optimized(src, w)} ${w}w`).join(", ")}
        sizes={OPT_SIZES}
        alt=""
        loading="lazy"
        decoding="async"
        onError={swap}
      />
    );
  }
  // eslint-disable-next-line @next/next/no-img-element
  return <img ref={ref} src={src} alt="" loading="lazy" decoding="async" onError={swap} />;
}
