/**
 * バリデーションユーティリティ
 * 
 * フロントエンドでの入力バリデーション関数を提供します。
 * サーバー側のバリデーションと整合性を保ちます。
 */

/**
 * バリデーション結果型
 */
export interface ValidationResult {
  valid: boolean;
  message?: string;
}

/**
 * ユーザー名をバリデーション
 * 
 * 制約:
 * - 3〜50文字
 * - 英数字・アンダースコアのみ
 * 
 * @param username - ユーザー名
 * @returns バリデーション結果
 */
export function validateUsername(username: string): ValidationResult {
  if (!username) {
    return { valid: false, message: 'ユーザー名を入力してください' };
  }

  if (username.length < 3 || username.length > 50) {
    return { valid: false, message: 'ユーザー名は3文字以上50文字以内である必要があります' };
  }

  const usernameRegex = /^[a-zA-Z0-9_]+$/;
  if (!usernameRegex.test(username)) {
    return { valid: false, message: 'ユーザー名は英数字とアンダースコアのみ使用できます' };
  }

  return { valid: true };
}

/**
 * パスワードをバリデーション
 * 
 * 制約:
 * - 8文字以上
 * 
 * @param password - パスワード
 * @returns バリデーション結果
 */
export function validatePassword(password: string): ValidationResult {
  if (!password) {
    return { valid: false, message: 'パスワードを入力してください' };
  }

  if (password.length < 8) {
    return { valid: false, message: 'パスワードは8文字以上である必要があります' };
  }

  return { valid: true };
}

/**
 * メールアドレスをバリデーション
 * 
 * @param email - メールアドレス
 * @returns バリデーション結果
 */
export function validateEmail(email: string): ValidationResult {
  if (!email) {
    return { valid: false, message: 'メールアドレスを入力してください' };
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return { valid: false, message: 'メールアドレスの形式が不正です' };
  }

  return { valid: true };
}

/**
 * 表示名をバリデーション
 * 
 * 制約:
 * - 1〜100文字
 * 
 * @param displayName - 表示名
 * @returns バリデーション結果
 */
export function validateDisplayName(displayName: string): ValidationResult {
  if (!displayName) {
    return { valid: false, message: '表示名を入力してください' };
  }

  if (displayName.length < 1 || displayName.length > 100) {
    return { valid: false, message: '表示名は1文字以上100文字以内である必要があります' };
  }

  return { valid: true };
}

/**
 * ロールをバリデーション
 * 
 * 制約:
 * - "admin" または "user"
 * 
 * @param role - ロール
 * @returns バリデーション結果
 */
export function validateRole(role: string): ValidationResult {
  if (!role) {
    return { valid: false, message: 'ロールを選択してください' };
  }

  if (role !== 'admin' && role !== 'user') {
    return { valid: false, message: 'ロールは "admin" または "user" である必要があります' };
  }

  return { valid: true };
}

/**
 * 必須入力をバリデーション
 * 
 * @param value - 検証する値
 * @param fieldName - フィールド名
 * @returns バリデーション結果
 */
export function validateRequired(value: string | undefined | null, fieldName: string): ValidationResult {
  if (!value || value.trim() === '') {
    return { valid: false, message: `${fieldName}を入力してください` };
  }

  return { valid: true };
}

/**
 * 最小文字数をバリデーション
 * 
 * @param value - 検証する値
 * @param minLength - 最小文字数
 * @param fieldName - フィールド名
 * @returns バリデーション結果
 */
export function validateMinLength(value: string, minLength: number, fieldName: string): ValidationResult {
  if (value.length < minLength) {
    return { valid: false, message: `${fieldName}は${minLength}文字以上である必要があります` };
  }

  return { valid: true };
}

/**
 * 最大文字数をバリデーション
 * 
 * @param value - 検証する値
 * @param maxLength - 最大文字数
 * @param fieldName - フィールド名
 * @returns バリデーション結果
 */
export function validateMaxLength(value: string, maxLength: number, fieldName: string): ValidationResult {
  if (value.length > maxLength) {
    return { valid: false, message: `${fieldName}は${maxLength}文字以内である必要があります` };
  }

  return { valid: true };
}

/**
 * 複数のバリデーション結果を統合
 * 
 * @param results - バリデーション結果の配列
 * @returns 統合されたバリデーション結果
 */
export function combineValidationResults(results: ValidationResult[]): ValidationResult {
  const invalidResult = results.find(result => !result.valid);
  
  if (invalidResult) {
    return invalidResult;
  }

  return { valid: true };
}
