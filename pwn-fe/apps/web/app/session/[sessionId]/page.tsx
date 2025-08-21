"use client"
import dynamic from "next/dynamic"
const Terminal = dynamic(() => import("../../../components/terminal/Terminal"), { ssr: false })

export default function Page({ params }: { params: { sessionId: string } }) {
  return (
    <main className="p-2 h-screen">
      <Terminal sessionId={params.sessionId} />
    </main>
  )
}