# エラーハンドリング詳細設計書（システム共通基盤）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | システム共通基盤（sys） |
| 工程 | 工程3: 詳細設計 |

---

## 1. エラーコード体系

### 1.1 エラーコード命名規則

**形式**: `ERR-<CATEGORY>-<SUBCATEGORY>-<NUMBER>`

| 部分 | 説明 | 例 |
|------|------|-----|
| `ERR` | プレフィックス（固定） | `ERR` |
| `CATEGORY` | カテゴリ（3文字） | `SYS`（システム共通）, `APP`（アプリ） |
| `SUBCATEGORY` | サブカテゴリ（3〜4文字） | `AUTH`, `USER`, `APPS`, `NOTF` |
| `NUMBER` | 連番（3桁） | `001`, `002`, `003` |

**例**:
- `ERR-SYS-AUTH-001`: システム認証エラー1
- `ERR-SYS-USER-001`: システムユーザー管理エラー1
- `ERR-APP-TODO-001`: TODOアプリエラー1

---

### 1.2 HTTPステータスコードとの対応

| HTTPステータス | 用途 | 例 |
|---------------|------|-----|
| `200 OK` | 成功 | — |
| `201 Created` | リソース作成成功 | ユーザー登録成功 |
| `204 No Content` | 成功（レスポンスボディなし） | 削除成功 |
| `400 Bad Request` | リクエストエラー | バリデーション失敗 |
| `401 Unauthorized` | 認証エラー | JWT無効・期限切れ |
| `403 Forbidden` | 認可エラー | 権限不足 |
| `404 Not Found` | リソース未検出 | ユーザー・アプリが見つからない |
| `409 Conflict` | リソース競合 | ユーザー名重複 |
| `500 Internal Server Error` | サーバーエラー | 予期しないエラー |

---

## 2. エラーコード一覧

### 2.1 認証エラー（ERR-SYS-AUTH-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-SYS-AUTH-001` | 401 | ユーザー名またはパスワードが正しくありません | 認証失敗 | `AuthService.authenticate()` |
| `ERR-SYS-AUTH-002` | 401 | 認証トークンが無効です | JWT検証失敗 | `get_current_user()` |
| `ERR-SYS-AUTH-003` | 401 | セッションの有効期限が切れています | JWT期限切れ | `get_current_user()` |
| `ERR-SYS-AUTH-004` | 401 | 認証トークンが見つかりません | JWT Cookieなし | `get_current_user()` |
| `ERR-SYS-AUTH-005` | 401 | セッションが存在しません | セッションDB未検出 | `get_current_user()` |
| `ERR-SYS-AUTH-006` | 403 | 管理者権限が必要です | 管理者以外がアクセス | `get_current_admin_user()` |
| `ERR-SYS-AUTH-007` | 400 | 現在のパスワードが正しくありません | パスワード変更時の検証失敗 | `AuthService.change_password()` |
| `ERR-SYS-AUTH-008` | 400 | 新しいパスワードは8文字以上である必要があります | パスワード強度不足 | `AuthService.change_password()` |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-SYS-AUTH-001",
    "message": "ユーザー名またはパスワードが正しくありません",
    "details": {}
  }
}
```

---

### 2.2 ユーザー管理エラー（ERR-SYS-USER-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-SYS-USER-001` | 404 | ユーザーが見つかりません | ユーザーID未検出 | `UserService.get_user()` |
| `ERR-SYS-USER-002` | 409 | ユーザー名が既に存在します | ユーザー名重複 | `UserService.create_user()` |
| `ERR-SYS-USER-003` | 409 | メールアドレスが既に存在します | メールアドレス重複 | `UserService.create_user()` |
| `ERR-SYS-USER-004` | 400 | ユーザー名は3文字以上50文字以内である必要があります | バリデーション失敗 | `UserService.validate_user_data()` |
| `ERR-SYS-USER-005` | 400 | メールアドレスの形式が不正です | バリデーション失敗 | `UserService.validate_user_data()` |
| `ERR-SYS-USER-006` | 400 | ロールは "admin" または "user" である必要があります | バリデーション失敗 | `UserService.validate_user_data()` |
| `ERR-SYS-USER-007` | 400 | 自分自身を削除することはできません | 自己削除防止 | `UserService.delete_user()` |
| `ERR-SYS-USER-008` | 400 | 表示名は1文字以上100文字以内である必要があります | バリデーション失敗 | `UserService.validate_user_data()` |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-SYS-USER-002",
    "message": "ユーザー名が既に存在します",
    "details": {
      "field": "username",
      "value": "admin"
    }
  }
}
```

---

### 2.3 アプリ管理エラー（ERR-SYS-APPS-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-SYS-APPS-001` | 404 | アプリが見つかりません | アプリID未検出 | `AppService.get_app()` |
| `ERR-SYS-APPS-002` | 400 | アプリは既に有効化されています | 有効化済みアプリを再度有効化 | `AppService.enable_app()` |
| `ERR-SYS-APPS-003` | 400 | アプリは既に無効化されています | 無効化済みアプリを再度無効化 | `AppService.disable_app()` |
| `ERR-SYS-APPS-004` | 400 | manifest.jsonが見つかりません | manifestファイル未検出 | `AppService.scan_apps()` |
| `ERR-SYS-APPS-005` | 400 | manifest.jsonの形式が不正です | JSONパースエラー | `AppService.scan_apps()` |
| `ERR-SYS-APPS-006` | 400 | manifest.jsonに必須フィールドが不足しています | スキーマ検証失敗 | `AppService.validate_app_manifest()` |
| `ERR-SYS-APPS-007` | 403 | このアプリは無効化されています | 無効化アプリへのアクセス | ミドルウェア |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-SYS-APPS-006",
    "message": "manifest.jsonに必須フィールドが不足しています",
    "details": {
      "missingFields": ["name", "version"]
    }
  }
}
```

---

### 2.4 通知エラー（ERR-SYS-NOTF-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-SYS-NOTF-001` | 404 | 通知が見つかりません | 通知ID未検出 | `NotificationService.mark_as_read()` |
| `ERR-SYS-NOTF-002` | 403 | この通知にアクセスする権限がありません | 他ユーザーの通知へのアクセス | `NotificationService.mark_as_read()` |
| `ERR-SYS-NOTF-003` | 400 | 通知タイプは "info", "warning", "error", "success" のいずれかである必要があります | バリデーション失敗 | `NotificationService.create_notification()` |
| `ERR-SYS-NOTF-004` | 400 | タイトルは1文字以上200文字以内である必要があります | バリデーション失敗 | `NotificationService.create_notification()` |
| `ERR-SYS-NOTF-005` | 400 | メッセージは1文字以上1000文字以内である必要があります | バリデーション失敗 | `NotificationService.create_notification()` |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-SYS-NOTF-001",
    "message": "通知が見つかりません",
    "details": {
      "notificationId": "notif_999"
    }
  }
}
```

---

### 2.5 バリデーションエラー（ERR-SYS-VALD-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-SYS-VALD-001` | 400 | リクエストパラメータが不正です | 一般的なバリデーション失敗 | 各API |
| `ERR-SYS-VALD-002` | 400 | 必須フィールドが不足しています | 必須フィールド欠落 | 各API |
| `ERR-SYS-VALD-003` | 400 | フィールドの型が不正です | 型不一致（文字列期待→数値受信） | 各API |
| `ERR-SYS-VALD-004` | 400 | フィールドの値が範囲外です | 数値範囲・文字列長オーバー | 各API |
| `ERR-SYS-VALD-005` | 400 | 不正なJSON形式です | JSONパースエラー | ミドルウェア |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-SYS-VALD-002",
    "message": "必須フィールドが不足しています",
    "details": {
      "missingFields": ["username", "password"]
    }
  }
}
```

---

### 2.6 サーバーエラー（ERR-SYS-SERV-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-SYS-SERV-001` | 500 | 予期しないエラーが発生しました | 一般的なサーバーエラー | 例外ハンドラー |
| `ERR-SYS-SERV-002` | 500 | データベースエラーが発生しました | DB接続・読み書きエラー | DAL層 |
| `ERR-SYS-SERV-003` | 500 | ファイル操作エラーが発生しました | ファイル読み書きエラー | DAL層 |
| `ERR-SYS-SERV-004` | 500 | 設定ファイルの読み込みに失敗しました | config.json読み込み失敗 | 起動時 |
| `ERR-SYS-SERV-005` | 503 | サービスが利用できません | メンテナンス中 | ミドルウェア |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-SYS-SERV-001",
    "message": "予期しないエラーが発生しました",
    "details": {
      "requestId": "req_12345"
    }
  }
}
```

---

## 3. エラーレスポンス仕様

### 3.1 標準エラーレスポンス形式

```json
{
  "error": {
    "code": "ERR-SYS-AUTH-001",
    "message": "ユーザー名またはパスワードが正しくありません",
    "details": {},
    "timestamp": "2026-05-28T10:00:00Z",
    "path": "/api/sys/auth/login",
    "requestId": "req_12345"
  }
}
```

**フィールド定義**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `error.code` | string | Yes | エラーコード（`ERR-XXX-XXX-XXX`） |
| `error.message` | string | Yes | ユーザー向けエラーメッセージ |
| `error.details` | object | No | 詳細情報（フィールド名・値など） |
| `error.timestamp` | string | No | エラー発生日時（ISO8601） |
| `error.path` | string | No | リクエストパス |
| `error.requestId` | string | No | リクエストID（ログ追跡用） |

---

### 3.2 FastAPI Exception Handler

**ファイル**: `backend/app/sys/core/exception_handlers.py`

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTPException をエラーレスポンスに変換"""
    request_id = str(uuid.uuid4())
    error_response = {
        "error": {
            "code": exc.detail if isinstance(exc.detail, str) and exc.detail.startswith("ERR-") else "ERR-SYS-SERV-001",
            "message": exc.detail if isinstance(exc.detail, str) else "予期しないエラーが発生しました",
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path),
            "requestId": request_id
        }
    }
    
    # ログ出力
    logger.error(f"[{request_id}] HTTP {exc.status_code}: {exc.detail} (path: {request.url.path})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """バリデーションエラーをエラーレスポンスに変換"""
    request_id = str(uuid.uuid4())
    missing_fields = []
    invalid_fields = []
    
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])
        if error["type"] == "value_error.missing":
            missing_fields.append(field)
        else:
            invalid_fields.append({"field": field, "message": error["msg"]})
    
    error_response = {
        "error": {
            "code": "ERR-SYS-VALD-002" if missing_fields else "ERR-SYS-VALD-001",
            "message": "必須フィールドが不足しています" if missing_fields else "リクエストパラメータが不正です",
            "details": {
                "missingFields": missing_fields,
                "invalidFields": invalid_fields
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path),
            "requestId": request_id
        }
    }
    
    # ログ出力
    logger.warning(f"[{request_id}] Validation error: {error_response['error']['message']} (path: {request.url.path})")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """予期しないエラーをエラーレスポンスに変換"""
    request_id = str(uuid.uuid4())
    error_response = {
        "error": {
            "code": "ERR-SYS-SERV-001",
            "message": "予期しないエラーが発生しました",
            "details": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": str(request.url.path),
            "requestId": request_id
        }
    }
    
    # ログ出力（スタックトレース含む）
    logger.exception(f"[{request_id}] Unhandled exception: {str(exc)} (path: {request.url.path})")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response
    )
```

---

## 4. ログ出力仕様

### 4.1 ログレベル

| レベル | 用途 | 例 |
|--------|------|-----|
| `DEBUG` | デバッグ情報 | 変数値・処理フロー |
| `INFO` | 一般情報 | API呼び出し・ユーザーログイン |
| `WARNING` | 警告 | バリデーション失敗・非推奨機能の使用 |
| `ERROR` | エラー | API呼び出し失敗・認証エラー |
| `CRITICAL` | 致命的エラー | サーバー起動失敗・DB接続不可 |

---

### 4.2 ログフォーマット

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [request_id] [module] message
```

**例**:

```
[2026-05-28 10:00:00] [ERROR] [req_12345] [auth_service] ERR-SYS-AUTH-001: Authentication failed for user 'admin'
[2026-05-28 10:01:00] [INFO] [req_12346] [user_service] User 'user1' created successfully
[2026-05-28 10:02:00] [WARNING] [req_12347] [validation] ERR-SYS-VALD-002: Missing required fields: username, password
```

---

### 4.3 ログ設定

**ファイル**: `backend/app/sys/core/logging_config.py`

```python
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """ログ設定を初期化"""
    # ルートロガー設定
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # フォーマット
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # コンソール出力
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # ファイル出力（ローテーション）
    file_handler = RotatingFileHandler(
        'backend/logs/app.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # エラーログ専用ファイル
    error_handler = RotatingFileHandler(
        'backend/logs/error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
```

---

### 4.4 ログローテーション

| 項目 | 設定 |
|------|------|
| **ログファイル** | `backend/logs/app.log`, `backend/logs/error.log` |
| **最大ファイルサイズ** | 10MB |
| **世代管理** | 5世代 |
| **ローテーション方式** | サイズベース |
| **圧縮** | なし（将来対応） |

---

## 5. エラーハンドリングのベストプラクティス

### 5.1 原則

| 原則 | 説明 |
|------|------|
| **明確なエラーメッセージ** | ユーザーが理解できる日本語メッセージ |
| **エラーコードの一意性** | 同じエラーコードを複数の箇所で使わない |
| **詳細情報の提供** | `details` フィールドで追加情報を提供 |
| **ログ出力** | 全てのエラーをログに記録 |
| **セキュリティ** | 機密情報（パスワード・トークン）をログに出力しない |
| **スタックトレース** | 本番環境ではスタックトレースを含めない |

---

### 5.2 実装例

**良い例**:

```python
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

def get_user(user_id: str) -> User:
    user_data = user_dal.find_one({"id": user_id})
    if not user_data:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ERR-SYS-USER-001"
        )
    return User.from_dict(user_data)
```

**悪い例**:

```python
# エラーメッセージが不明瞭
raise HTTPException(status_code=404, detail="Not found")

# エラーコードなし
raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

# 機密情報をログ出力
logger.error(f"Authentication failed for user '{username}' with password '{password}'")
```

---

### 5.3 FastAPI での HTTPException 使用例

```python
from fastapi import HTTPException, status

# 認証エラー
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="ERR-SYS-AUTH-001"
)

# ユーザー未検出
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="ERR-SYS-USER-001"
)

# ユーザー名重複
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="ERR-SYS-USER-002"
)

# バリデーション失敗（Pydanticが自動的に処理）
# リクエストモデルで定義すればOK
```

---

## 6. まとめ

### 6.1 エラーコード総数

| カテゴリ | エラーコード数 |
|---------|-------------|
| 認証エラー（`ERR-SYS-AUTH-XXX`） | 8 |
| ユーザー管理エラー（`ERR-SYS-USER-XXX`） | 8 |
| アプリ管理エラー（`ERR-SYS-APPS-XXX`） | 7 |
| 通知エラー（`ERR-SYS-NOTF-XXX`） | 5 |
| バリデーションエラー（`ERR-SYS-VALD-XXX`） | 5 |
| サーバーエラー（`ERR-SYS-SERV-XXX`） | 5 |
| **合計** | **38** |

### 6.2 次工程への引き継ぎ

- 工程4（コーディング）では、このエラーコード体系に基づいて実装
- 全てのAPIで `HTTPException` を使用してエラーを返す
- Exception Handlerを `main.py` で登録
- ログ設定を起動時に初期化

---

**トレーサビリティ**: この設計書は工程2の基本設計書（api-design.md）および工程3の `class-design.md`, `sequence-diagrams.md` に基づいています。
