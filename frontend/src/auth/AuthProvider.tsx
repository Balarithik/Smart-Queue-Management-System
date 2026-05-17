import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'

import { apiClient, bareClient } from '../api/client'
import { AuthContext, type AuthContextValue, type RegisterPayload } from './authContext'
import { clearTokens, getAccessToken, setTokens } from './tokenStorage'
import type { AuthUser } from './types'

const ACCESS_STORAGE_KEY = 'sqms_access_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)
  const focusDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const refreshProfile = useCallback(async () => {
    const token = getAccessToken()
    if (!token) {
      setUser(null)
      return
    }
    const { data } = await apiClient.get<AuthUser>('/api/accounts/me/')
    setUser(data)
  }, [])

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        await refreshProfile()
      } catch {
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [refreshProfile])

  /** Other tabs overwrite localStorage tokens; re-fetch /me/ so role matches JWT (avoids 403 spam). */
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key !== ACCESS_STORAGE_KEY && e.key !== 'sqms_refresh_token') return
      void refreshProfile()
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [refreshProfile])

  useEffect(() => {
    const onFocus = () => {
      if (focusDebounceRef.current) clearTimeout(focusDebounceRef.current)
      focusDebounceRef.current = setTimeout(() => {
        focusDebounceRef.current = null
        if (!getAccessToken()) return
        void refreshProfile()
      }, 300)
    }
    window.addEventListener('focus', onFocus)
    return () => {
      window.removeEventListener('focus', onFocus)
      if (focusDebounceRef.current) clearTimeout(focusDebounceRef.current)
    }
  }, [refreshProfile])

  const login = useCallback(
    async (username: string, password: string) => {
      const { data } = await bareClient.post<{ access: string; refresh: string }>(
        '/api/accounts/token/',
        { username, password },
      )
      setTokens(data.access, data.refresh)
      await refreshProfile()
    },
    [refreshProfile],
  )

  const register = useCallback(async (payload: RegisterPayload) => {
    const { data } = await bareClient.post<AuthUser & { access: string; refresh: string }>(
      '/api/accounts/register/',
      payload,
    )
    const { access, refresh, ...profile } = data
    setTokens(access, refresh)
    setUser(profile)
  }, [])

  const logout = useCallback(() => {
    clearTokens()
    setUser(null)
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      refreshProfile,
    }),
    [user, loading, login, register, logout, refreshProfile],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
