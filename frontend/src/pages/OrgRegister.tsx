import { type FormEvent, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'

import { formatApiError, USERNAME_HINT } from '../api/errors'
import { useAuth } from '../auth/useAuth'

export function OrgRegister() {
  const { register, user } = useAuth()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirm, setPasswordConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) {
    return <Navigate to="/org/dashboard" replace />
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (password !== passwordConfirm) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      await register({
        username,
        email,
        password,
        password_confirm: passwordConfirm,
        role: 'ORGANIZATION',
      })
    } catch (err) {
      setError(formatApiError(err, 'Registration failed. Check your input and try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="text-2xl font-semibold text-slate-900">Organization account</h1>
      <p className="mt-2 text-sm text-slate-600">
        Register as an organization operator to create queues and manage your site. Already have an
        account?{' '}
        <Link className="font-medium text-indigo-600 hover:text-indigo-500" to="/org/login">
          Organization sign in
        </Link>
      </p>
      <p className="mt-1 text-sm text-slate-500">
        End-user account?{' '}
        <Link className="font-medium text-slate-700 hover:text-slate-900" to="/register">
          Standard registration
        </Link>
      </p>

      <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="org-reg-username">
            Username
          </label>
          <input
            id="org-reg-username"
            autoComplete="username"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <p className="mt-1 text-xs text-slate-500">{USERNAME_HINT}</p>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="org-email">
            Email
          </label>
          <input
            id="org-email"
            type="email"
            autoComplete="email"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="org-reg-password">
            Password
          </label>
          <input
            id="org-reg-password"
            type="password"
            autoComplete="new-password"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="org-reg-password2">
            Confirm password
          </label>
          <input
            id="org-reg-password2"
            type="password"
            autoComplete="new-password"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={passwordConfirm}
            onChange={(e) => setPasswordConfirm(e.target.value)}
            required
            minLength={8}
          />
        </div>
        {error ? (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
        ) : null}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
        >
          {submitting ? 'Creating…' : 'Create organization account'}
        </button>
      </form>
    </div>
  )
}
