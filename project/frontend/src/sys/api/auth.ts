/**
 * 認証API
 */
import { http } from '../utils/http';

export interface User {
  id: string;
  username: string;
  displayName: string;
  role: string;
  email: string;
  createdAt: string;
  lastLogin?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  user: User;
}

export async function login(username: string, password: string): Promise<User> {
  const response = await http.post<LoginResponse>('/api/sys/auth/login', {
    username,
    password,
  });
  return response.user;
}

export async function logout(): Promise<void> {
  await http.post<void>('/api/sys/auth/logout', {});
}

export async function getMe(): Promise<User> {
  return http.get<User>('/api/sys/auth/me');
}

export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
  await http.put<void>('/api/sys/auth/password', {
    currentPassword,
    newPassword,
  });
}
