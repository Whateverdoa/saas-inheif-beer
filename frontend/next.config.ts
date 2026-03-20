import type { NextConfig } from "next";

/** Must match `getPublicApiBase` fallback when `NEXT_PUBLIC_API_URL` is unset on Vercel. */
const VERCEL_API = "https://saas-inheif-beer.vercel.app";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },
  /**
   * Do NOT set `env.NEXT_PUBLIC_API_URL` with a localhost fallback — that value is inlined into
   * the browser bundle and breaks production (fetches go to the user’s localhost).
   */
  async rewrites() {
    const fromEnv = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");
    const apiUrl =
      fromEnv && !fromEnv.includes("localhost") && !fromEnv.includes("127.0.0.1")
        ? fromEnv
        : process.env.VERCEL === "1"
          ? VERCEL_API
          : "http://127.0.0.1:8000";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
