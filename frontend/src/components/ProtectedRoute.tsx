import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { defaultHomeForRole } from '../auth/postAuthRedirect'
import type { UserRole } from '../auth/types'
import { useAuth } from '../auth/useAuth'
import { LoadingScreen } from './LoadingScreen'

type ProtectedRouteProps = {
  children: ReactNode
  roles?: UserRole[]
}

export function ProtectedRoute({ children, roles }: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return <LoadingScreen message="Loading session…" />
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  if (roles && roles.length > 0 && !roles.includes(user.role)) {
    return <Navigate to={defaultHomeForRole(user.role)} replace />
  }

  return <>{children}</>
}
