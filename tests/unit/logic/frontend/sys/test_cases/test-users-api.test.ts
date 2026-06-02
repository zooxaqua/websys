/**
 * 単体テスト: Users API
 * 
 * テスト対象: project/frontend/src/sys/api/users.ts
 * MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { listUsers, getUser, createUser, deleteUser } from '../../../../../../project/frontend/src/sys/api/users';
import * as httpModule from '../../../../../../project/frontend/src/sys/utils/http';

// http モジュールをモック
vi.mock('../../../../../../project/frontend/src/sys/utils/http');

describe('Users API', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // TC-USERS-API-TS-001: 正常系 - ユーザー一覧取得
  it('should list users successfully', async () => {
    const mockResponse = {
      users: [{ id: 'user-001', username: 'testuser', email: 'test@example.com' }],
      total: 1,
      limit: 100,
      offset: 0,
    };
    vi.spyOn(httpModule.http, 'get').mockResolvedValue(mockResponse);

    const result = await listUsers();

    expect(result.users).toHaveLength(1);
    expect(result.total).toBe(1);
    expect(httpModule.http.get).toHaveBeenCalledWith('/api/sys/users?limit=100&offset=0');
  });

  // TC-USERS-API-TS-002: 正常系 - ロールでフィルタ
  it('should filter users by role', async () => {
    const mockResponse = { users: [], total: 0, limit: 100, offset: 0 };
    vi.spyOn(httpModule.http, 'get').mockResolvedValue(mockResponse);

    await listUsers('admin');

    expect(httpModule.http.get).toHaveBeenCalledWith('/api/sys/users?role=admin&limit=100&offset=0');
  });

  // TC-USERS-API-TS-003: 正常系 - ページネーション
  it('should paginate users', async () => {
    const mockResponse = { users: [], total: 100, limit: 10, offset: 20 };
    vi.spyOn(httpModule.http, 'get').mockResolvedValue(mockResponse);

    await listUsers(undefined, 10, 20);

    expect(httpModule.http.get).toHaveBeenCalledWith('/api/sys/users?limit=10&offset=20');
  });

  // TC-USERS-API-TS-004: 正常系 - ユーザー詳細取得
  it('should get user by ID', async () => {
    const mockUser = { id: 'user-001', username: 'testuser', email: 'test@example.com' };
    vi.spyOn(httpModule.http, 'get').mockResolvedValue(mockUser);

    const result = await getUser('user-001');

    expect(result.id).toBe('user-001');
    expect(httpModule.http.get).toHaveBeenCalledWith('/api/sys/users/user-001');
  });

  // TC-USERS-API-TS-005: 異常系 - ユーザーが存在しない
  it('should throw error when user not found', async () => {
    vi.spyOn(httpModule.http, 'get').mockRejectedValue(new Error('User not found'));

    await expect(getUser('nonexistent')).rejects.toThrow('User not found');
  });

  // TC-USERS-API-TS-006: 正常系 - ユーザー作成
  it('should create user successfully', async () => {
    const newUser = {
      username: 'newuser',
      password: 'Pass123!',
      displayName: 'New User',
      role: 'user',
      email: 'new@example.com',
    };
    const mockResponse = { id: 'user-002', ...newUser };
    vi.spyOn(httpModule.http, 'post').mockResolvedValue(mockResponse);

    const result = await createUser(newUser);

    expect(result.username).toBe('newuser');
    expect(httpModule.http.post).toHaveBeenCalledWith('/api/sys/users', newUser);
  });

  // TC-USERS-API-TS-007: 異常系 - ユーザー作成失敗（重複）
  it('should throw error when creating duplicate user', async () => {
    const newUser = {
      username: 'testuser',
      password: 'Pass123!',
      displayName: 'Test',
      role: 'user',
      email: 'test@example.com',
    };
    vi.spyOn(httpModule.http, 'post').mockRejectedValue(new Error('User already exists'));

    await expect(createUser(newUser)).rejects.toThrow('User already exists');
  });

  // TC-USERS-API-TS-008: 正常系 - ユーザー削除
  it('should delete user successfully', async () => {
    vi.spyOn(httpModule.http, 'delete').mockResolvedValue(undefined);

    await deleteUser('user-001');

    expect(httpModule.http.delete).toHaveBeenCalledWith('/api/sys/users/user-001');
  });

  // TC-USERS-API-TS-009: 異常系 - ユーザー削除失敗
  it('should throw error when deleting user fails', async () => {
    vi.spyOn(httpModule.http, 'delete').mockRejectedValue(new Error('Delete failed'));

    await expect(deleteUser('user-001')).rejects.toThrow('Delete failed');
  });

  // TC-USERS-API-TS-010: 境界値 - 空のユーザー一覧
  it('should handle empty user list', async () => {
    const mockResponse = { users: [], total: 0, limit: 100, offset: 0 };
    vi.spyOn(httpModule.http, 'get').mockResolvedValue(mockResponse);

    const result = await listUsers();

    expect(result.users).toHaveLength(0);
    expect(result.total).toBe(0);
  });
});
