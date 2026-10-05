import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/masthead.jpg", destination: "/masthead" },
      // Kan check: /og.png must 200; Next serves app/opengraph-image as /opengraph-image
      { source: "/og.png", destination: "/opengraph-image" },
    ];
  },
};

export default nextConfig;
