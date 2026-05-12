import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { bareClient } from '../api/client'

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

type StatusResponse = {
  token: number
  status: string
  waiting_ahead: number
  queue_name: string
  is_active: boolean
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

export function JoinQueue() {
  const { publicId } = useParams<{ publicId: string }>()
  const [meta, setMeta] = useState<PublicQueue | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [joining, setJoining] = useState(false)
  const [joinError, setJoinError] = useState<string | null>(null)
  const [joined, setJoined] = useState<JoinResponse | null>(null)
  const [status, setStatus] = useState<StatusResponse | null>(null)

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

  useEffect(() => {
    if (!publicId || !joined) return
    const token = joined.token
    let cancelled = false
    const poll = async () => {
      try {
        const { data } = await bareClient.get<StatusResponse>(
          `/api/queues/${publicId}/status/?token=${token}`,
        )
        if (!cancelled) setStatus(data)
      } catch {
        /* ignore transient errors while polling */
      }
    }
    void poll()
    const id = window.setInterval(() => void poll(), 4000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [publicId, joined])

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

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="text-2xl font-semibold text-slate-900">{meta.name}</h1>
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
          <p className="text-sm text-slate-600">
            People ahead of you: <span className="font-medium text-slate-900">{joined.waiting_ahead}</span>
          </p>
          {status ? (
            <div className="border-t border-slate-100 pt-4 text-sm text-slate-600">
              <p>Status: {status.status}</p>
              {status.status === 'WAITING' ? (
                <p className="mt-1">Still ahead: {status.waiting_ahead}</p>
              ) : null}
            </div>
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
