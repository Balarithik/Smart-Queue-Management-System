import axios from 'axios'
import { type FormEvent, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'

type Organization = {
  id: number
  name: string
  slug: string
  description: string
  owner_id: number
  created_at: string
  updated_at: string
}

type QueueRow = {
  id: number
  public_id: string
  name: string
  slug: string
  is_active: boolean
  last_token_issued: number
  created_at: string
  join_url: string
  qr_image_url: string | null
  qr_png_base64: string
}

type OrgStats = {
  organization_id: number
  name: string
  queue_count: number
  active_queue_count: number
}

function formatApiError(err: unknown): string {
  if (!axios.isAxiosError(err) || err.response?.data == null) {
    return 'Request failed.'
  }
  const data = err.response.data
  if (typeof data === 'string') return data
  if (typeof data === 'object' && data !== null) {
    const d = data as Record<string, unknown>
    if (typeof d.detail === 'string') return d.detail
    if (Array.isArray(d.detail)) {
      return d.detail.map((x) => (typeof x === 'string' ? x : JSON.stringify(x))).join(', ')
    }
    const lines: string[] = []
    for (const [key, val] of Object.entries(d)) {
      if (val === undefined || key === 'detail') continue
      if (typeof val === 'string') lines.push(`${key}: ${val}`)
      else if (Array.isArray(val)) lines.push(`${key}: ${val.join(', ')}`)
    }
    if (lines.length) return lines.join(' ')
  }
  return 'Request failed.'
}

export function OrgDashboard() {
  const { user, logout } = useAuth()
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [needsSetup, setNeedsSetup] = useState(false)
  const [org, setOrg] = useState<Organization | null>(null)

  const [queues, setQueues] = useState<QueueRow[]>([])
  const [stats, setStats] = useState<OrgStats | null>(null)
  const [secondaryError, setSecondaryError] = useState<string | null>(null)

  const [createName, setCreateName] = useState('')
  const [createSlug, setCreateSlug] = useState('')
  const [createDescription, setCreateDescription] = useState('')
  const [createError, setCreateError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      await Promise.resolve()
      if (cancelled) return
      setLoadError(null)
      if (!user || (user.role !== 'ORGANIZATION' && user.role !== 'ADMIN')) {
        setLoading(false)
        return
      }
      try {
        const { data } = await apiClient.get<Organization>('/api/organizations/me/')
        if (!cancelled) {
          setOrg(data)
          setNeedsSetup(false)
        }
      } catch (e) {
        if (cancelled) return
        if (axios.isAxiosError(e) && e.response?.status === 404) {
          setNeedsSetup(true)
        } else {
          setLoadError(formatApiError(e))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [user])

  useEffect(() => {
    if (!org) return
    let cancelled = false
    ;(async () => {
      setSecondaryError(null)
      try {
        const [qRes, sRes] = await Promise.all([
          apiClient.get<QueueRow[]>(`/api/organizations/${org.id}/queues/`),
          apiClient.get<OrgStats>(`/api/organizations/${org.id}/stats/`),
        ])
        if (!cancelled) {
          setQueues(qRes.data)
          setStats(sRes.data)
        }
      } catch (e) {
        if (!cancelled) setSecondaryError(formatApiError(e))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [org])

  async function handleCreateOrg(e: FormEvent) {
    e.preventDefault()
    setCreateError(null)
    setCreating(true)
    try {
      const payload: { name: string; description?: string; slug?: string } = {
        name: createName.trim(),
        description: createDescription.trim(),
      }
      if (createSlug.trim()) payload.slug = createSlug.trim()
      const { data } = await apiClient.post<Organization>('/api/organizations/', payload)
      setOrg(data)
      setNeedsSetup(false)
    } catch (err) {
      setCreateError(formatApiError(err))
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-slate-600">
        Loading organization…
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-16">
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{loadError}</p>
        <Link className="mt-4 inline-block text-sm font-medium text-indigo-600" to="/">
          Home
        </Link>
      </div>
    )
  }

  if (needsSetup && !org) {
    return (
      <div className="mx-auto max-w-lg px-6 py-16">
        <h1 className="text-2xl font-semibold text-slate-900">Create your organization</h1>
        <p className="mt-2 text-sm text-slate-600">
          Your account does not have an organization profile yet. Add a display name to continue.
        </p>
        <form className="mt-8 space-y-4" onSubmit={(e) => void handleCreateOrg(e)}>
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="org-name">
              Organization name
            </label>
            <input
              id="org-name"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={createName}
              onChange={(e) => setCreateName(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="org-slug">
              URL slug (optional)
            </label>
            <input
              id="org-slug"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={createSlug}
              onChange={(e) => setCreateSlug(e.target.value)}
              placeholder="auto-generated if empty"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="org-desc">
              Description (optional)
            </label>
            <textarea
              id="org-desc"
              rows={3}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={createDescription}
              onChange={(e) => setCreateDescription(e.target.value)}
            />
          </div>
          {createError ? (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{createError}</p>
          ) : null}
          <button
            type="submit"
            disabled={creating}
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
          >
            {creating ? 'Saving…' : 'Create organization'}
          </button>
        </form>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Organization dashboard</h1>
          <p className="text-sm text-slate-600">
            Signed in as <span className="font-medium">{user?.username}</span> ({user?.role})
          </p>
        </div>
        <div className="flex gap-3">
          <Link className="text-sm font-medium text-indigo-600 hover:text-indigo-500" to="/org/reports">
            View analytics →
          </Link>
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

      {org ? (
        <section className="mt-10 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-medium text-slate-900">{org.name}</h2>
          <p className="mt-1 text-sm text-slate-500">Slug: {org.slug}</p>
          {org.description ? (
            <p className="mt-3 text-sm text-slate-600">{org.description}</p>
          ) : null}
        </section>
      ) : null}

      {stats ? (
        <section className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">Queues</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{stats.queue_count}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">Active queues</p>
            <p className="mt-1 text-2xl font-semibold text-slate-900">{stats.active_queue_count}</p>
          </div>
        </section>
      ) : null}

      {secondaryError ? (
        <p className="mt-6 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">{secondaryError}</p>
      ) : null}

      <section className="mt-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <h2 className="text-lg font-medium text-slate-900">Queues</h2>
          <Link
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
            to="/queues/create"
          >
            Create queue
          </Link>
        </div>
        {queues.length === 0 ? (
          <p className="mt-2 text-sm text-slate-600">
            No queues yet. Use Create queue to add one and generate a QR join link.
          </p>
        ) : (
          <ul className="mt-4 divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
            {queues.map((q) => (
              <li
                key={q.id}
                className="flex flex-wrap items-start justify-between gap-4 px-4 py-4"
              >
                <div className="flex min-w-0 flex-1 gap-4">
                  {q.qr_image_url ? (
                    <img
                      src={q.qr_image_url}
                      alt=""
                      width={96}
                      height={96}
                      className="h-24 w-24 shrink-0 rounded-lg border border-slate-200 bg-white object-contain"
                    />
                  ) : (
                    <div
                      className="flex h-24 w-24 shrink-0 items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50 text-xs text-slate-400"
                      title="QR unavailable"
                    >
                      QR
                    </div>
                  )}
                  <div className="min-w-0">
                    <span className="font-medium text-slate-900">{q.name}</span>
                    <span className="ml-2 text-sm text-slate-500">{q.slug}</span>
                    <p className="mt-0.5 text-xs text-slate-400">Issued: {q.last_token_issued}</p>
                    <p className="mt-1 break-all text-xs text-slate-500">{q.join_url}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3">
                  <span
                    className={
                      q.is_active ? 'text-xs font-medium text-emerald-700' : 'text-xs text-slate-500'
                    }
                  >
                    {q.is_active ? 'Active' : 'Inactive'}
                  </span>
                  <Link
                    className="text-xs font-medium text-indigo-600 hover:text-indigo-500"
                    to={`/queues/${q.public_id}/dashboard`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    className="text-xs font-medium text-slate-600 hover:text-slate-900"
                    to={`/queues/${q.public_id}/qr`}
                  >
                    QR page
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
