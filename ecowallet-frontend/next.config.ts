import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  allowedDevOrigins: [
    "10.0.0.14",
    "10.0.0.14:3000",
    "localhost",
    "localhost:3000",
  ],
};

export default nextConfig;
