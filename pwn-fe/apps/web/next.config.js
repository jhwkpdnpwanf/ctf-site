/** @type {import("next").NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const target = process.env.API_PROXY_TARGET
    const prefix = process.env.API_PROXY_PREFIX || "/api"
    if (!target) return []
    return [{ source: `${prefix}/:path*`, destination: `${target}/:path*` }]
  }
}
module.exports = nextConfig