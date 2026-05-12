import { createContext } from 'react'

import type { AuthUser } from './types'

export type RegisterPayload = {
  username: string
  email: string
  password: string
  password_confirm: string
  role?: AuthUser['role']
}

export type AuthContextValue = {
  user: AuthUser | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)
