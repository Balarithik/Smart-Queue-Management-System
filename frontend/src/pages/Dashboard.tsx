import { Link } from 'react-router-dom'

import { useAuth } from '../auth/useAuth'

export function Dashboard() {
  const { user, logout } = useAuth()

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
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

      <section className="mt-10 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="text-lg font-medium text-slate-900">Account</h2>
        <p className="mt-2 text-sm text-slate-600">
          Role-gated API routes (organization dashboard, queue staff tools) are listed in the
          project README. The dev server logs <code className="rounded bg-slate-100 px-1">Forbidden</code>{' '}
          when a request uses a token whose role is not allowed for that path—usually from another
          tab signing in as a different user while this tab still showed the old session.
        </p>
      </section>
    </div>
  )
}
