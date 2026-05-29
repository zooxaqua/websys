/**
 * ローカルストレージユーティリティ
 * 
 * ブラウザのlocalStorageを安全に操作するユーティリティ関数を提供します。
 * - JSON自動変換
 * - エラーハンドリング
 * - TypeScript型安全性
 */

/**
 * ローカルストレージにアイテムを保存
 * 
 * @param key - ストレージキー
 * @param value - 保存する値（JSON.stringifyで自動変換）
 */
export function setItem<T>(key: string, value: T): void {
  try {
    const serialized = JSON.stringify(value);
    localStorage.setItem(key, serialized);
  } catch (error) {
    console.error(`Failed to save to localStorage (key: ${key}):`, error);
  }
}

/**
 * ローカルストレージからアイテムを取得
 * 
 * @param key - ストレージキー
 * @returns 取得した値、存在しない場合はnull
 */
export function getItem<T>(key: string): T | null {
  try {
    const serialized = localStorage.getItem(key);
    if (serialized === null) {
      return null;
    }
    return JSON.parse(serialized) as T;
  } catch (error) {
    console.error(`Failed to load from localStorage (key: ${key}):`, error);
    return null;
  }
}

/**
 * ローカルストレージからアイテムを削除
 * 
 * @param key - ストレージキー
 */
export function removeItem(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error(`Failed to remove from localStorage (key: ${key}):`, error);
  }
}

/**
 * ローカルストレージをクリア
 */
export function clear(): void {
  try {
    localStorage.clear();
  } catch (error) {
    console.error('Failed to clear localStorage:', error);
  }
}

/**
 * ローカルストレージにキーが存在するか確認
 * 
 * @param key - ストレージキー
 * @returns 存在する場合はtrue
 */
export function hasItem(key: string): boolean {
  try {
    return localStorage.getItem(key) !== null;
  } catch (error) {
    console.error(`Failed to check localStorage (key: ${key}):`, error);
    return false;
  }
}

/**
 * ローカルストレージの全キーを取得
 * 
 * @returns キーの配列
 */
export function getAllKeys(): string[] {
  try {
    const keys: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        keys.push(key);
      }
    }
    return keys;
  } catch (error) {
    console.error('Failed to get all keys from localStorage:', error);
    return [];
  }
}

/**
 * プレフィックスに一致するキーをすべて削除
 * 
 * @param prefix - キーのプレフィックス
 */
export function removeByPrefix(prefix: string): void {
  try {
    const keysToRemove = getAllKeys().filter(key => key.startsWith(prefix));
    keysToRemove.forEach(key => localStorage.removeItem(key));
  } catch (error) {
    console.error(`Failed to remove items by prefix (${prefix}):`, error);
  }
}

/**
 * ユーザー設定キー
 */
export const USER_SETTINGS_KEY = 'websys:user:settings';

/**
 * テーマキー
 */
export const THEME_KEY = 'websys:theme';

/**
 * 言語キー
 */
export const LANGUAGE_KEY = 'websys:language';

/**
 * テーマを保存
 * 
 * @param theme - テーマ（"light" or "dark"）
 */
export function saveTheme(theme: 'light' | 'dark'): void {
  setItem(THEME_KEY, theme);
}

/**
 * テーマを取得
 * 
 * @returns テーマ、未設定の場合は "light"
 */
export function getTheme(): 'light' | 'dark' {
  return getItem<'light' | 'dark'>(THEME_KEY) ?? 'light';
}

/**
 * 言語を保存
 * 
 * @param language - 言語コード（"ja" or "en"）
 */
export function saveLanguage(language: string): void {
  setItem(LANGUAGE_KEY, language);
}

/**
 * 言語を取得
 * 
 * @returns 言語コード、未設定の場合は "ja"
 */
export function getLanguage(): string {
  return getItem<string>(LANGUAGE_KEY) ?? 'ja';
}
