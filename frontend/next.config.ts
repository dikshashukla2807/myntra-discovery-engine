import type { NextConfig } from "next";
import path from "node:path";

const projectDir = process.cwd();
const repoRoot = path.basename(projectDir) === "frontend" ? path.join(projectDir, "..") : projectDir;

const nextConfig: NextConfig = {
  outputFileTracingRoot: repoRoot,
  outputFileTracingIncludes: {
    "/api/**/*": ["./dataset/**/*"],
  },
  // Local Python proxy is opt-in. Hosted deploys have no FastAPI process;
  // dashboard APIs are Next.js route handlers that read the processed dataset.
  async rewrites() {
    const backend = process.env.API_PROXY_TARGET;
    if (!backend) return [];
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;
