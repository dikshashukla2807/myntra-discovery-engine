import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {
    "/api/**/*": ["./dataset/**/*"],
  },
  // Hosted deploys have no FastAPI process. Dashboard APIs are Next.js routes.
  async rewrites() {
    const backend = process.env.API_PROXY_TARGET;
    if (!backend) return [];
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
