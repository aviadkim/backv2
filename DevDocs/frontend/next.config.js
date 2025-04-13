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
  reactStrictMode: false, // Disable strict mode to avoid double-rendering
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
    NEXT_PUBLIC_SUPABASE_URL: 'https://dnjnsotemnfrjlotgved.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTI4NTI0MDAsImV4cCI6MjAyODQyODQwMH0.placeholder-key',
  },
  // Add path aliases
  webpack(config) {
    config.resolve.alias['@'] = path.join(__dirname, './');
    return config;
  },
};

module.exports = nextConfig;
