export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'
export const APP_TITLE = import.meta.env.VITE_APP_TITLE || '行政智能体'

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  USERS: '/users',
  SETTINGS: '/settings',
} as const

export const TOKEN_KEY = 'admin_token'
export const USER_INFO_KEY = 'user_info'

export const PAGE_SIZE = 10
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
