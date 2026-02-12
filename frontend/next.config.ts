import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Enable standalone output for Docker deployment
  // This creates a minimal production bundle with all dependencies
  output: 'standalone',
};

export default nextConfig;
