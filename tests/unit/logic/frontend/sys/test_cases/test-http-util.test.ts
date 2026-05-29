/**
 * 単体テスト: HttpClient (http.ts)
 * 
 * テスト対象: project/frontend/src/sys/utils/http.ts
 * MCDCカバレッジ: 100%
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HttpClient } from '@sys/utils/http';
import fixtures from '/Users/zooaqua/Desktop/repo/websys/tests/unit/inputs/fixtures/http-fixtures.json';
import expected from '/Users/zooaqua/Desktop/repo/websys/tests/unit/inputs/expected/http-expected.json';

describe('HttpClient', () => {
  let httpClient: HttpClient;
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    httpClient = new HttpClient();
    fetchMock = vi.fn();
    global.fetch = fetchMock;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('request()', () => {
    it('TC-HTTP-001: 正常系（response.ok = true）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(fixtures.testData.successResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.request(fixtures.testUrls.get);

      // Assert
      expect(result).toEqual(expected.testCases['TC-HTTP-001'].expected.data);
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.get,
        expect.objectContaining({
          credentials: 'include',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('TC-HTTP-002: 異常系（response.ok = false, error.error.message）', async () => {
      // Arrange
      const mockResponse = {
        ok: false,
        json: vi.fn().mockResolvedValue(fixtures.testData.errorResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act & Assert
      await expect(httpClient.request(fixtures.testUrls.get)).rejects.toThrow(
        expected.testCases['TC-HTTP-002'].expected.message
      );
    });

    it('TC-HTTP-003: 異常系（response.ok = false, error.message）', async () => {
      // Arrange
      const mockResponse = {
        ok: false,
        json: vi.fn().mockResolvedValue(fixtures.testData.errorResponseLegacy),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act & Assert
      await expect(httpClient.request(fixtures.testUrls.get)).rejects.toThrow(
        expected.testCases['TC-HTTP-003'].expected.message
      );
    });

    it('TC-HTTP-004: 異常系（response.ok = false, JSONパース失敗）', async () => {
      // Arrange
      const mockResponse = {
        ok: false,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON')),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act & Assert
      await expect(httpClient.request(fixtures.testUrls.get)).rejects.toThrow(
        expected.testCases['TC-HTTP-004'].expected.message
      );
    });

    it('TC-HTTP-011: credentials = "include" が設定される', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({}),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      await httpClient.request(fixtures.testUrls.get);

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.get,
        expect.objectContaining({
          credentials: expected.testCases['TC-HTTP-011'].expected.credentials,
        })
      );
    });

    it('TC-HTTP-012: Content-Type = "application/json" が設定される', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({}),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      await httpClient.request(fixtures.testUrls.get);

      // Assert
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.get,
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': expected.testCases['TC-HTTP-012'].expected.contentType,
          }),
        })
      );
    });

    it('TC-HTTP-013: 異常系（error.error, error.message 両方なし）', async () => {
      // Arrange
      const mockResponse = {
        ok: false,
        json: vi.fn().mockResolvedValue(fixtures.testData.errorResponseEmptyMessages),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act & Assert
      await expect(httpClient.request(fixtures.testUrls.get)).rejects.toThrow(
        expected.testCases['TC-HTTP-013'].expected.message
      );
    });
  });

  describe('get()', () => {
    it('TC-HTTP-005: 正常系（GETメソッド呼び出し）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(fixtures.testData.successResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.get(fixtures.testUrls.get);

      // Assert
      expect(result).toEqual(fixtures.testData.successResponse);
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.get,
        expect.objectContaining({
          method: expected.testCases['TC-HTTP-005'].expected.method,
        })
      );
    });
  });

  describe('post()', () => {
    it('TC-HTTP-006: 正常系（POSTメソッド、データあり）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(fixtures.testData.successResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.post(
        fixtures.testUrls.post,
        fixtures.testData.postData
      );

      // Assert
      expect(result).toEqual(fixtures.testData.successResponse);
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.post,
        expect.objectContaining({
          method: expected.testCases['TC-HTTP-006'].expected.method,
          body: JSON.stringify(fixtures.testData.postData),
        })
      );
    });
  });

  describe('put()', () => {
    it('TC-HTTP-007: 正常系（PUTメソッド、データあり）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(fixtures.testData.successResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.put(
        fixtures.testUrls.put,
        fixtures.testData.putData
      );

      // Assert
      expect(result).toEqual(fixtures.testData.successResponse);
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.put,
        expect.objectContaining({
          method: expected.testCases['TC-HTTP-007'].expected.method,
          body: JSON.stringify(fixtures.testData.putData),
        })
      );
    });
  });

  describe('delete()', () => {
    it('TC-HTTP-008: 正常系（DELETEメソッド）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({}),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.delete(fixtures.testUrls.delete);

      // Assert
      expect(result).toEqual({});
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.delete,
        expect.objectContaining({
          method: expected.testCases['TC-HTTP-008'].expected.method,
        })
      );
    });
  });

  describe('patch()', () => {
    it('TC-HTTP-009: 正常系（PATCHメソッド、data = あり）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(fixtures.testData.successResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.patch(
        fixtures.testUrls.patch,
        fixtures.testData.patchData
      );

      // Assert
      expect(result).toEqual(fixtures.testData.successResponse);
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.patch,
        expect.objectContaining({
          method: expected.testCases['TC-HTTP-009'].expected.method,
          body: JSON.stringify(fixtures.testData.patchData),
        })
      );
    });

    it('TC-HTTP-010: 正常系（PATCHメソッド、data = なし）', async () => {
      // Arrange
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue(fixtures.testData.successResponse),
      };
      fetchMock.mockResolvedValue(mockResponse);

      // Act
      const result = await httpClient.patch(fixtures.testUrls.patch);

      // Assert
      expect(result).toEqual(fixtures.testData.successResponse);
      expect(fetchMock).toHaveBeenCalledWith(
        fixtures.testUrls.patch,
        expect.objectContaining({
          method: expected.testCases['TC-HTTP-010'].expected.method,
          body: undefined,
        })
      );
    });
  });
});
