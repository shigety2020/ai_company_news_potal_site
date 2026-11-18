import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // e: TOC thumbnails come from many hosts (X, PR TIMES, YouTube, company sites),
  // so allow any https host and resize to ~display size. Failures fall back in
  // app/thumb-img.tsx (original URL, then /thumb-fallback).
  images: {
    remotePatterns: [{ protocol: "https", hostname: "**" }],
    // Thumbnails of a past issue do not change; keep resized copies longer
    // (fewer re-transformations on Vercel). Upstream may send no-store.
    minimumCacheTTL: 2678400,
  },
  async rewrites() {
    return [
      { source: "/masthead.jpg", destination: "/masthead" },
      { source: "/og.png", destination: "/api/og" },
    ];
  },
};

export default nextConfig;
