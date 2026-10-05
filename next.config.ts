import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      { source: "/masthead.jpg", destination: "/masthead" },
      { source: "/og.png", destination: "/api/og" },
    ];
  },
};

export default nextConfig;
