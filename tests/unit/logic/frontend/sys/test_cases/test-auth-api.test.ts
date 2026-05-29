/**
 * 認証API 単体テスト
 * 
 * MCDC 100%達成を目標とする
 * 
 * 対象: project/frontend/src/sys/api/auth.ts
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { login, logout, getMe, changePassword, type User } from '../../../../../project/frontend/src/sys/api/auth';
import * as httpModule from '../../../../../project/frontend/src/sys/utils/http';
import fixtures from '../../../inputs/fixtures/frontend-fixtures.json';
import expected from '../../../inputs/expected/frontend-expected.json';

describe('認証API: login', () => {
  let httpPostSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // http.post をモック化
    httpPostSpy = vi.spyOn(httpModule.http, 'post');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-001
   * 正常系: 有効なユーザー名・パスワードでログイン成功
   * 条件: username=valid AND password=valid
   * 期待: User オブジェクトが返される
   */
  it('TC-AUTH-LOGIN-001: 有効な認証情報でログイン成功', async () => {
    const { username, password } = fixtures.auth.login_requests.valid;
    const expectedUser = expected.auth.login.success;

    httpPostSpy.mockResolvedValue(fixtures.auth.api_responses.login_success);

    const result = await login(username, password);

    expect(httpPostSpy).toHaveBeenCalledWith('/api/sys/auth/login', {
      username,
      password,
    });
    expect(result).toEqual(expectedUser);
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-002
   * 異常系: 無効なパスワード
   * 条件: username=valid AND password=invalid
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-LOGIN-002: 無効なパスワードでログイン失敗', async () => {
    const { username, password } = fixtures.auth.login_requests.invalid_password;

    httpPostSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(login(username, password)).rejects.toThrow(
      expected.auth.errors.invalid_credentials
    );
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-003
   * 異常系: 存在しないユーザー名
   * 条件: username=invalid AND password=valid
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-LOGIN-003: 存在しないユーザー名でログイン失敗', async () => {
    const { username, password } = fixtures.auth.login_requests.invalid_username;

    httpPostSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(login(username, password)).rejects.toThrow(
      expected.auth.errors.invalid_credentials
    );
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-004
   * 境界値: 空のユーザー名
   * 条件: username=empty AND password=valid
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-LOGIN-004: 空のユーザー名でログイン失敗', async () => {
    const { username, password } = fixtures.auth.login_requests.empty_username;

    httpPostSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(login(username, password)).rejects.toThrow();
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-005
   * 境界値: 空のパスワード
   * 条件: username=valid AND password=empty
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-LOGIN-005: 空のパスワードでログイン失敗', async () => {
    const { username, password } = fixtures.auth.login_requests.empty_password;

    httpPostSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(login(username, password)).rejects.toThrow();
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-006
   * 境界値: 非常に長いユーザー名（100文字）
   * 条件: username.length=100 AND password=valid
   * 期待: リクエストが送信される（サーバー側でバリデーション）
   */
  it('TC-AUTH-LOGIN-006: 長いユーザー名でのリクエスト', async () => {
    const { username, password } = fixtures.auth.login_requests.boundary_long_username;

    httpPostSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(login(username, password)).rejects.toThrow();
    expect(httpPostSpy).toHaveBeenCalledWith('/api/sys/auth/login', {
      username,
      password,
    });
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGIN-007
   * 境界値: 非常に長いパスワード（200文字）
   * 条件: username=valid AND password.length=200
   * 期待: リクエストが送信される
   */
  it('TC-AUTH-LOGIN-007: 長いパスワードでのリクエスト', async () => {
    const { username, password } = fixtures.auth.login_requests.boundary_long_password;

    httpPostSpy.mockResolvedValue(fixtures.auth.api_responses.login_success);

    const result = await login(username, password);
    expect(result).toBeDefined();
    expect(httpPostSpy).toHaveBeenCalledWith('/api/sys/auth/login', {
      username,
      password,
    });
  });
});

describe('認証API: logout', () => {
  let httpPostSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    httpPostSpy = vi.spyOn(httpModule.http, 'post');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGOUT-001
   * 正常系: ログアウト成功
   * 条件: 認証済みセッション存在
   * 期待: エラーなく完了
   */
  it('TC-AUTH-LOGOUT-001: ログアウト成功', async () => {
    httpPostSpy.mockResolvedValue(undefined);

    await expect(logout()).resolves.toBeUndefined();
    expect(httpPostSpy).toHaveBeenCalledWith('/api/sys/auth/logout', {});
  });

  /**
   * MCDC テストケース: TC-AUTH-LOGOUT-002
   * 異常系: セッションなし（未認証）
   * 条件: セッション存在しない
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-LOGOUT-002: セッションなしでログアウト失敗', async () => {
    httpPostSpy.mockRejectedValue(new Error(expected.auth.errors.unauthorized));

    await expect(logout()).rejects.toThrow(expected.auth.errors.unauthorized);
  });
});

describe('認証API: getMe', () => {
  let httpGetSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    httpGetSpy = vi.spyOn(httpModule.http, 'get');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * MCDC テストケース: TC-AUTH-GETME-001
   * 正常系: 認証済みユーザー情報取得成功
   * 条件: 有効なセッション存在
   * 期待: User オブジェクトが返される
   */
  it('TC-AUTH-GETME-001: 認証済みユーザー情報取得成功', async () => {
    const expectedUser = expected.auth.getMe.success;

    httpGetSpy.mockResolvedValue(fixtures.auth.api_responses.me_success);

    const result = await getMe();

    expect(httpGetSpy).toHaveBeenCalledWith('/api/sys/auth/me');
    expect(result).toEqual(expectedUser);
  });

  /**
   * MCDC テストケース: TC-AUTH-GETME-002
   * 異常系: 未認証（セッションなし）
   * 条件: セッション存在しない
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-GETME-002: 未認証でユーザー情報取得失敗', async () => {
    httpGetSpy.mockRejectedValue(new Error(expected.auth.errors.unauthorized));

    await expect(getMe()).rejects.toThrow(expected.auth.errors.unauthorized);
  });
});

describe('認証API: changePassword', () => {
  let httpPutSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    httpPutSpy = vi.spyOn(httpModule.http, 'put');
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  /**
   * MCDC テストケース: TC-AUTH-CHANGEPWD-001
   * 正常系: パスワード変更成功
   * 条件: currentPassword=valid AND newPassword=valid
   * 期待: エラーなく完了
   */
  it('TC-AUTH-CHANGEPWD-001: パスワード変更成功', async () => {
    const { currentPassword, newPassword } = fixtures.auth.change_password_requests.valid;

    httpPutSpy.mockResolvedValue(undefined);

    await expect(changePassword(currentPassword, newPassword)).resolves.toBeUndefined();
    expect(httpPutSpy).toHaveBeenCalledWith('/api/sys/auth/password', {
      currentPassword,
      newPassword,
    });
  });

  /**
   * MCDC テストケース: TC-AUTH-CHANGEPWD-002
   * 異常系: 現在のパスワードが誤り
   * 条件: currentPassword=invalid AND newPassword=valid
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-CHANGEPWD-002: 現在のパスワード誤りで変更失敗', async () => {
    const { currentPassword, newPassword } = fixtures.auth.change_password_requests.invalid_current;

    httpPutSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(changePassword(currentPassword, newPassword)).rejects.toThrow(
      expected.auth.errors.invalid_credentials
    );
  });

  /**
   * MCDC テストケース: TC-AUTH-CHANGEPWD-003
   * 異常系: 新しいパスワードが弱い（短い）
   * 条件: currentPassword=valid AND newPassword=weak
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-CHANGEPWD-003: 弱いパスワードで変更失敗', async () => {
    const { currentPassword, newPassword } = fixtures.auth.change_password_requests.weak_new_password;

    httpPutSpy.mockRejectedValue(
      new Error(expected.auth.errors.weak_password)
    );

    await expect(changePassword(currentPassword, newPassword)).rejects.toThrow(
      expected.auth.errors.weak_password
    );
  });

  /**
   * MCDC テストケース: TC-AUTH-CHANGEPWD-004
   * 境界値: 現在のパスワードが空
   * 条件: currentPassword=empty AND newPassword=valid
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-CHANGEPWD-004: 空の現在のパスワードで変更失敗', async () => {
    const { currentPassword, newPassword } = fixtures.auth.change_password_requests.empty_current;

    httpPutSpy.mockRejectedValue(
      new Error(expected.auth.errors.invalid_credentials)
    );

    await expect(changePassword(currentPassword, newPassword)).rejects.toThrow();
  });

  /**
   * MCDC テストケース: TC-AUTH-CHANGEPWD-005
   * 境界値: 新しいパスワードが空
   * 条件: currentPassword=valid AND newPassword=empty
   * 期待: エラーがスローされる
   */
  it('TC-AUTH-CHANGEPWD-005: 空の新しいパスワードで変更失敗', async () => {
    const { currentPassword, newPassword } = fixtures.auth.change_password_requests.empty_new;

    httpPutSpy.mockRejectedValue(
      new Error(expected.auth.errors.weak_password)
    );

    await expect(changePassword(currentPassword, newPassword)).rejects.toThrow();
  });
});
