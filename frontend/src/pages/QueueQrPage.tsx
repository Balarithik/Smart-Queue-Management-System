import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { apiClient } from '../api/client'

type ManageQueue = {
  public_id: string
  name: string
  join_url: string
  qr_png_base64: string
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

export function QueueQrPage() {
  const { publicId } = useParams<{ publicId: string }>()
  const [data, setData] = useState<ManageQueue | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!publicId) return
    let cancelled = false
    ;(async () => {
      setError(null)
      try {
        const { data: body } = await apiClient.get<ManageQueue>(`/api/queues/${publicId}/manage/`)
        if (!cancelled) setData(body)
      } catch (e) {
        if (!cancelled) setError(formatApiError(e))
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [publicId])

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

  const src = `data:image/png;base64,${data.qr_png_base64}`

  return (
    <div className="mx-auto max-w-lg px-6 py-16">
      <h1 className="text-2xl font-semibold text-slate-900">Queue QR</h1>
      <p className="mt-2 text-sm text-slate-600">{data.name}</p>
      <p className="mt-1 break-all text-xs text-slate-500">{data.join_url}</p>

      <div className="mt-8 flex justify-center rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <img src={src} alt="Queue join QR code" className="max-w-full" width={256} height={256} />
      </div>

      <div className="mt-8 flex flex-wrap gap-4 text-sm">
        <Link
          className="font-medium text-indigo-600 hover:text-indigo-500"
          to={`/queues/${publicId}/dashboard`}
        >
          Operator dashboard
        </Link>
        <Link className="font-medium text-slate-700 hover:text-slate-900" to="/org/dashboard">
          Organization dashboard
        </Link>
      </div>
    </div>
  )
}
