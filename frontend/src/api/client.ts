import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios'

import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
} from '../auth/tokenStorage'

const baseURL = import.meta.env.VITE_API_BASE_URL ?? ''

/** Used for login/register/refresh so we never attach a stale Authorization header. */
export const bareClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean }

let refreshPromise: Promise<string | null> | null = null

function refreshAccessToken(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      const refresh = getRefreshToken()
      if (!refresh) {
        clearTokens()
        return null
      }
      try {
        const { data } = await bareClient.post<{ access: string }>(
          '/api/accounts/token/refresh/',
          { refresh },
        )
        setAccessToken(data.access)
        return data.access
      } catch {
        clearTokens()
        return null
      }
    })().finally(() => {
      refreshPromise = null
    })
  }
  return refreshPromise
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config as RetryConfig | undefined
    const status = error.response?.status
    const url = original?.url ?? ''

    if (
      status === 401 &&
      original &&
      !original._retry &&
      typeof url === 'string' &&
      !url.includes('/token/refresh') &&
      !url.includes('/token/')
    ) {
      original._retry = true
      const access = await refreshAccessToken()
      if (access) {
        original.headers.Authorization = `Bearer ${access}`
        return apiClient(original as AxiosRequestConfig)
      }
    }

    return Promise.reject(error)
  },
)
