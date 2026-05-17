import { type FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { formatApiError } from '../api/errors'
import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'

const MAX_IMAGE_BYTES = 2 * 1024 * 1024
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']

type CreatedQueue = {
  public_id: string
}

function validateImageFile(file: File): string | null {
  if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
    return 'Image must be JPEG or PNG.'
  }
  if (file.size > MAX_IMAGE_BYTES) {
    return 'Image must be 2 MB or smaller.'
  }
  return null
}

export function QueueCreate() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [organizationId, setOrganizationId] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imageError, setImageError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const previewUrl = useMemo(
    () => (imageFile ? URL.createObjectURL(imageFile) : null),
    [imageFile],
  )

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  function handleImageChange(file: File | null) {
    setImageError(null)
    if (!file) {
      setImageFile(null)
      return
    }
    const validation = validateImageFile(file)
    if (validation) {
      setImageError(validation)
      setImageFile(null)
      return
    }
    setImageFile(file)
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    if (imageFile) {
      const validation = validateImageFile(imageFile)
      if (validation) {
        setImageError(validation)
        return
      }
    }
    setSubmitting(true)
    try {
      const form = new FormData()
      form.append('name', name.trim())
      if (slug.trim()) form.append('slug', slug.trim())
      if (user?.role === 'ADMIN') {
        const id = Number.parseInt(organizationId, 10)
        if (!Number.isFinite(id)) {
          setError('Organization ID is required for administrators.')
          setSubmitting(false)
          return
        }
        form.append('organization_id', String(id))
      }
      if (imageFile) form.append('image', imageFile)

      const { data } = await apiClient.post<CreatedQueue>('/api/queues/', form, {
        headers: { 'Content-Type': undefined },
      })
      navigate(`/queues/${data.public_id}/qr`, { replace: true })
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-md px-6 py-16">
      <h1 className="text-2xl font-semibold text-slate-900">Create queue</h1>
      <p className="mt-2 text-sm text-slate-600">
        Creates a queue with a shareable ID and QR code. Optional banner image (JPEG/PNG, max 2
        MB).{' '}
        <Link className="font-medium text-indigo-600 hover:text-indigo-500" to="/org/dashboard">
          Back to organization
        </Link>
      </p>

      <form className="mt-8 space-y-4" onSubmit={(e) => void handleSubmit(e)}>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="qc-name">
            Display name
          </label>
          <input
            id="qc-name"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="qc-slug">
            Slug (optional)
          </label>
          <input
            id="qc-slug"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
            placeholder="auto from name"
          />
        </div>
        {user?.role === 'ADMIN' ? (
          <div>
            <label className="block text-sm font-medium text-slate-700" htmlFor="qc-org">
              Organization ID
            </label>
            <input
              id="qc-org"
              inputMode="numeric"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              placeholder="Target organization primary key"
              required
            />
          </div>
        ) : null}
        <div>
          <label className="block text-sm font-medium text-slate-700" htmlFor="qc-image">
            Banner image (optional)
          </label>
          <input
            id="qc-image"
            type="file"
            accept="image/jpeg,image/png"
            className="mt-1 block w-full text-sm text-slate-600 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-indigo-700"
            onChange={(e) => handleImageChange(e.target.files?.[0] ?? null)}
          />
          {previewUrl ? (
            <img
              src={previewUrl}
              alt="Queue banner preview"
              className="mt-3 h-32 w-full rounded-lg border border-slate-200 object-cover"
            />
          ) : null}
          {imageError ? (
            <p className="mt-2 text-sm text-red-700">{imageError}</p>
          ) : null}
        </div>
        {error ? (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
        ) : null}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-60"
        >
          {submitting ? 'Creating…' : 'Create queue'}
        </button>
      </form>
    </div>
  )
}
