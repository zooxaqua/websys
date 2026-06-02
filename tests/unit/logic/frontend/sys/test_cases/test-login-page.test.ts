/**
 * 単体テスト: Login Page
 * 
 * テスト対象: project/frontend/src/sys/pages/login.ts
 * MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import loginPage from '../../../../../../project/frontend/src/sys/pages/login';
import * as authModule from '../../../../../../project/frontend/src/sys/api/auth';

// auth モジュールをモック
vi.mock('../../../../../../project/frontend/src/sys/api/auth');

// window.location.reload をモック
delete (window as any).location;
(window as any).location = { reload: vi.fn() };

describe('Login Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // TC-LOGIN-001: 正常系 - ログイン成功
  it('should login successfully', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = 'SecurePass123!';
    
    vi.spyOn(authModule, 'login').mockResolvedValue({
      success: true,
      user: { id: 'user-001', username: 'testuser', email: 'test@example.com', role: 'user', displayName: 'Test', createdAt: '', updatedAt: '' },
    });

    await loginInstance.login();

    expect(loginInstance.isAuthenticated).toBe(true);
    expect(loginInstance.error).toBe('');
    expect(window.location.reload).toHaveBeenCalled();
  });

  // TC-LOGIN-002: 異常系 - ログイン失敗（認証エラー）
  it('should handle login failure', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = 'wrongpassword';
    
    vi.spyOn(authModule, 'login').mockRejectedValue(new Error('認証に失敗しました'));

    await loginInstance.login();

    expect(loginInstance.isAuthenticated).toBe(false);
    expect(loginInstance.error).toBe('認証に失敗しました');
    expect(window.location.reload).not.toHaveBeenCalled();
  });

  // TC-LOGIN-003: 異常系 - ログイン失敗（一般エラー）
  it('should handle generic error', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = 'pass';
    
    vi.spyOn(authModule, 'login').mockRejectedValue('Unknown error');

    await loginInstance.login();

    expect(loginInstance.error).toBe('ログインに失敗しました');
  });

  // TC-LOGIN-004: 境界値 - 空のユーザー名
  it('should handle empty username', async () => {
    const loginInstance = loginPage();
    loginInstance.username = '';
    loginInstance.password = 'pass';
    
    vi.spyOn(authModule, 'login').mockRejectedValue(new Error('ユーザー名が必要です'));

    await loginInstance.login();

    expect(loginInstance.error).toBe('ユーザー名が必要です');
  });

  // TC-LOGIN-005: 境界値 - 空のパスワード
  it('should handle empty password', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = '';
    
    vi.spyOn(authModule, 'login').mockRejectedValue(new Error('パスワードが必要です'));

    await loginInstance.login();

    expect(loginInstance.error).toBe('パスワードが必要です');
  });

  // TC-LOGIN-006: 正常系 - エラーメッセージクリア
  it('should clear error on successful login', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = 'pass';
    loginInstance.error = 'Previous error';
    
    vi.spyOn(authModule, 'login').mockResolvedValue({
      success: true,
      user: { id: 'user-001', username: 'testuser', email: 'test@example.com', role: 'user', displayName: 'Test', createdAt: '', updatedAt: '' },
    });

    await loginInstance.login();

    expect(loginInstance.error).toBe('');
  });

  // TC-LOGIN-007: MCDC - エラーがErrorインスタンスの場合
  it('should use error message when error is Error instance', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = 'pass';
    
    vi.spyOn(authModule, 'login').mockRejectedValue(new Error('Custom error message'));

    await loginInstance.login();

    expect(loginInstance.error).toBe('Custom error message');
  });

  // TC-LOGIN-008: MCDC - エラーがErrorインスタンスでない場合
  it('should use default message when error is not Error instance', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'testuser';
    loginInstance.password = 'pass';
    
    vi.spyOn(authModule, 'login').mockRejectedValue({ code: 'ERR-001' });

    await loginInstance.login();

    expect(loginInstance.error).toBe('ログインに失敗しました');
  });

  // TC-LOGIN-009: 正常系 - 初期状態
  it('should have correct initial state', () => {
    const loginInstance = loginPage();

    expect(loginInstance.username).toBe('');
    expect(loginInstance.password).toBe('');
    expect(loginInstance.error).toBe('');
    expect(loginInstance.isAuthenticated).toBe(false);
  });

  // TC-LOGIN-010: 境界値 - 長いユーザー名/パスワード
  it('should handle long credentials', async () => {
    const loginInstance = loginPage();
    loginInstance.username = 'a'.repeat(100);
    loginInstance.password = 'b'.repeat(100);
    
    vi.spyOn(authModule, 'login').mockResolvedValue({
      success: true,
      user: { id: 'user-001', username: loginInstance.username, email: 'test@example.com', role: 'user', displayName: 'Test', createdAt: '', updatedAt: '' },
    });

    await loginInstance.login();

    expect(loginInstance.isAuthenticated).toBe(true);
  });
});
