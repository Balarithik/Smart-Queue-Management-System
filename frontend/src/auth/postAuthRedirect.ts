import type { UserRole } from './types'

const ORG_ONLY_PREFIXES = ['/org/', '/queues/']
const ADMIN_ONLY_PREFIXES = ['/admin/']

export function defaultHomeForRole(role: UserRole): string {
  if (role === 'ADMIN') return '/admin/dashboard'
  if (role === 'ORGANIZATION') return '/org/dashboard'
  return '/dashboard'
}

/**
 * After login, avoid sending personal (USER) accounts to org-operator URLs,
 * which would 403 and spam Django's WARNING logs for Forbidden.
 */
export function postAuthDestination(role: UserRole, from: string, fallback: string): string {
  const target = from.trim() || fallback
  const canUseOrgRoutes = role === 'ORGANIZATION' || role === 'ADMIN'
  const canUseAdminRoutes = role === 'ADMIN'
  if (canUseAdminRoutes) return target
  if (ADMIN_ONLY_PREFIXES.some((p) => target.startsWith(p))) {
    return defaultHomeForRole(role)
  }
  if (canUseOrgRoutes) return target
  if (ORG_ONLY_PREFIXES.some((p) => target.startsWith(p))) {
    return '/'
  }
  return target
}
