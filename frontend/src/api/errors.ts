import axios from 'axios'

/** Shown under the username field — not mixed into API error messages. */
export const USERNAME_HINT =
  'Required, unique, max 150 characters. Letters, digits, and @ . + - _ only.'

function friendlyFieldMessage(field: string, messages: string[]): string | null {
  const text = messages.join(' ')
  if (field === 'username') {
    if (text.toLowerCase().includes('already exists')) {
      return 'This username is already taken. Sign in or choose a different username.'
    }
    if (text.toLowerCase().includes('valid username')) {
      return 'Username may only contain letters, numbers, and @ . + - _ characters.'
    }
    if (text.toLowerCase().includes('required')) {
      return 'Username is required.'
    }
    return text
  }
  if (field === 'password' || field === 'password_confirm') {
    return text
  }
  if (field === 'role') {
    return text
  }
  return `${field}: ${text}`
}

export function formatApiError(err: unknown, fallback = 'Request failed.'): string {
  if (!axios.isAxiosError(err) || err.response?.data == null) {
    return fallback
  }
  const status = err.response.status
  const data = err.response.data
  if (status >= 500) {
    return 'Server error. Please try again later.'
  }
  if (typeof data === 'string') return data
  if (typeof data === 'object' && data !== null) {
    const d = data as Record<string, unknown>
    if (typeof d.detail === 'string') return d.detail
    if (Array.isArray(d.detail)) {
      return d.detail.map((x) => (typeof x === 'string' ? x : JSON.stringify(x))).join(', ')
    }
    const lines: string[] = []
    for (const [key, val] of Object.entries(d)) {
      if (val === undefined || key === 'detail') continue
      if (typeof val === 'string') {
        const friendly = friendlyFieldMessage(key, [val])
        if (friendly) lines.push(friendly)
      } else if (Array.isArray(val)) {
        const friendly = friendlyFieldMessage(
          key,
          val.map((x) => (typeof x === 'string' ? x : String(x))),
        )
        if (friendly) lines.push(friendly)
      }
    }
    if (lines.length) return lines.join(' ')
  }
  return fallback
}
