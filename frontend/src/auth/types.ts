export type UserRole = 'USER' | 'ORGANIZATION' | 'ADMIN'

export interface AuthUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
}
