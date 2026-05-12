import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'

type HealthResponse = {
  status: string
  service: string
}

export function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    apiClient
      .get<HealthResponse>('/api/health/')
      .then((res) => {
        if (!cancelled) setHealth(res.data)
      })
      .catch(() => {
        if (!cancelled) setError('API unreachable (start the Django backend on port 8000)')
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 px-6 py-16">
      <header className="space-y-2">
        <p className="text-sm font-medium text-slate-500">Smart Queue Management</p>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
          Dashboard
        </h1>
        <p className="text-slate-600">
          React + Vite + Tailwind + React Router + Axios. Use the navigation to explore routes.
        </p>
      </header>

      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-medium text-slate-900">API health</h2>
        <p className="mt-2 text-sm text-slate-600">
          Proxied via Vite in dev (<code className="rounded bg-slate-100 px-1">/api</code> →{' '}
          <code className="rounded bg-slate-100 px-1">localhost:8000</code>).
        </p>
        <dl className="mt-4 grid gap-2 text-sm">
          <div className="flex gap-2">
            <dt className="text-slate-500">Status</dt>
            <dd className="font-mono text-slate-900">
              {health?.status ?? (error ? 'offline' : '…')}
            </dd>
          </div>
          <div className="flex gap-2">
            <dt className="text-slate-500">Service</dt>
            <dd className="font-mono text-slate-900">{health?.service ?? '—'}</dd>
          </div>
        </dl>
        {error ? (
          <p className="mt-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">{error}</p>
        ) : null}
      </section>

      <p className="text-sm text-slate-500">
        <Link className="font-medium text-indigo-600 hover:text-indigo-500" to="/about">
          About this scaffold
        </Link>
      </p>
    </div>
  )
}
