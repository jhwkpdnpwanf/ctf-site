let token: string | null = null
export function setToken(t: string) { token = t; localStorage.setItem("token", t) }
function getToken() { return token || localStorage.getItem("token") || "" }

const base = process.env.NEXT_PUBLIC_API_BASE || "/api"

async function req(method: string, path: string, body?: any) {
  const r = await fetch(base + path, {
    method,
    headers: { "Content-Type": "application/json", ...(getToken() ? { Authorization: "Bearer " + getToken() } : {}) },
    body: body ? JSON.stringify(body) : undefined,
    credentials: "include"
  })
  if (!r.ok) throw new Error(await r.text())
  return await r.json()
}
export const api = { get: (p: string) => req("GET", p), post: (p: string, b?: any) => req("POST", p, b) }