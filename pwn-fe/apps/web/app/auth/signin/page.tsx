"use client"
import { useState } from "react"
import { api, setToken } from "../../../lib/api"

export default function Page() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const submit = async () => {
    const r = await api.post("/auth/signin", { email, password })
    setToken(r.access_token)
    window.location.href = "/"
  }
  return (
    <main className="p-8">
      <h2 className="text-xl font-semibold">Sign in</h2>
      <div className="mt-4 space-y-2">
        <input className="border px-2 py-1" placeholder="email" value={email} onChange={(e)=>setEmail(e.target.value)} />
        <input className="border px-2 py-1" type="password" placeholder="password" value={password} onChange={(e)=>setPassword(e.target.value)} />
        <button onClick={submit} className="px-3 py-1 border rounded">Submit</button>
      </div>
    </main>
  )
}