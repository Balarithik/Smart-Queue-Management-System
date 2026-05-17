import { motion } from 'framer-motion'
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { formatApiError } from '../api/errors'
import { apiClient, bareClient } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { PageLoader } from '../components/LoadingScreen'
import { formatEtaSeconds, useQueueStatus } from '../hooks/useQueueStatus'

type QueueSearchResult = {
  public_id: string
  name: string
  slug: string
  is_active: boolean
  queue_status: 'OPEN' | 'CLOSED'
  organization_id: number
  organization_name: string
  image_url: string | null
  waiting_count: number
}

type SearchResponse = {
  count: number
  next: string | null
  previous: string | null
  results: QueueSearchResult[]
}

type JoinResponse = {
  token: number
  waiting_ahead: number
  queue_name: string
  status: string
}

function QueueStatusBadge({ status }: { status: 'OPEN' | 'CLOSED' }) {
  const open = status === 'OPEN'
  return (
    <span
      className={
        open
          ? 'rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-800'
          : 'rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600'
      }
    >
      {open ? 'Open' : 'Closed'}
    </span>
  )
}

function SearchSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className="h-40 animate-pulse rounded-xl border border-slate-200 bg-white"
          aria-hidden
        />
      ))}
    </div>
  )
}

function QueueCatalogCard({ queue }: { queue: QueueSearchResult }) {
  const [joining, setJoining] = useState(false)
  const [joinError, setJoinError] = useState<string | null>(null)
  const [joined, setJoined] = useState<JoinResponse | null>(null)

  const { data: status, error: statusError, loading: statusLoading } = useQueueStatus(
    queue.public_id,
    joined?.token,
    { enabled: Boolean(joined) },
  )

  const canJoin = queue.queue_status === 'OPEN'

  async function handleJoin() {
    setJoinError(null)
    setJoining(true)
    try {
      const { data } = await bareClient.post<JoinResponse>(
        `/api/queues/${queue.public_id}/join/`,
        {},
      )
      setJoined(data)
    } catch (err) {
      setJoinError(formatApiError(err))
    } finally {
      setJoining(false)
    }
  }

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm"
    >
      {queue.image_url ? (
        <img
          src={queue.image_url}
          alt={`${queue.name} banner`}
          className="h-32 w-full object-cover"
        />
      ) : (
        <div className="flex h-20 items-center justify-center bg-slate-100 text-xs text-slate-400">
          No image
        </div>
      )}
      <div className="flex flex-1 flex-col p-4">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <h3 className="font-medium text-slate-900">{queue.name}</h3>
            <p className="text-sm text-slate-500">{queue.organization_name}</p>
          </div>
          <QueueStatusBadge status={queue.queue_status} />
        </div>
        <p className="mt-2 text-xs text-slate-500">
          {queue.waiting_count} waiting
        </p>

        {!joined ? (
          <button
            type="button"
            disabled={!canJoin || joining}
            onClick={() => void handleJoin()}
            className="mt-4 w-full rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {joining ? 'Joining…' : canJoin ? 'Join queue' : 'Queue closed'}
          </button>
        ) : (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-4 space-y-3 border-t border-slate-100 pt-4"
          >
            <p className="text-xs text-slate-500">Your token</p>
            <p className="text-3xl font-bold tabular-nums text-slate-900">{joined.token}</p>
            {status ? (
              <div className="space-y-1 text-sm text-slate-600">
                {status.status === 'WAITING' ? (
                  <p>
                    Position: <span className="font-medium">#{status.position}</span>
                  </p>
                ) : null}
                <p>
                  Ahead: <span className="font-medium">{status.waiting_ahead}</span>
                </p>
                <p>
                  ETA:{' '}
                  <span className="font-medium">{formatEtaSeconds(status.eta_seconds)}</span>
                </p>
              </div>
            ) : statusLoading ? (
              <PageLoader label="Updating status…" />
            ) : null}
            {statusError ? (
              <p className="text-xs text-amber-800">{statusError}</p>
            ) : null}
            <p className="text-xs text-slate-400">Status refreshes every 10 seconds</p>
          </motion.div>
        )}

        {joinError ? (
          <p className="mt-2 rounded-lg bg-red-50 px-2 py-1 text-xs text-red-800">{joinError}</p>
        ) : null}

        <Link
          className="mt-3 text-center text-xs font-medium text-indigo-600 hover:text-indigo-500"
          to={`/join/${queue.public_id}`}
        >
          Open full join page
        </Link>
      </div>
    </motion.article>
  )
}

function UserQueueCatalog() {
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [results, setResults] = useState<QueueSearchResult[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedQuery(query.trim()), 300)
    return () => window.clearTimeout(timer)
  }, [query])

  const fetchSearch = useCallback(async (q: string) => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await apiClient.get<SearchResponse>('/api/queues/search/', {
        params: { q, page: 1, page_size: 20, is_active: true },
      })
      setResults(data.results)
      setTotal(data.count)
    } catch (err) {
      setError(formatApiError(err))
      setResults([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchSearch(debouncedQuery)
  }, [debouncedQuery, fetchSearch])

  return (
    <section className="mt-10">
      <h2 className="text-lg font-medium text-slate-900">Find a queue</h2>
      <p className="mt-1 text-sm text-slate-600">
        Search by queue or organization name, then join without leaving this page.
      </p>
      <label className="mt-4 block">
        <span className="sr-only">Search queues</span>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search queues or organizations…"
          className="w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </label>

      {error ? (
        <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      ) : null}

      <div className="mt-6">
        {loading ? (
          <SearchSkeleton />
        ) : results.length === 0 ? (
          <p className="text-sm text-slate-600">
            {debouncedQuery
              ? `No active queues match “${debouncedQuery}”.`
              : 'No active queues are available right now.'}
          </p>
        ) : (
          <>
            <p className="mb-4 text-xs text-slate-500">
              {total} queue{total === 1 ? '' : 's'} found
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              {results.map((q) => (
                <QueueCatalogCard key={q.public_id} queue={q} />
              ))}
            </div>
          </>
        )}
      </div>
    </section>
  )
}

export function Dashboard() {
  const { user, logout } = useAuth()
  const isEndUser = user?.role === 'USER'

  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
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

      {isEndUser ? (
        <UserQueueCatalog />
      ) : (
        <section className="mt-10 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-medium text-slate-900">Account</h2>
          <p className="mt-2 text-sm text-slate-600">
            Use the organization or admin areas for queue management. End users can search and
            join queues from this dashboard.
          </p>
          {user?.role === 'ORGANIZATION' || user?.role === 'ADMIN' ? (
            <Link
              className="mt-4 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-500"
              to={user.role === 'ADMIN' ? '/admin/dashboard' : '/org/dashboard'}
            >
              Go to {user.role === 'ADMIN' ? 'admin' : 'organization'} dashboard →
            </Link>
          ) : null}
        </section>
      )}
    </div>
  )
}
