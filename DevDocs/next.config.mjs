let userConfig = undefined
try {
  userConfig = await import('./v0-user-next.config')
} catch (e) {
  // ignore error
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Removed standalone output mode as we're using a simpler Docker approach
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    webpackBuildWorker: true,
    parallelServerBuildTraces: true,
    parallelServerCompiles: true,
  },
  env: {
    // Keep existing env vars, but API calls will now be proxied
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:5000', // Updated default to 5000
    MCP_HOST: process.env.MCP_HOST || 'localhost',
    NEXT_PUBLIC_BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:5000', // Updated default to 5000
  },
  // Add rewrites for proxying API requests in development
  async rewrites() {
    return [
      {
        source: '/api/:path*', // Match all routes starting with /api/
        destination: 'http://localhost:5000/api/:path*', // Proxy to backend on port 5000
      },
    ]
  }
}

export default nextConfig