/**
 * Fetchユーティリティ
 * 
 * システム共通基盤のAPIアクセス用fetch関数を提供します。
 * - 自動エラーハンドリング
 * - httpOnly Cookieによる認証
 * - レスポンス型定義
 */

/**
 * APIエラーレスポンス型
 */
export interface APIError {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

/**
 * Fetchオプション型
 */
export interface FetchOptions extends RequestInit {
  skipErrorHandling?: boolean;
}

/**
 * APIリクエストを実行
 * 
 * @param url - リクエストURL（相対パスまたは絶対パス）
 * @param options - Fetchオプション
 * @returns レスポンスデータ
 * @throws APIError エラー時にエラーオブジェクトをスロー
 */
export async function apiFetch<T = unknown>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  const { skipErrorHandling = false, ...fetchOptions } = options;

  // デフォルトオプション
  const defaultOptions: RequestInit = {
    credentials: 'include', // httpOnly Cookie送信
    headers: {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    },
  };

  // オプションをマージ
  const mergedOptions = { ...defaultOptions, ...fetchOptions };

  try {
    const response = await fetch(url, mergedOptions);

    // レスポンスがJSONでない場合（204 No Contentなど）
    if (response.status === 204) {
      return undefined as T;
    }

    // JSONパース
    const data = await response.json();

    // エラーレスポンスの場合
    if (!response.ok) {
      if (skipErrorHandling) {
        throw data;
      }
      
      // エラーハンドリング
      handleAPIError(response.status, data);
      throw data; // handleAPIErrorでthrowされない場合
    }

    return data as T;
  } catch (error) {
    if (skipErrorHandling) {
      throw error;
    }
    
    // ネットワークエラーなど
    if (error instanceof TypeError) {
      console.error('Network error:', error);
      throw {
        error: {
          code: 'ERR-SYS-NET-001',
          message: 'ネットワークエラーが発生しました',
          details: { originalError: error.message },
        },
      };
    }
    
    throw error;
  }
}

/**
 * APIエラーをハンドリング
 * 
 * @param status - HTTPステータスコード
 * @param errorData - エラーデータ
 */
function handleAPIError(status: number, errorData: APIError): void {
  const error = errorData.error;

  // 認証エラー（401）の場合はログインページにリダイレクト
  if (status === 401) {
    console.warn('Authentication error:', error.message);
    // セッション切れの場合はログインページへ
    if (error.code === 'ERR-SYS-AUTH-003' || error.code === 'ERR-SYS-AUTH-004') {
      window.location.href = '/login';
    }
    return;
  }

  // 権限エラー（403）
  if (status === 403) {
    console.warn('Authorization error:', error.message);
    alert(error.message);
    return;
  }

  // その他のエラーはコンソールに出力
  console.error(`API Error [${error.code}]:`, error.message, error.details);
}

/**
 * GETリクエスト
 * 
 * @param url - リクエストURL
 * @param options - Fetchオプション
 * @returns レスポンスデータ
 */
export async function get<T = unknown>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  return apiFetch<T>(url, { ...options, method: 'GET' });
}

/**
 * POSTリクエスト
 * 
 * @param url - リクエストURL
 * @param body - リクエストボディ
 * @param options - Fetchオプション
 * @returns レスポンスデータ
 */
export async function post<T = unknown>(
  url: string,
  body: unknown,
  options: FetchOptions = {}
): Promise<T> {
  return apiFetch<T>(url, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/**
 * PUTリクエスト
 * 
 * @param url - リクエストURL
 * @param body - リクエストボディ
 * @param options - Fetchオプション
 * @returns レスポンスデータ
 */
export async function put<T = unknown>(
  url: string,
  body: unknown,
  options: FetchOptions = {}
): Promise<T> {
  return apiFetch<T>(url, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

/**
 * DELETEリクエスト
 * 
 * @param url - リクエストURL
 * @param options - Fetchオプション
 * @returns レスポンスデータ
 */
export async function del<T = unknown>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  return apiFetch<T>(url, { ...options, method: 'DELETE' });
}
