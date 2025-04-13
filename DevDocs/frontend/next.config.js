/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  // Use static export for Cloud Run
  output: 'export',
  // Include all pages in the export
  exportPathMap: async function (defaultPathMap, { dev, dir, outDir, distDir, buildId }) {
    return {
      '/': { page: '/' },
      '/dashboard': { page: '/dashboard' },
      '/mcp-demo': { page: '/mcp-demo' },
      '/portfolio': { page: '/portfolio' },
    };
  },
  reactStrictMode: true,
  // Enable CORS for API requests
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: 'http://localhost:24125',
  },
  // Add path aliases
  webpack(config) {
    config.resolve.alias['@'] = path.join(__dirname, './');
    return config;
  },
};

module.exports = nextConfig;
