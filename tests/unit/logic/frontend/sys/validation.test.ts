/**
 * バリデーションユーティリティ 単体テスト
 */

import { describe, it, expect } from 'vitest';
import {
  validateUsername,
  validatePassword,
  validateEmail,
  validateDisplayName,
} from '@/sys/utils/validation';

describe('validation', () => {
  describe('validateUsername', () => {
    it('正常系: 有効なユーザー名', () => {
      // Act
      const result = validateUsername('testuser');

      // Assert
      expect(result.valid).toBe(true);
      expect(result.message).toBeUndefined();
    });

    it('正常系: 数字を含むユーザー名', () => {
      // Act
      const result = validateUsername('user123');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('正常系: アンダースコアを含むユーザー名', () => {
      // Act
      const result = validateUsername('test_user');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('異常系: 空文字列', () => {
      // Act
      const result = validateUsername('');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toBe('ユーザー名を入力してください');
    });

    it('境界値: 3文字（最小値）', () => {
      // Act
      const result = validateUsername('abc');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('境界値: 2文字（最小値未満）', () => {
      // Act
      const result = validateUsername('ab');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toContain('3文字以上50文字以内');
    });

    it('境界値: 50文字（最大値）', () => {
      // Act
      const result = validateUsername('a'.repeat(50));

      // Assert
      expect(result.valid).toBe(true);
    });

    it('境界値: 51文字（最大値超過）', () => {
      // Act
      const result = validateUsername('a'.repeat(51));

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toContain('3文字以上50文字以内');
    });

    it('異常系: ハイフンを含む', () => {
      // Act
      const result = validateUsername('test-user');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toContain('英数字とアンダースコアのみ');
    });

    it('異常系: スペースを含む', () => {
      // Act
      const result = validateUsername('test user');

      // Assert
      expect(result.valid).toBe(false);
    });

    it('異常系: 特殊文字を含む', () => {
      // Act
      const result = validateUsername('test@user');

      // Assert
      expect(result.valid).toBe(false);
    });
  });

  describe('validatePassword', () => {
    it('正常系: 有効なパスワード', () => {
      // Act
      const result = validatePassword('password123');

      // Assert
      expect(result.valid).toBe(true);
      expect(result.message).toBeUndefined();
    });

    it('異常系: 空文字列', () => {
      // Act
      const result = validatePassword('');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toBe('パスワードを入力してください');
    });

    it('境界値: 8文字（最小値）', () => {
      // Act
      const result = validatePassword('12345678');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('境界値: 7文字（最小値未満）', () => {
      // Act
      const result = validatePassword('1234567');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toContain('8文字以上');
    });

    it('正常系: 長いパスワード', () => {
      // Act
      const result = validatePassword('a'.repeat(100));

      // Assert
      expect(result.valid).toBe(true);
    });

    it('正常系: 特殊文字を含む', () => {
      // Act
      const result = validatePassword('P@ssw0rd!');

      // Assert
      expect(result.valid).toBe(true);
    });
  });

  describe('validateEmail', () => {
    it('正常系: 有効なメールアドレス', () => {
      // Act
      const result = validateEmail('test@example.com');

      // Assert
      expect(result.valid).toBe(true);
      expect(result.message).toBeUndefined();
    });

    it('異常系: 空文字列', () => {
      // Act
      const result = validateEmail('');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toBe('メールアドレスを入力してください');
    });

    it('異常系: @なし', () => {
      // Act
      const result = validateEmail('testexample.com');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toContain('形式が不正');
    });

    it('異常系: ドメインなし', () => {
      // Act
      const result = validateEmail('test@');

      // Assert
      expect(result.valid).toBe(false);
    });

    it('異常系: ローカルパートなし', () => {
      // Act
      const result = validateEmail('@example.com');

      // Assert
      expect(result.valid).toBe(false);
    });

    it('異常系: ドット抜け', () => {
      // Act
      const result = validateEmail('test@examplecom');

      // Assert
      expect(result.valid).toBe(false);
    });

    it('正常系: サブドメイン付き', () => {
      // Act
      const result = validateEmail('test@mail.example.com');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('正常系: 数字を含む', () => {
      // Act
      const result = validateEmail('test123@example.com');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('正常系: ハイフンを含む', () => {
      // Act
      const result = validateEmail('test-user@example.com');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('異常系: スペースを含む', () => {
      // Act
      const result = validateEmail('test user@example.com');

      // Assert
      expect(result.valid).toBe(false);
    });
  });

  describe('validateDisplayName', () => {
    it('正常系: 有効な表示名', () => {
      // Act
      const result = validateDisplayName('太郎');

      // Assert
      expect(result.valid).toBe(true);
      expect(result.message).toBeUndefined();
    });

    it('異常系: 空文字列', () => {
      // Act
      const result = validateDisplayName('');

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toBe('表示名を入力してください');
    });

    it('境界値: 1文字（最小値）', () => {
      // Act
      const result = validateDisplayName('A');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('境界値: 100文字（最大値）', () => {
      // Act
      const result = validateDisplayName('あ'.repeat(100));

      // Assert
      expect(result.valid).toBe(true);
    });

    it('境界値: 101文字（最大値超過）', () => {
      // Act
      const result = validateDisplayName('あ'.repeat(101));

      // Assert
      expect(result.valid).toBe(false);
      expect(result.message).toContain('1文字以上100文字以内');
    });

    it('正常系: 日本語', () => {
      // Act
      const result = validateDisplayName('山田太郎');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('正常系: 英数字', () => {
      // Act
      const result = validateDisplayName('John Doe 123');

      // Assert
      expect(result.valid).toBe(true);
    });

    it('正常系: 特殊文字を含む', () => {
      // Act
      const result = validateDisplayName('テスト (Test)');

      // Assert
      expect(result.valid).toBe(true);
    });
  });
});
