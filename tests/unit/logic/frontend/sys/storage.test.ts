/**
 * ローカルストレージユーティリティ 単体テスト
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setItem, getItem, removeItem, clear, hasItem, getAllKeys } from '@/sys/utils/storage';

describe('storage', () => {
  beforeEach(() => {
    // localStorageをクリア
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('setItem', () => {
    it('正常系: アイテムを保存', () => {
      // Arrange
      const key = 'testKey';
      const value = { name: 'test', count: 123 };

      // Act
      setItem(key, value);

      // Assert
      const stored = localStorage.getItem(key);
      expect(stored).toBe(JSON.stringify(value));
    });

    it('正常系: 文字列を保存', () => {
      // Arrange
      const key = 'stringKey';
      const value = 'test string';

      // Act
      setItem(key, value);

      // Assert
      const stored = localStorage.getItem(key);
      expect(stored).toBe(JSON.stringify(value));
    });

    it('正常系: 数値を保存', () => {
      // Arrange
      const key = 'numberKey';
      const value = 42;

      // Act
      setItem(key, value);

      // Assert
      const stored = localStorage.getItem(key);
      expect(stored).toBe('42');
    });

    it('正常系: 配列を保存', () => {
      // Arrange
      const key = 'arrayKey';
      const value = [1, 2, 3];

      // Act
      setItem(key, value);

      // Assert
      const stored = localStorage.getItem(key);
      expect(stored).toBe('[1,2,3]');
    });

    it('境界値: 空オブジェクトを保存', () => {
      // Arrange
      const key = 'emptyObject';
      const value = {};

      // Act
      setItem(key, value);

      // Assert
      const stored = localStorage.getItem(key);
      expect(stored).toBe('{}');
    });

    it('境界値: null を保存', () => {
      // Arrange
      const key = 'nullKey';
      const value = null;

      // Act
      setItem(key, value);

      // Assert
      const stored = localStorage.getItem(key);
      expect(stored).toBe('null');
    });
  });

  describe('getItem', () => {
    it('正常系: アイテムを取得', () => {
      // Arrange
      const key = 'testKey';
      const value = { name: 'test', count: 123 };
      localStorage.setItem(key, JSON.stringify(value));

      // Act
      const result = getItem<typeof value>(key);

      // Assert
      expect(result).toEqual(value);
    });

    it('異常系: 存在しないキー', () => {
      // Act
      const result = getItem<string>('nonexistent');

      // Assert
      expect(result).toBeNull();
    });

    it('正常系: 文字列を取得', () => {
      // Arrange
      const key = 'stringKey';
      const value = 'test';
      localStorage.setItem(key, JSON.stringify(value));

      // Act
      const result = getItem<string>(key);

      // Assert
      expect(result).toBe(value);
    });

    it('正常系: 数値を取得', () => {
      // Arrange
      const key = 'numberKey';
      const value = 42;
      localStorage.setItem(key, JSON.stringify(value));

      // Act
      const result = getItem<number>(key);

      // Assert
      expect(result).toBe(value);
    });

    it('境界値: 空文字列', () => {
      // Arrange
      const key = 'emptyString';
      localStorage.setItem(key, JSON.stringify(''));

      // Act
      const result = getItem<string>(key);

      // Assert
      expect(result).toBe('');
    });
  });

  describe('removeItem', () => {
    it('正常系: アイテムを削除', () => {
      // Arrange
      const key = 'testKey';
      localStorage.setItem(key, 'value');

      // Act
      removeItem(key);

      // Assert
      expect(localStorage.getItem(key)).toBeNull();
    });

    it('正常系: 存在しないキーを削除（エラーにならない）', () => {
      // Act & Assert
      expect(() => removeItem('nonexistent')).not.toThrow();
    });
  });

  describe('clear', () => {
    it('正常系: 全アイテムをクリア', () => {
      // Arrange
      localStorage.setItem('key1', 'value1');
      localStorage.setItem('key2', 'value2');

      // Act
      clear();

      // Assert
      expect(localStorage.length).toBe(0);
    });

    it('境界値: 既に空の場合', () => {
      // Act & Assert
      expect(() => clear()).not.toThrow();
      expect(localStorage.length).toBe(0);
    });
  });

  describe('hasItem', () => {
    it('正常系: アイテムが存在する', () => {
      // Arrange
      const key = 'testKey';
      localStorage.setItem(key, 'value');

      // Act
      const result = hasItem(key);

      // Assert
      expect(result).toBe(true);
    });

    it('正常系: アイテムが存在しない', () => {
      // Act
      const result = hasItem('nonexistent');

      // Assert
      expect(result).toBe(false);
    });

    it('境界値: 空文字列値が保存されている場合', () => {
      // Arrange
      const key = 'emptyKey';
      localStorage.setItem(key, '');

      // Act
      const result = hasItem(key);

      // Assert
      expect(result).toBe(true);
    });
  });

  describe('getAllKeys', () => {
    it('正常系: 全キーを取得', () => {
      // Arrange
      localStorage.setItem('key1', 'value1');
      localStorage.setItem('key2', 'value2');
      localStorage.setItem('key3', 'value3');

      // Act
      const keys = getAllKeys();

      // Assert
      expect(keys).toHaveLength(3);
      expect(keys).toContain('key1');
      expect(keys).toContain('key2');
      expect(keys).toContain('key3');
    });

    it('境界値: ストレージが空', () => {
      // Act
      const keys = getAllKeys();

      // Assert
      expect(keys).toHaveLength(0);
    });

    it('境界値: キーが1つ', () => {
      // Arrange
      localStorage.setItem('onlyKey', 'value');

      // Act
      const keys = getAllKeys();

      // Assert
      expect(keys).toHaveLength(1);
      expect(keys[0]).toBe('onlyKey');
    });
  });
});
