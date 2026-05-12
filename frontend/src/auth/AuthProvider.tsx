import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'

import { apiClient, bareClient } from '../api/client'
import { AuthContext, type AuthContextValue, type RegisterPayload } from './authContext'
import { clearTokens, getAccessToken, setTokens } from './tokenStorage'
import type { AuthUser } from './types'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

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
