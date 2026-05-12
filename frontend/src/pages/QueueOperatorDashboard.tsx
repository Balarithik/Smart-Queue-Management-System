import axios from 'axios'
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { apiClient } from '../api/client'

type StaffQueue = {
  public_id: string
  name: string
  is_active: boolean
  last_token_issued: number
  join_url: string
  qr_png_base64: string
}

type DashboardPayload = {
  queue: StaffQueue
  waiting_count: number
  now_serving_token: number | null
  latest_waiting_tokens: number[]
}

type NextResponse = {
  called_token: number | null
  remaining_waiting: number
  detail?: string
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

export function QueueOperatorDashboard() {
  const { publicId } = useParams<{ publicId: string }>()
  const [data, setData] = useState<DashboardPayload | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [nextMessage, setNextMessage] = useState<string | null>(null)
  const [calling, setCalling] = useState(false)

  const refresh = useCallback(async () => {
    if (!publicId) return
    const { data: body } = await apiClient.get<DashboardPayload>(
      `/api/queues/${publicId}/dashboard/`,
    )
    setData(body)
  }, [publicId])

  useEffect(() => {
    if (!publicId) return
    let cancelled = false
    ;(async () => {
      setError(null)
      try {
        await refresh()
      } catch (e) {
        if (!cancelled) setError(formatApiError(e))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    const id = window.setInterval(() => {
      void refresh().catch(() => {})
    }, 5000)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [publicId, refresh])

  async function callNext() {
    if (!publicId) return
    setNextMessage(null)
    setCalling(true)
    try {
      const { data: body } = await apiClient.post<NextResponse>(`/api/queues/${publicId}/next/`, {})
      if (body.called_token != null) {
        setNextMessage(`Called token ${body.called_token}. Waiting left: ${body.remaining_waiting}.`)
      } else {
        setNextMessage(body.detail ?? 'No waiting entries.')
      }
      await refresh()
    } catch (e) {
      setNextMessage(formatApiError(e))
    } finally {
      setCalling(false)
    }
  }

  if (!publicId) {
    return <p className="px-6 py-16 text-slate-600">Missing queue id.</p>
  }

  if (loading) {
    return <div className="flex min-h-[40vh] items-center justify-center text-slate-600">Loading…</div>
  }

  if (error || !data) {
    return (
      <div className="mx-auto max-w-lg px-6 py-16">
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{error ?? 'Not found.'}</p>
        <Link className="mt-4 inline-block text-sm text-indigo-600" to="/org/dashboard">
          Organization dashboard
        </Link>
      </div>
    )
  }

  const q = data.queue
  const src = `data:image/png;base64,${q.qr_png_base64}`

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Queue status</h1>
          <p className="text-sm text-slate-600">{q.name}</p>
          <p className="mt-1 break-all text-xs text-slate-500">{q.join_url}</p>
        </div>
        <div className="flex flex-col gap-2 text-sm">
          <Link className="text-indigo-600 hover:text-indigo-500" to={`/queues/${publicId}/qr`}>
            View QR
          </Link>
          <Link className="text-slate-700 hover:text-slate-900" to="/org/dashboard">
            Organization dashboard
          </Link>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">Now serving (last called)</p>
            <p className="mt-1 text-3xl font-semibold tabular-nums text-slate-900">
              {data.now_serving_token ?? '—'}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-sm text-slate-500">Waiting</p>
            <p className="mt-1 text-3xl font-semibold tabular-nums text-slate-900">
              {data.waiting_count}
            </p>
            <p className="mt-2 text-xs text-slate-500">Last issued: {q.last_token_issued}</p>
          </div>
          <button
            type="button"
            disabled={calling}
            onClick={() => void callNext()}
            className="w-full rounded-lg bg-emerald-600 px-4 py-3 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-60"
          >
            {calling ? 'Calling…' : 'Call next'}
          </button>
          {nextMessage ? (
            <p className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-800">{nextMessage}</p>
          ) : null}
        </div>
        <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p className="text-center text-sm font-medium text-slate-700">QR</p>
          <div className="mt-4 flex justify-center">
            <img src={src} alt="" width={220} height={220} className="max-w-full" />
          </div>
        </div>
      </div>

      {data.latest_waiting_tokens.length > 0 ? (
        <section className="mt-10">
          <h2 className="text-lg font-medium text-slate-900">Latest waiting tokens</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {data.latest_waiting_tokens.map((t) => (
              <span
                key={t}
                className="rounded-lg bg-indigo-50 px-3 py-1 text-sm font-medium tabular-nums text-indigo-900"
              >
                {t}
              </span>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}
