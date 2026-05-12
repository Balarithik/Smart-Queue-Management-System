import { useState } from 'react'
import { Link } from 'react-router-dom'

import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'

export function Dashboard() {
  const { user, logout } = useAuth()
  const [adminPing, setAdminPing] = useState<string | null>(null)
  const [orgPing, setOrgPing] = useState<string | null>(null)

  async function tryAdminPing() {
    setAdminPing(null)
    try {
      const { data } = await apiClient.get<{ detail: string }>('/api/accounts/admin/ping/')
      setAdminPing(`OK: ${data.detail}`)
    } catch {
      setAdminPing('Forbidden or error (requires ADMIN role).')
    }
  }

  async function tryOrgPing() {
    setOrgPing(null)
    try {
      const { data } = await apiClient.get<{ detail: string }>(
        '/api/accounts/organization/ping/',
      )
      setOrgPing(`OK: ${data.detail}`)
    } catch {
      setOrgPing('Forbidden or error (requires ORGANIZATION or ADMIN).')
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-600">
            Signed in as <span className="font-medium">{user?.username}</span> ({user?.role})
          </p>
        </div>
        <div className="flex gap-3">
          <Link className="text-sm font-medium text-indigo-600 hover:text-indigo-500" to="/">
            Home
          </Link>
          <button
            type="button"
            className="text-sm font-medium text-slate-600 hover:text-slate-900"
            onClick={() => logout()}
          >
            Sign out
          </button>
        </div>
      </div>

      <section className="mt-10 space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-medium text-slate-900">Role checks</h2>
        <p className="text-sm text-slate-600">
          These call API routes protected by Django permissions. Expect <strong>403</strong> unless
          your role matches.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-50"
            onClick={() => void tryAdminPing()}
          >
            Call admin ping
          </button>
          <button
            type="button"
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-50"
            onClick={() => void tryOrgPing()}
          >
            Call organization ping
          </button>
        </div>
        {adminPing ? (
          <p className="text-sm text-slate-700">
            Admin route: {adminPing}
          </p>
        ) : null}
        {orgPing ? <p className="text-sm text-slate-700">Organization route: {orgPing}</p> : null}
      </section>
    </div>
  )
}
