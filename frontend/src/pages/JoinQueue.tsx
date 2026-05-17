import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { bareClient } from '../api/client'
import { formatEtaSeconds, useQueueStatus } from '../hooks/useQueueStatus'

type PublicQueue = {
  name: string
  is_active: boolean
  public_id: string
}

type JoinResponse = {
  token: number
  waiting_ahead: number
  queue_name: string
  status: string
}

function formatApiError(err: unknown): string {
  if (!axios.isAxiosError(err) || err.response?.data == null) return 'Request failed.'
  const d = err.response.data
  if (typeof d === 'string') return d
  if (typeof d === 'object' && d && 'detail' in d && typeof (d as { detail: unknown }).detail === 'string') {
    return (d as { detail: string }).detail
  }
  return 'Request failed.'
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

export function JoinQueue() {
  const { publicId } = useParams<{ publicId: string }>()
  const [meta, setMeta] = useState<PublicQueue | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [joining, setJoining] = useState(false)
  const [joinError, setJoinError] = useState<string | null>(null)
  const [joined, setJoined] = useState<JoinResponse | null>(null)

  const { data: status, error: statusError, loading: statusLoading } = useQueueStatus(
    publicId,
    joined?.token,
    { enabled: Boolean(joined) },
  )

  useEffect(() => {
    if (!publicId) return
    let cancelled = false
    ;(async () => {
      setLoadError(null)
      try {
        const { data } = await bareClient.get<PublicQueue>(`/api/queues/${publicId}/`)
        if (!cancelled) setMeta(data)
      } catch (e) {
        if (!cancelled) setLoadError(formatApiError(e))
      }
    })()
    return () => {
      cancelled = true
    }
  }, [publicId])

  async function handleJoin() {
    if (!publicId) return
    setJoinError(null)
    setJoining(true)
    try {
      const { data } = await bareClient.post<JoinResponse>(`/api/queues/${publicId}/join/`, {})
      setJoined(data)
    } catch (e) {
      setJoinError(formatApiError(e))
    } finally {
      setJoining(false)
    }
  }

  if (!publicId) {
    return <p className="px-6 py-16 text-slate-600">Invalid link.</p>
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-md px-6 py-16">
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{loadError}</p>
        <Link className="mt-4 inline-block text-sm text-indigo-600" to="/">
          Home
        </Link>
      </div>
    )
  }

  if (!meta) {
    return <div className="flex min-h-[40vh] items-center justify-center text-slate-600">Loading…</div>
  }

  const displayStatus = status ?? null

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="text-2xl font-semibold text-slate-900">{meta.name}</h1>
        <QueueStatusBadge status={displayStatus?.queue_status ?? (meta.is_active ? 'OPEN' : 'CLOSED')} />
      </div>
      <p className="mt-2 text-sm text-slate-600">
        {meta.is_active ? 'This queue is open.' : 'This queue is closed.'}
      </p>

      {!joined ? (
        <>
          <button
            type="button"
            disabled={!meta.is_active || joining}
            onClick={() => void handleJoin()}
            className="mt-8 w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {joining ? 'Joining…' : 'Join queue'}
          </button>
          {joinError ? (
            <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{joinError}</p>
          ) : null}
        </>
      ) : (
        <div className="mt-8 space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm text-slate-600">Your token</p>
          <p className="text-4xl font-bold tabular-nums text-slate-900">{joined.token}</p>

          {displayStatus ? (
            <>
              <div className="grid gap-3 border-t border-slate-100 pt-4 text-sm">
                <div className="flex justify-between text-slate-600">
                  <span>Now serving</span>
                  <span className="font-medium tabular-nums text-slate-900">
                    {displayStatus.current_token != null ? `#${displayStatus.current_token}` : '—'}
                  </span>
                </div>
                {displayStatus.status === 'WAITING' ? (
                  <div className="flex justify-between text-slate-600">
                    <span>Your position</span>
                    <span className="font-medium tabular-nums text-slate-900">
                      #{displayStatus.position}
                    </span>
                  </div>
                ) : null}
                <div className="flex justify-between text-slate-600">
                  <span>People ahead</span>
                  <span className="font-medium tabular-nums text-slate-900">
                    {displayStatus.waiting_ahead}
                  </span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Estimated wait</span>
                  <span className="font-medium text-slate-900">
                    {formatEtaSeconds(displayStatus.eta_seconds)}
                  </span>
                </div>
                <div className="flex justify-between text-slate-600">
                  <span>Status</span>
                  <span className="font-medium text-slate-900">{displayStatus.status}</span>
                </div>
              </div>
              <p className="text-xs text-slate-400">
                Updates every 10 seconds
                {displayStatus.updated_at ? ` · Last: ${new Date(displayStatus.updated_at).toLocaleTimeString()}` : ''}
              </p>
            </>
          ) : statusLoading ? (
            <p className="text-sm text-slate-500">Refreshing status…</p>
          ) : null}

          {statusError ? (
            <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900">{statusError}</p>
          ) : null}
        </div>
      )}

      <p className="mt-8 text-center text-sm text-slate-500">
        <Link className="text-indigo-600 hover:text-indigo-500" to="/">
          Home
        </Link>
      </p>
    </div>
  )
}
