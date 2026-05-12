import type { UserRole } from './types'

const ORG_ONLY_PREFIXES = ['/org/', '/queues/']

/**
 * After login, avoid sending personal (USER) accounts to org-operator URLs,
 * which would 403 and spam Django's WARNING logs for Forbidden.
 */
export function postAuthDestination(role: UserRole, from: string, fallback: string): string {
  const target = from.trim() || fallback
  const canUseOrgRoutes = role === 'ORGANIZATION' || role === 'ADMIN'
  if (canUseOrgRoutes) return target
  if (ORG_ONLY_PREFIXES.some((p) => target.startsWith(p))) {
    return '/'
  }
  return target
}
