"use client"
import { useEffect, useRef } from "react"
import { wsUrl, wsPath } from "../../lib/config"

export default function Terminal({ sessionId }: { sessionId: string }) {
  const ref = useRef<HTMLTextAreaElement>(null)
  useEffect(() => {
    const url = `${wsUrl()}${wsPath()}/session/${sessionId}`
    const ws = new WebSocket(url)
    const el = ref.current
    if (!el) return
    ws.onmessage = (ev) => { el.value += typeof ev.data === "string" ? ev.data : "" }
    const onKey = (e: KeyboardEvent) => {
      if (!ws || ws.readyState !== WebSocket.OPEN) return
      if (e.key.length === 1) ws.send(e.key)
      else if (e.key === "Enter") ws.send("\n")
      else if (e.key === "Backspace") ws.send("\x7f")
    }
    window.addEventListener("keydown", onKey)
    return () => { window.removeEventListener("keydown", onKey); ws.close() }
  }, [sessionId])
  return <textarea ref={ref} className="w-full h-full border p-2 font-mono text-sm" />
}