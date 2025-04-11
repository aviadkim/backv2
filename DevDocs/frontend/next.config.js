/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  // Disable static site generation for pages that require authentication
  exportPathMap: async function (defaultPathMap, { dev, dir, outDir, distDir, buildId }) {
    return {
      '/': { page: '/' },
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
