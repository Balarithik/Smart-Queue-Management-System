import { Link } from 'react-router-dom'

export function About() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight text-slate-900">About</h1>
      <p className="mt-4 text-slate-600">
        This frontend is scaffolded with Vite, React, Tailwind CSS v4, React Router v6, and Axios.
        Configure <code className="rounded bg-slate-100 px-1">VITE_API_BASE_URL</code> for production
        builds when the API is on another origin.
      </p>
      <p className="mt-6">
        <Link className="font-medium text-indigo-600 hover:text-indigo-500" to="/">
          ← Back home
        </Link>
      </p>
    </div>
  )
}
