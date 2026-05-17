import { useEffect, useRef } from 'react'

/**
 * Run callback immediately and on a fixed interval while enabled.
 */
export function usePolling(
  callback: () => void | Promise<void>,
  intervalMs: number,
  enabled = true,
): void {
  const callbackRef = useRef(callback)
  callbackRef.current = callback

  useEffect(() => {
    if (!enabled) return

    let cancelled = false

    const run = () => {
      if (cancelled) return
      void Promise.resolve(callbackRef.current()).catch(() => {})
    }

    run()
    const id = window.setInterval(run, intervalMs)
    return () => {
      cancelled = true
      window.clearInterval(id)
    }
  }, [intervalMs, enabled])
}
