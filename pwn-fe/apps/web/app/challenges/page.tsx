'use client'
import { useEffect, useState } from 'react'
import { api } from '../../lib/api'

export default function Page() {
  const [items, setItems] = useState<any[]>([])
  useEffect(() => { api.get('/challenges').then(setItems).catch(() => setItems([])) }, [])
  return (
    <main className="p-8">
      <h2 className="text-xl font-semibold">Challenges</h2>
      <ul className="mt-4 list-disc pl-6">
        {items.map((c) => (
          <li key={c.id}>
            <a href={`/challenges/${c.slug}`} className="underline">{c.title}</a>
          </li>
        ))}
      </ul>
    </main>
  )
}