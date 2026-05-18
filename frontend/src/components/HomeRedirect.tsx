import { Navigate } from 'react-router-dom'

import { defaultHomeForRole } from '../auth/postAuthRedirect'
import { useAuth } from '../auth/useAuth'
import { LoadingScreen } from './LoadingScreen'

/** `/` — unauthenticated users go to login; authenticated users to their role home. */
export function HomeRedirect() {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen message="Loading session…" />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <Navigate to={defaultHomeForRole(user.role)} replace />
}
