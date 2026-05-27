# TypeScript コーディング規約

## tsconfig.json 必須設定

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "target": "ES2020",
    "module": "ESNext"
  }
}
```

## 命名規則

| 対象 | 規則 | 例 |
|------|------|-----|
| 型・インターフェース | PascalCase | `UserProfile`, `ApiResponse<T>` |
| 関数 | camelCase | `fetchUserData()` |
| 定数 | UPPER_SNAKE | `API_BASE_URL` |
| ファイル | kebab-case | `user-auth.ts` |

## `any` 型の禁止

```typescript
// NG
const data: any = await response.json();

// OK
interface UserResponse {
  id: string;
  username: string;
}
const data: UserResponse = await response.json();
```

## API コール規則

```typescript
// REST API 呼び出しの標準パターン
async function callApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    credentials: 'same-origin', // Cookie（JWT httpOnly）を自動送信
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const err = await response.json();
    throw new ApiError(err.error.code, err.error.message);
  }
  return response.json() as Promise<T>;
}
```

## セキュリティ規則

- JWT トークンを `localStorage` / `sessionStorage` に保存しない（httpOnly Cookie で管理）
- ユーザー入力を innerHTML に直接セットしない（XSS 防止）

```typescript
// NG
element.innerHTML = userInput;

// OK
element.textContent = userInput;
```

## SSE（Server-Sent Events）実装パターン

```typescript
function subscribeEvents(onMessage: (data: unknown) => void): () => void {
  const es = new EventSource('/api/events', { withCredentials: true });
  es.onmessage = (e) => onMessage(JSON.parse(e.data));
  es.onerror = () => console.error('SSE connection error');
  return () => es.close(); // cleanup
}
```
