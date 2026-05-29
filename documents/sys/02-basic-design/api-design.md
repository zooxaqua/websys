# API設計書（システム共通基盤）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | システム共通基盤（sys） |
| 工程 | 工程2: 基本設計 |

---

## 1. API概要

### 1.1 基本仕様

| 項目 | 仕様 |
|------|------|
| **プロトコル** | HTTP/1.1, HTTPS |
| **データフォーマット** | JSON |
| **文字エンコーディング** | UTF-8 |
| **認証方式** | JWT（httpOnly Cookie） |
| **Cookie名** | `auth_token` |
| **ベースURL（開発）** | `http://localhost:8000` |
| **ベースURL（本番）** | `https://<domain>` |

### 1.2 共通HTTPヘッダー

**リクエスト**：

```
Content-Type: application/json
Accept: application/json
Cookie: auth_token=<JWT>
```

**レスポンス**：

```
Content-Type: application/json; charset=utf-8
X-Request-ID: <uuid>
```

### 1.3 共通エラーレスポンス

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": {}
  }
}
```

---

## 2. 認証API

### API-SYS-001: ログイン

**エンドポイント**: `POST /api/sys/auth/login`

**説明**: ユーザー名とパスワードでログインし、JWT Cookieを発行する

**認証**: 不要

**リクエスト**:

```json
{
  "username": "admin",
  "password": "password123"
}
```

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "user": {
    "id": "user_001",
    "username": "admin",
    "displayName": "管理者",
    "role": "admin",
    "email": "admin@example.com"
  }
}
```

**Set-Cookie ヘッダー**:

```
Set-Cookie: auth_token=<JWT>; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 401 | `AUTH_INVALID_CREDENTIALS` | ユーザー名またはパスワードが正しくありません |
| 400 | `VALIDATION_ERROR` | リクエストパラメータが不正です |

---

### API-SYS-002: ログアウト

**エンドポイント**: `POST /api/sys/auth/logout`

**説明**: セッションを破棄し、JWT Cookieを削除する

**認証**: 必要

**リクエスト**: なし

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "ログアウトしました"
}
```

**Set-Cookie ヘッダー**:

```
Set-Cookie: auth_token=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0
```

---

### API-SYS-003: 現在のユーザー情報取得

**エンドポイント**: `GET /api/sys/auth/me`

**説明**: ログイン中のユーザー情報を取得する

**認証**: 必要

**リクエスト**: なし

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "user_001",
  "username": "admin",
  "displayName": "管理者",
  "role": "admin",
  "email": "admin@example.com",
  "createdAt": "2026-05-01T10:00:00Z",
  "lastLogin": "2026-05-28T09:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 401 | `AUTH_TOKEN_EXPIRED` | セッションの有効期限が切れています |
| 401 | `AUTH_INVALID_TOKEN` | 認証トークンが無効です |

---

### API-SYS-004: パスワード変更

**エンドポイント**: `PUT /api/sys/auth/password`

**説明**: 自分のパスワードを変更する

**認証**: 必要

**リクエスト**:

```json
{
  "currentPassword": "old_password",
  "newPassword": "new_password"
}
```

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "パスワードを変更しました"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 401 | `AUTH_INVALID_CREDENTIALS` | 現在のパスワードが正しくありません |
| 400 | `VALIDATION_ERROR` | 新しいパスワードは8文字以上である必要があります |

---

## 3. ユーザー管理API

### API-SYS-010: ユーザー一覧取得

**エンドポイント**: `GET /api/sys/users`

**説明**: 全ユーザーの一覧を取得する（管理者のみ）

**認証**: 必要（管理者権限）

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `role` | string | No | ロールでフィルタ（`admin`, `user`） |
| `limit` | integer | No | 取得件数（デフォルト: 100） |
| `offset` | integer | No | オフセット（デフォルト: 0） |

**レスポンス（成功: 200 OK）**:

```json
{
  "users": [
    {
      "id": "user_001",
      "username": "admin",
      "displayName": "管理者",
      "role": "admin",
      "email": "admin@example.com",
      "createdAt": "2026-05-01T10:00:00Z",
      "lastLogin": "2026-05-28T09:00:00Z"
    },
    {
      "id": "user_002",
      "username": "user1",
      "displayName": "ユーザー1",
      "role": "user",
      "email": "user1@example.com",
      "createdAt": "2026-05-10T12:00:00Z",
      "lastLogin": "2026-05-27T15:30:00Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |

---

### API-SYS-011: ユーザー詳細取得

**エンドポイント**: `GET /api/sys/users/{user_id}`

**説明**: 特定ユーザーの詳細情報を取得する（管理者のみ）

**認証**: 必要（管理者権限）

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `user_id` | string | ユーザーID |

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "user_001",
  "username": "admin",
  "displayName": "管理者",
  "role": "admin",
  "email": "admin@example.com",
  "createdAt": "2026-05-01T10:00:00Z",
  "lastLogin": "2026-05-28T09:00:00Z",
  "metadata": {
    "department": "システム管理部",
    "phone": "090-1234-5678"
  }
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `USER_NOT_FOUND` | ユーザーが見つかりません |
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |

---

### API-SYS-012: ユーザー登録

**エンドポイント**: `POST /api/sys/users`

**説明**: 新しいユーザーを登録する（管理者のみ）

**認証**: 必要（管理者権限）

**リクエスト**:

```json
{
  "username": "user2",
  "password": "password123",
  "displayName": "ユーザー2",
  "role": "user",
  "email": "user2@example.com",
  "metadata": {
    "department": "営業部"
  }
}
```

**レスポンス（成功: 201 Created）**:

```json
{
  "id": "user_003",
  "username": "user2",
  "displayName": "ユーザー2",
  "role": "user",
  "email": "user2@example.com",
  "createdAt": "2026-05-28T10:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 409 | `USER_ALREADY_EXISTS` | ユーザー名が既に存在します |
| 400 | `VALIDATION_ERROR` | パスワードは8文字以上である必要があります |
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |

---

### API-SYS-013: ユーザー更新

**エンドポイント**: `PUT /api/sys/users/{user_id}`

**説明**: ユーザー情報を更新する（管理者のみ）

**認証**: 必要（管理者権限）

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `user_id` | string | ユーザーID |

**リクエスト**:

```json
{
  "displayName": "ユーザー2（更新）",
  "role": "admin",
  "email": "user2_updated@example.com",
  "metadata": {
    "department": "営業部",
    "phone": "090-9876-5432"
  }
}
```

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "user_003",
  "username": "user2",
  "displayName": "ユーザー2（更新）",
  "role": "admin",
  "email": "user2_updated@example.com",
  "updatedAt": "2026-05-28T11:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `USER_NOT_FOUND` | ユーザーが見つかりません |
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |

---

### API-SYS-014: ユーザー削除

**エンドポイント**: `DELETE /api/sys/users/{user_id}`

**説明**: ユーザーを削除する（管理者のみ）

**認証**: 必要（管理者権限）

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `user_id` | string | ユーザーID |

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "ユーザーを削除しました"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `USER_NOT_FOUND` | ユーザーが見つかりません |
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |
| 400 | `VALIDATION_ERROR` | 自分自身を削除することはできません |

---

## 4. アプリ管理API

### API-SYS-020: アプリ一覧取得

**エンドポイント**: `GET /api/sys/apps`

**説明**: 登録済みアプリの一覧を取得する

**認証**: 必要

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `enabled` | boolean | No | 有効化状態でフィルタ（`true`, `false`） |

**レスポンス（成功: 200 OK）**:

```json
{
  "apps": [
    {
      "id": "todo-app",
      "name": "TODO管理",
      "version": "1.0.0",
      "description": "タスク管理アプリケーション",
      "icon": "/apps/todo-app/icon.png",
      "entryPoint": "/apps/todo-app/",
      "enabled": true,
      "author": "System Team",
      "lastUpdated": "2026-05-28T10:00:00Z"
    },
    {
      "id": "calendar-app",
      "name": "カレンダー",
      "version": "1.0.0",
      "description": "スケジュール管理アプリケーション",
      "icon": "/apps/calendar-app/icon.png",
      "entryPoint": "/apps/calendar-app/",
      "enabled": false,
      "author": "System Team",
      "lastUpdated": "2026-05-28T10:00:00Z"
    }
  ],
  "total": 2
}
```

---

### API-SYS-021: アプリ詳細取得

**エンドポイント**: `GET /api/sys/apps/{app_id}`

**説明**: 特定アプリの詳細情報を取得する

**認証**: 必要

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `app_id` | string | アプリID（manifest.jsonの `name`） |

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "todo-app",
  "name": "TODO管理",
  "version": "1.0.0",
  "description": "タスク管理アプリケーション",
  "icon": "/apps/todo-app/icon.png",
  "entryPoint": "/apps/todo-app/",
  "apiPrefix": "/api/todo-app",
  "enabled": true,
  "author": "System Team",
  "requiredPermissions": ["read", "write"],
  "dependencies": [],
  "manifest": {
    "name": "todo-app",
    "displayName": "TODO管理",
    "version": "1.0.0",
    "description": "タスク管理アプリケーション",
    "entryPoint": "/apps/todo-app/",
    "apiPrefix": "/api/todo-app",
    "icon": "icon.png",
    "author": "System Team",
    "requiredPermissions": ["read", "write"],
    "dependencies": []
  },
  "lastUpdated": "2026-05-28T10:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `APP_NOT_FOUND` | アプリが見つかりません |

---

### API-SYS-022: アプリ有効化

**エンドポイント**: `POST /api/sys/apps/{app_id}/enable`

**説明**: アプリを有効化する（管理者のみ）

**認証**: 必要（管理者権限）

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `app_id` | string | アプリID |

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "アプリを有効化しました",
  "app": {
    "id": "todo-app",
    "name": "TODO管理",
    "enabled": true
  }
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `APP_NOT_FOUND` | アプリが見つかりません |
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |
| 400 | `APP_ALREADY_ENABLED` | アプリは既に有効化されています |

---

### API-SYS-023: アプリ無効化

**エンドポイント**: `POST /api/sys/apps/{app_id}/disable`

**説明**: アプリを無効化する（管理者のみ）

**認証**: 必要（管理者権限）

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `app_id` | string | アプリID |

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "アプリを無効化しました",
  "app": {
    "id": "todo-app",
    "name": "TODO管理",
    "enabled": false
  }
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `APP_NOT_FOUND` | アプリが見つかりません |
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |
| 400 | `APP_ALREADY_DISABLED` | アプリは既に無効化されています |

---

### API-SYS-024: アプリ再読み込み

**エンドポイント**: `POST /api/sys/apps/reload`

**説明**: apps/ディレクトリを再スキャンし、manifest.jsonを再読み込みする（管理者のみ）

**認証**: 必要（管理者権限）

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "アプリを再読み込みしました",
  "apps": [
    {
      "id": "todo-app",
      "name": "TODO管理",
      "status": "loaded"
    },
    {
      "id": "calendar-app",
      "name": "カレンダー",
      "status": "loaded"
    }
  ]
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |

---

## 5. 通知API

### API-SYS-030: 通知送信

**エンドポイント**: `POST /api/sys/notifications`

**説明**: ユーザーに通知を送信する（SSE経由で配信）

**認証**: 必要

**リクエスト**:

```json
{
  "userId": "user_001",
  "type": "info",
  "title": "通知タイトル",
  "message": "通知メッセージ",
  "data": {
    "url": "/apps/todo-app/"
  }
}
```

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "通知を送信しました",
  "notificationId": "notif_12345"
}
```

**通知タイプ**:

| タイプ | 説明 |
|-------|------|
| `info` | 情報通知（青） |
| `success` | 成功通知（緑） |
| `warning` | 警告通知（黄） |
| `error` | エラー通知（赤） |

---

### API-SYS-031: 通知ストリーム（SSE）

**エンドポイント**: `GET /api/sys/notifications/stream`

**説明**: リアルタイム通知をSSEで受信する

**認証**: 必要

**レスポンス形式**（text/event-stream）:

```
event: notification
data: {"id": "notif_12345", "type": "info", "title": "通知タイトル", "message": "通知メッセージ", "timestamp": "2026-05-28T10:00:00Z"}

event: notification
data: {"id": "notif_12346", "type": "success", "title": "成功", "message": "処理が完了しました", "timestamp": "2026-05-28T10:01:00Z"}

event: ping
data: {"timestamp": "2026-05-28T10:02:00Z"}
```

**接続維持**:
- 30秒ごとに `ping` イベントを送信
- クライアント切断時は自動的にストリームを終了

**クライアント実装例**:

```typescript
const eventSource = new EventSource('/api/sys/notifications/stream');

eventSource.addEventListener('notification', (event) => {
  const notification = JSON.parse(event.data);
  showNotification(notification);
});

eventSource.addEventListener('ping', (event) => {
  console.log('Connection alive:', event.data);
});

eventSource.addEventListener('error', (error) => {
  console.error('SSE error:', error);
  eventSource.close();
});
```

---

## 6. システム設定API

### API-SYS-040: システム設定取得

**エンドポイント**: `GET /api/sys/config`

**説明**: システム全体の設定を取得する（管理者のみ）

**認証**: 必要（管理者権限）

**レスポンス（成功: 200 OK）**:

```json
{
  "system": {
    "name": "Webシステム",
    "version": "1.0.0",
    "environment": "production"
  },
  "auth": {
    "jwtExpiration": 86400,
    "sessionTimeout": 3600,
    "passwordMinLength": 8
  },
  "apps": {
    "autoReload": false
  }
}
```

---

### API-SYS-041: システム設定更新

**エンドポイント**: `PUT /api/sys/config`

**説明**: システム設定を更新する（管理者のみ）

**認証**: 必要（管理者権限）

**リクエスト**:

```json
{
  "auth": {
    "jwtExpiration": 172800,
    "sessionTimeout": 7200
  }
}
```

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "システム設定を更新しました",
  "config": {
    "auth": {
      "jwtExpiration": 172800,
      "sessionTimeout": 7200
    }
  }
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 403 | `AUTH_INSUFFICIENT_PERMISSIONS` | 管理者権限が必要です |
| 400 | `VALIDATION_ERROR` | 設定値が不正です |

---

## 7. ヘルスチェックAPI

### API-SYS-050: ヘルスチェック

**エンドポイント**: `GET /api/sys/health`

**説明**: システムの稼働状態を確認する

**認証**: 不要

**レスポンス（成功: 200 OK）**:

```json
{
  "status": "healthy",
  "timestamp": "2026-05-28T10:00:00Z",
  "version": "1.0.0",
  "components": {
    "api": "healthy",
    "database": "healthy",
    "apps": "healthy"
  }
}
```

**ステータス**:

| ステータス | 説明 |
|-----------|------|
| `healthy` | 正常 |
| `degraded` | 一部機能が低下 |
| `unhealthy` | 異常 |

---

## 8. API実装例

### 8.1 FastAPI ルーター構成

```python
from fastapi import APIRouter

# 認証API
auth_router = APIRouter(prefix="/api/sys/auth", tags=["auth"])

@auth_router.post("/login")
async def login(credentials: LoginRequest):
    # 実装

@auth_router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    # 実装

@auth_router.get("/me")
async def get_current_user_info(user: User = Depends(get_current_user)):
    # 実装

# ユーザー管理API
users_router = APIRouter(prefix="/api/sys/users", tags=["users"])

@users_router.get("/")
async def list_users(user: User = Depends(require_admin)):
    # 実装

@users_router.post("/")
async def create_user(data: CreateUserRequest, user: User = Depends(require_admin)):
    # 実装

# アプリ管理API
apps_router = APIRouter(prefix="/api/sys/apps", tags=["apps"])

@apps_router.get("/")
async def list_apps(user: User = Depends(get_current_user)):
    # 実装

@apps_router.post("/{app_id}/enable")
async def enable_app(app_id: str, user: User = Depends(require_admin)):
    # 実装

# 通知API
notifications_router = APIRouter(prefix="/api/sys/notifications", tags=["notifications"])

@notifications_router.get("/stream")
async def notification_stream(request: Request, user: User = Depends(get_current_user)):
    # SSE実装
    pass
```

### 8.2 認証ミドルウェア

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    # Cookie からJWT取得
    token = request.cookies.get("auth_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "AUTH_INVALID_TOKEN", "message": "認証トークンがありません"}}
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401)
        
        # DAL経由でユーザー取得
        user = await dal.get("users", user_id)
        
        if not user:
            raise HTTPException(status_code=401)
        
        return User(**user)
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "AUTH_INVALID_TOKEN", "message": "認証トークンが無効です"}}
        )

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "AUTH_INSUFFICIENT_PERMISSIONS", "message": "管理者権限が必要です"}}
        )
    return user
```

---

## 関連ドキュメント

- [システムアーキテクチャ設計書](./architecture.md)
- [画面設計書](./screen-design.md)
- [manifest.jsonスキーマ](./manifest-schema.md)
- [工程1: 要件定義](../01-requirements/)
