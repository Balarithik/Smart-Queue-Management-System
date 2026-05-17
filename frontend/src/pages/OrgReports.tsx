import axios from 'axios'
import { useEffect, useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'
import {
  EntriesOverTimeChart,
  type DailySeriesPoint,
} from '../components/reports/EntriesOverTimeChart'
import { QueueComparisonChart, type QueueSummary } from '../components/reports/QueueComparisonChart'
import { StatusBreakdownChart } from '../components/reports/StatusBreakdownChart'

type Organization = {
  id: number
  name: string
  slug: string
}

type OrganizationReport = {
  organization_id: number
  name: string
  days: number
  start_date: string
  end_date: string
  queue_count: number
  active_queue_count: number
  total_entries: number
  waiting_count: number
  called_count: number
  completed_count: number
  daily_series: DailySeriesPoint[]
  queues: QueueSummary[]
}

const DAY_OPTIONS = [7, 30, 90] as const

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
  }
  return 'Request failed.'
}

function ReportCard({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">{children}</div>
  )
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <ReportCard>
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
    </ReportCard>
  )
}

export function OrgReports() {
  const { user, logout } = useAuth()
  const [days, setDays] = useState<number>(30)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [org, setOrg] = useState<Organization | null>(null)
  const [report, setReport] = useState<OrganizationReport | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setLoadError(null)
      try {
        const meRes = await apiClient.get<Organization>('/api/organizations/me/')
        if (cancelled) return
        const currentOrg = meRes.data
        setOrg(currentOrg)
        const reportRes = await apiClient.get<OrganizationReport>(
          `/api/reports/organizations/${currentOrg.id}/`,
          { params: { days } },
        )
        if (cancelled) return
        setReport(reportRes.data)
      } catch (err) {
        if (!cancelled) {
          setLoadError(formatApiError(err))
          setOrg(null)
          setReport(null)
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [days])

  if (loading) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <p className="text-slate-600">Loading analytics…</p>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{loadError}</p>
        <Link className="mt-4 inline-block text-sm text-indigo-600" to="/org/dashboard">
          Back to org dashboard
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <ReportsPageHeader org={org} user={user} days={days} setDays={setDays} logout={logout} />

      {report ? (
        <>
          <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Total joins" value={report.total_entries} />
            <StatCard label="Waiting" value={report.waiting_count} />
            <StatCard label="Called" value={report.called_count} />
            <StatCard label="Completed" value={report.completed_count} />
          </section>

          <p className="mt-4 text-xs text-slate-500">
            {report.start_date} — {report.end_date} ({report.days} days) · {report.queue_count}{' '}
            queues ({report.active_queue_count} active)
          </p>

          <section className="mt-8">
            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">Activity over time</h2>
              <div className="mt-4">
                <EntriesOverTimeChart data={report.daily_series} />
              </div>
            </ReportCard>
          </section>

          <div className="mt-8 grid gap-8 lg:grid-cols-2">
            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">Status breakdown</h2>
              <div className="mt-4">
                <StatusBreakdownChart
                  waiting={report.waiting_count}
                  called={report.called_count}
                  completed={report.completed_count}
                />
              </div>
            </ReportCard>

            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">Per-queue comparison</h2>
              <div className="mt-4">
                <QueueComparisonChart queues={report.queues} />
              </div>
            </ReportCard>
          </div>

          {report.queues.length > 0 ? (
            <section className="mt-8">
              <h2 className="text-lg font-medium text-slate-900">Queue detail</h2>
              <ul className="mt-4 divide-y divide-slate-200 rounded-xl border border-slate-200 bg-white">
                {report.queues.map((q) => (
                  <li
                    key={q.queue_id}
                    className="flex flex-wrap items-center justify-between gap-4 px-4 py-3"
                  >
                    <QueueReportRowContent q={q} />
                  </li>
                ))}
              </ul>
            </section>
          ) : null}
        </>
      ) : null}
    </div>
  )
}

function ReportsPageHeader({
  org,
  user,
  days,
  setDays,
  logout,
}: {
  org: Organization | null
  user: { username?: string; role?: string } | null
  days: number
  setDays: (d: number) => void
  logout: () => void
}) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Analytics</h1>
        <p className="text-sm text-slate-600">
          {org ? org.name : 'Organization'} · signed in as {user?.username} ({user?.role})
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-2 text-sm text-slate-600">
          Period
          <select
            className="rounded-lg border border-slate-300 bg-white px-2 py-1 text-slate-900"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            {DAY_OPTIONS.map((d) => (
              <option key={d} value={d}>
                {d} days
              </option>
            ))}
          </select>
        </label>
        <Link
          className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          to="/org/dashboard"
        >
          Org dashboard
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
  )
}

function QueueReportRowContent({ q }: { q: QueueSummary }) {
  return (
    <>
      <div>
        <span className="font-medium text-slate-900">{q.name}</span>
        <span className="ml-2 text-sm text-slate-500">
          {q.joins} joins · {q.completed} completed
        </span>
      </div>
      <Link
        className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
        to={`/queues/${q.public_id}/dashboard`}
      >
        Operator dashboard
      </Link>
    </>
  )
}
