"use client"
import { useEffect, useState } from "react"
import { api } from "../../../lib/api"

export default function Page({ params }: { params: { slug: string } }) {
  const [challenge, setChallenge] = useState<any>(null)
  const [session, setSession] = useState<any>(null)

  useEffect(() => {
    api.get("/challenges").then((list) => {
      const c = list.find((x: any) => x.slug === params.slug)
      setChallenge(c || null)
    })
  }, [params.slug])

  const start = async () => {
    if (!challenge) return
    const s = await api.post("/sessions", { challenge_id: challenge.id })
    setSession(s)
    if (s.ws_url) window.location.href = `/session/${s.id}`
  }

  return (
    <main className="p-8">
      <h2 className="text-xl font-semibold">{challenge ? challenge.title : "濡쒕뵫 以?}</h2>
      <button onClick={start} className="mt-4 rounded px-3 py-2 border">Start Session</button>
      {session && <pre className="mt-4">{JSON.stringify(session, null, 2)}</pre>}
    </main>
  )
}