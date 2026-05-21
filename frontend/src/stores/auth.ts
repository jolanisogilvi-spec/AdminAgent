import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'
import { storage } from '@/utils'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  clearAuth: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()((
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      setAuth: (user, token) => {
        storage.setToken(token)
        storage.setUserInfo(user)
        set({ user, token, isAuthenticated: true })
      },

      clearAuth: () => {
        storage.clear()
        set({ user: null, token: null, isAuthenticated: false })
      },

      updateUser: (userData) => {
        set((state) => {
          if (!state.user) return state
          const updatedUser = { ...state.user, ...userData }
          storage.setUserInfo(updatedUser)
          return { user: updatedUser }
        })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
))