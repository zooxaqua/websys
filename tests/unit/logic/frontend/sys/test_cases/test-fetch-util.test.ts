/**
 * 単体テスト: Fetch Utility
 * 
 * テスト対象: project/frontend/src/sys/utils/fetch.ts
 * MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiFetch } from '../../../../../../project/frontend/src/sys/utils/fetch';

// グローバルfetchをモック
global.fetch = vi.fn();

describe('Fetch Utility', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // TC-FETCH-001: 正常系 - GETリクエスト成功
  it('should fetch successfully', async () => {
    const mockData = { id: '1', name: 'Test' };
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockData,
    });

    const result = await apiFetch('/api/test');

    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith('/api/test', expect.objectContaining({
      credentials: 'include',
    }));
  });

  // TC-FETCH-002: 正常系 - POSTリクエスト成功
  it('should post data successfully', async () => {
    const mockResponse = { success: true };
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => mockResponse,
    });

    const result = await apiFetch('/api/test', {
      method: 'POST',
      body: JSON.stringify({ name: 'Test' }),
    });

    expect(result).toEqual(mockResponse);
  });

  // TC-FETCH-003: 正常系 - 204 No Content
  it('should handle 204 No Content', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 204,
    });

    const result = await apiFetch('/api/test');

    expect(result).toBeUndefined();
  });

  // TC-FETCH-004: 異常系 - 404 Not Found
  it('should throw error on 404', async () => {
    const mockError = { error: { code: 'NOT_FOUND', message: 'Not found' } };
    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 404,
      json: async () => mockError,
    });

    await expect(apiFetch('/api/test')).rejects.toEqual(mockError);
  });

  // TC-FETCH-005: 異常系 - ネットワークエラー
  it('should handle network error', async () => {
    (global.fetch as any).mockRejectedValue(new TypeError('Network error'));

    await expect(apiFetch('/api/test')).rejects.toMatchObject({
      error: {
        code: 'ERR-SYS-NET-001',
        message: 'ネットワークエラーが発生しました',
      },
    });
  });

  // TC-FETCH-006: 正常系 - カスタムヘッダー
  it('should include custom headers', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    });

    await apiFetch('/api/test', {
      headers: { 'X-Custom': 'value' },
    });

    expect(global.fetch).toHaveBeenCalledWith('/api/test', expect.objectContaining({
      headers: expect.objectContaining({
        'X-Custom': 'value',
      }),
    }));
  });

  // TC-FETCH-007: 正常系 - skipErrorHandling
  it('should skip error handling when specified', async () => {
    const mockError = { error: { code: 'ERROR', message: 'Error' } };
    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => mockError,
    });

    await expect(apiFetch('/api/test', { skipErrorHandling: true })).rejects.toEqual(mockError);
  });

  // TC-FETCH-008: 境界値 - 空のレスポンス
  it('should handle empty response', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    });

    const result = await apiFetch('/api/test');

    expect(result).toEqual({});
  });

  // TC-FETCH-009: 正常系 - credentials設定
  it('should include credentials', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({}),
    });

    await apiFetch('/api/test');

    expect(global.fetch).toHaveBeenCalledWith('/api/test', expect.objectContaining({
      credentials: 'include',
    }));
  });

  // TC-FETCH-010: 異常系 - 500 Internal Server Error
  it('should throw error on 500', async () => {
    const mockError = { error: { code: 'INTERNAL_ERROR', message: 'Server error' } };
    (global.fetch as any).mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => mockError,
    });

    await expect(apiFetch('/api/test')).rejects.toEqual(mockError);
  });
});
