import { useCallback, useEffect, useState } from 'react'

import { bareClient } from '../api/client'
import { POLL_INTERVAL_MS } from '../config/polling'
import { usePolling } from './usePolling'

export type QueueStatusSnapshot = {
  public_id: string
  queue_name: string
  queue_status: 'OPEN' | 'CLOSED'
  is_active: boolean
  current_token: number | null
  waiting_count: number
  token: number
  status: string
  position: number
  waiting_ahead: number
  eta_seconds: number | null
  updated_at: string
}

type Options = {
  intervalMs?: number
  enabled?: boolean
}

export function useQueueStatus(
  publicId: string | undefined,
  token: number | undefined,
  options: Options = {},
) {
  const intervalMs = options.intervalMs ?? POLL_INTERVAL_MS
  const [data, setData] = useState<QueueStatusSnapshot | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const enabled = options.enabled ?? true
  const shouldPoll =
    enabled &&
    Boolean(publicId && token != null) &&
    data?.status !== 'COMPLETED'

  const fetchStatus = useCallback(async () => {
    if (!publicId || token == null) return
    try {
      const { data: body } = await bareClient.get<QueueStatusSnapshot>(
        `/api/queues/${publicId}/status/`,
        { params: { token } },
      )
      setData(body)
      setError(null)
    } catch {
      setError('Unable to refresh status.')
    } finally {
      setLoading(false)
    }
  }, [publicId, token])

  useEffect(() => {
    if (!publicId || token == null) {
      setData(null)
      setLoading(false)
      return
    }
    setData(null)
    setLoading(true)
    setError(null)
  }, [publicId, token])

  usePolling(() => fetchStatus(), intervalMs, shouldPoll)

  return { data, error, loading: loading && data == null }
}

export function formatEtaSeconds(seconds: number | null | undefined): string {
  if (seconds == null) return '—'
  if (seconds <= 0) return 'Less than a minute'
  const minutes = Math.ceil(seconds / 60)
  if (minutes < 60) return `~${minutes} min`
  const hours = Math.floor(minutes / 60)
  const rem = minutes % 60
  return rem > 0 ? `~${hours}h ${rem}m` : `~${hours}h`
}
