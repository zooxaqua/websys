/**
 * ユーザー管理API
 */
import { http } from '../utils/http';
import type { User } from './auth';

export interface UserListResponse {
  users: User[];
  total: number;
  limit: number;
  offset: number;
}

export interface UserCreate {
  username: string;
  password: string;
  displayName: string;
  role: string;
  email: string;
  metadata?: Record<string, unknown>;
}

export async function listUsers(role?: string, limit = 100, offset = 0): Promise<UserListResponse> {
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  params.append('limit', limit.toString());
  params.append('offset', offset.toString());
  
  return http.get<UserListResponse>(`/api/sys/users?${params.toString()}`);
}

export async function getUser(userId: string): Promise<User> {
  return http.get<User>(`/api/sys/users/${userId}`);
}

export async function createUser(data: UserCreate): Promise<User> {
  return http.post<User>('/api/sys/users', data);
}

export async function deleteUser(userId: string): Promise<void> {
  await http.delete<void>(`/api/sys/users/${userId}`);
}
