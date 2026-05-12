import axios from 'axios'
import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'

function formatApiError(err: unknown): string {
  if (!axios.isAxiosError(err) || err.response?.data == null) return 'Request failed.'
  const data = err.response.data
  if (typeof data === 'string') return data
  if (typeof data === 'object' && data !== null && 'detail' in data && typeof (data as { detail?: unknown }).detail === 'string') {
    return (data as { detail: string }).detail
  }
  return 'Request failed.'
}

type CreatedQueue = {
  public_id: string
}

export function QueueCreate() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [organizationId, setOrganizationId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      const payload: { name: string; slug?: string; organization_id?: number } = { name: name.trim() }
      if (slug.trim()) payload.slug = slug.trim()
      if (user?.role === 'ADMIN') {
        const id = Number.parseInt(organizationId, 10)
        if (!Number.isFinite(id)) {
          setError('Organization ID is required for administrators.')
          setSubmitting(false)
          return
        }
        payload.organization_id = id
      }
      const { data } = await apiClient.post<CreatedQueue>('/api/queues/', payload)
      navigate(`/queues/${data.public_id}/qr`, { replace: true })
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="text-2xl font-semibold text-slate-900">Create queue</h1>
      <p className="mt-2 text-sm text-slate-600">
        Creates a queue with a shareable ID and QR code.{' '}
        <Link className="font-medium text-indigo-600 hover:text-indigo-500" to="/org/dashboard">
          Back to organization
        </Link>
      </p>

      <form className="mt-8 space-y-4" onSubmit={(e) => void handleSubmit(e)}>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="qc-name">
            Display name
          </label>
          <input
            id="qc-name"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="qc-slug">
            Slug (optional)
          </label>
          <input
            id="qc-slug"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="auto from name"
          />
        </div>
        {user?.role === 'ADMIN' ? (
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="qc-org">
              Organization ID
            </label>
            <input
              id="qc-org"
              inputMode="numeric"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              placeholder="Target organization primary key"
              required
            />
          </div>
        ) : null}
        {error ? (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
        ) : null}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
        >
          {submitting ? 'Creating…' : 'Create queue'}
        </button>
      </form>
    </div>
  )
}
