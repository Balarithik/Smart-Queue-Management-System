import axios from 'axios'
import { useEffect, useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'
import {
  EntriesOverTimeChart,
  type DailySeriesPoint,
} from '../components/reports/EntriesOverTimeChart'
import { RoleBreakdownChart } from '../components/reports/RoleBreakdownChart'
import { SignupsOverTimeChart, type SignupDay } from '../components/reports/SignupsOverTimeChart'
import { StatusBreakdownChart } from '../components/reports/StatusBreakdownChart'

type PlatformDashboard = {
  days: number
  start_date: string
  end_date: string
  users: {
    total_users: number
    active_users: number
    by_role: { USER: number; ORGANIZATION: number; ADMIN: number }
    signups_by_day: SignupDay[]
  }
  organizations: { total: number }
  queues: {
    total: number
    active: number
    waiting_count: number
    called_count: number
    completed_count: number
    total_entries: number
  }
  daily_series: DailySeriesPoint[]
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
    <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      {children}
    </div>
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

export function AdminDashboard() {
  const { user, logout } = useAuth()
  const [days, setDays] = useState<number>(30)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [report, setReport] = useState<PlatformDashboard | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      setLoading(true)
      setLoadError(null)
      try {
        const res = await apiClient.get<PlatformDashboard>('/api/reports/platform/', {
          params: { days },
        })
        if (!cancelled) setReport(res.data)
      } catch (err) {
        if (!cancelled) {
          setLoadError(formatApiError(err))
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
        <p className="text-slate-600">Loading platform metrics…</p>
      </div>
    )
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{loadError}</p>
        <Link className="mt-4 inline-block text-sm text-indigo-600" to="/">
          Back to home
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Admin dashboard</h1>
          <p className="text-sm text-slate-600">
            Platform monitoring · signed in as {user?.username} ({user?.role})
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

      {report ? (
        <>
          <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <StatCard label="Total users" value={report.users.total_users} />
            <StatCard label="Active users" value={report.users.active_users} />
            <StatCard label="Organizations" value={report.organizations.total} />
            <StatCard label="Total queues" value={report.queues.total} />
            <StatCard label="Active queues" value={report.queues.active} />
          </section>

          <section className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Joins (period)" value={report.queues.total_entries} />
            <StatCard label="Waiting" value={report.queues.waiting_count} />
            <StatCard label="Called" value={report.queues.called_count} />
            <StatCard label="Completed" value={report.queues.completed_count} />
          </section>

          <p className="mt-4 text-xs text-slate-500">
            {report.start_date} — {report.end_date} ({report.days} days)
          </p>

          <section className="mt-8">
            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">Platform activity over time</h2>
              <div className="mt-4">
                <EntriesOverTimeChart data={report.daily_series} />
              </div>
            </ReportCard>
          </section>

          <div className="mt-8 grid gap-8 lg:grid-cols-2">
            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">Queue entry status</h2>
              <div className="mt-4">
                <StatusBreakdownChart
                  waiting={report.queues.waiting_count}
                  called={report.queues.called_count}
                  completed={report.queues.completed_count}
                />
              </div>
            </ReportCard>

            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">Users by role</h2>
              <div className="mt-4">
                <RoleBreakdownChart
                  user={report.users.by_role.USER}
                  organization={report.users.by_role.ORGANIZATION}
                  admin={report.users.by_role.ADMIN}
                />
              </div>
            </ReportCard>
          </div>

          <section className="mt-8">
            <ReportCard>
              <h2 className="text-lg font-medium text-slate-900">User signups over time</h2>
              <div className="mt-4">
                <SignupsOverTimeChart data={report.users.signups_by_day} />
              </div>
            </ReportCard>
          </section>
        </>
      ) : null}
    </div>
  )
}
