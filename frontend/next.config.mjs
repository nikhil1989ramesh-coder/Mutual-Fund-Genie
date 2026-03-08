/** @type {import('next').NextConfig} */
const nextConfig = {
  // In development: only proxy /api/* to FastAPI when NEXT_PUBLIC_API_URL is set.
  // When unset, requests hit the Next.js Pages API (stub) so local app works without running the backend.
  async rewrites() {
    if (process.env.NODE_ENV === 'development') {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (apiUrl && apiUrl.trim() !== '') {
        return [
          {
            source: '/api/:path*',
            destination: `${apiUrl.trim().replace(/\/$/, '')}/api/:path*`,
          },
        ];
      }
    }
    return [];
  },
};

export default nextConfig;
