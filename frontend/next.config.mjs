/** @type {import('next').NextConfig} */
const nextConfig = {
  // Rewrite /api/* calls to the FastAPI backend in local development.
  // In production on Vercel, this is handled by vercel.json routing.
  async rewrites() {
    // Only proxy to local backend if running in development mode.
    // In production, we use relative paths handled by vercel.json.
    if (process.env.NODE_ENV === 'development') {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
