export function wsUrl() {
  const host = process.env.NEXT_PUBLIC_WS_HOST
  const port = process.env.NEXT_PUBLIC_WS_PORT
  if (!host || !port) throw new Error("NEXT_PUBLIC_WS_HOST / NEXT_PUBLIC_WS_PORT must be set")
  const scheme = port === "443" ? "wss" : "ws"
  const usePort = !(port === "443" || port === "80")
  return `${scheme}://${host}${usePort ? `:${port}` : ""}`
}

export function wsPath() {
  const p = process.env.NEXT_PUBLIC_WS_PATH
  if (!p) throw new Error("NEXT_PUBLIC_WS_PATH must be set")
  return p.endsWith("/") ? p.slice(0, -1) : p
}