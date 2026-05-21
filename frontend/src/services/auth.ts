import { apiClient } from './api';
import type { LoginRequest, LoginResponse, User } from '@/types';

export const authApi = {
  login: (data: LoginRequest) => {
    return apiClient.post<LoginResponse>('/auth/login', data);
  },

  register: (data: { username: string; password: string; name: string; department: string }) => {
    return apiClient.post<LoginResponse>('/auth/register', data);
  },

  getCurrentUser: () => {
    return apiClient.get<User>('/auth/me');
  },

  logout: () => {
    return apiClient.post('/auth/logout');
  },
};
