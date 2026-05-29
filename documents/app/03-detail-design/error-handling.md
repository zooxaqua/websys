# エラーハンドリング詳細設計書（TODOアプリ）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | TODOアプリ（app） |
| 工程 | 工程3: 詳細設計 |

---

## 1. エラーコード体系

### 1.1 エラーコード命名規則

**形式**: `ERR-TODO-<NUMBER>`

| 部分 | 説明 | 例 |
|------|------|-----|
| `ERR` | プレフィックス（固定） | `ERR` |
| `TODO` | カテゴリ（TODOアプリ） | `TODO` |
| `NUMBER` | 連番（3桁） | `001`, `002`, `003` |

**例**:
- `ERR-TODO-001`: TODO未検出
- `ERR-TODO-002`: TODOアクセス権限なし
- `ERR-TODO-003`: タイトル必須

---

### 1.2 HTTPステータスコードとの対応

| HTTPステータス | 用途 | 例 |
|---------------|------|-----|
| `200 OK` | 成功 | — |
| `201 Created` | TODO作成成功 | TODO追加成功 |
| `400 Bad Request` | リクエストエラー | バリデーション失敗 |
| `401 Unauthorized` | 認証エラー | JWT無効（システム共通基盤） |
| `403 Forbidden` | 認可エラー | 他ユーザーのTODOへのアクセス |
| `404 Not Found` | リソース未検出 | TODOが見つからない |
| `500 Internal Server Error` | サーバーエラー | 予期しないエラー |

---

## 2. エラーコード一覧

### 2.1 TODOエラー（ERR-TODO-XXX）

| エラーコード | HTTPステータス | メッセージ | 説明 | 発生場所 |
|------------|---------------|-----------|------|---------|
| `ERR-TODO-001` | 404 | TODOが見つかりません | TODO ID未検出 | `TodoService.get_todo()` |
| `ERR-TODO-002` | 403 | このTODOにアクセスする権限がありません | 他ユーザーのTODOへのアクセス | `TodoService.get_todo()` |
| `ERR-TODO-003` | 400 | タイトルは必須です | タイトル未入力 | `TodoService.validate_todo_data()` |
| `ERR-TODO-004` | 400 | タイトルは100文字以内である必要があります | タイトル長すぎ | `TodoService.validate_todo_data()` |
| `ERR-TODO-005` | 400 | 説明は500文字以内である必要があります | 説明長すぎ | `TodoService.validate_todo_data()` |
| `ERR-TODO-006` | 400 | 期限の形式が不正です | dueDate形式エラー | `TodoService.validate_todo_data()` |

**レスポンス例**:

```json
{
  "error": {
    "code": "ERR-TODO-001",
    "message": "TODOが見つかりません",
    "details": {
      "todoId": "todo_999"
    },
    "timestamp": "2026-05-28T10:00:00Z",
    "path": "/api/todo-app/todos/todo_999",
    "requestId": "req_12345"
  }
}
```

---

## 3. エラーレスポンス仕様

### 3.1 標準エラーレスポンス形式

TODOアプリのエラーレスポンスは、システム共通基盤と同じ形式を使用します。

```json
{
  "error": {
    "code": "ERR-TODO-003",
    "message": "タイトルは必須です",
    "details": {},
    "timestamp": "2026-05-28T10:00:00Z",
    "path": "/api/todo-app/todos",
    "requestId": "req_12345"
  }
}
```

**フィールド定義**:

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `error.code` | string | Yes | エラーコード（`ERR-TODO-XXX`） |
| `error.message` | string | Yes | ユーザー向けエラーメッセージ |
| `error.details` | object | No | 詳細情報（フィールド名・値など） |
| `error.timestamp` | string | No | エラー発生日時（ISO8601） |
| `error.path` | string | No | リクエストパス |
| `error.requestId` | string | No | リクエストID（ログ追跡用） |

---

### 3.2 FastAPI Exception Handler

TODOアプリは、システム共通基盤の Exception Handler を使用します。

**ファイル**: `backend/app/sys/core/exception_handlers.py`（システム共通基盤）

TODOアプリのAPI実装時に、以下のように `HTTPException` を使用します：

```python
from fastapi import HTTPException, status

# TODO未検出
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="ERR-TODO-001"
)

# TODOアクセス権限なし
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="ERR-TODO-002"
)

# タイトル必須
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="ERR-TODO-003"
)
```

---

## 4. ログ出力仕様

### 4.1 ログレベル

TODOアプリは、システム共通基盤のログレベルを使用します。

| レベル | 用途 | 例 |
|--------|------|-----|
| `DEBUG` | デバッグ情報 | 変数値・処理フロー |
| `INFO` | 一般情報 | TODO作成・更新・削除 |
| `WARNING` | 警告 | バリデーション失敗 |
| `ERROR` | エラー | TODO取得失敗・権限エラー |
| `CRITICAL` | 致命的エラー | DAL接続不可 |

---

### 4.2 ログフォーマット

システム共通基盤と同じフォーマットを使用します。

```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [request_id] [module] message
```

**例**:

```
[2026-05-28 10:00:00] [INFO] [req_12345] [todo_service] Todo created: todo_001 by user_001
[2026-05-28 10:01:00] [ERROR] [req_12346] [todo_service] ERR-TODO-001: Todo not found: todo_999
[2026-05-28 10:02:00] [WARNING] [req_12347] [todo_service] ERR-TODO-003: Title is required
```

---

### 4.3 ログ設定

TODOアプリは、システム共通基盤のログ設定を使用します。

**ファイル**: `backend/app/sys/core/logging_config.py`（システム共通基盤）

TODOアプリのログは以下のファイルに出力されます：
- `backend/logs/app.log` — 全ログ
- `backend/logs/error.log` — エラーログのみ

---

## 5. エラーハンドリング実装例

### 5.1 TODO取得時のエラーハンドリング

**ファイル**: `apps/todo-app/backend/app/services/todo_service.py`

```python
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

def get_todo(self, todo_id: str, user_id: str) -> Todo:
    """TODO詳細を取得（権限チェック）"""
    todo_data = self.dal.find_one({"id": todo_id})
    
    # TODO未検出
    if not todo_data:
        logger.warning(f"Todo not found: {todo_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ERR-TODO-001"
        )
    
    # 権限チェック
    if todo_data["userId"] != user_id:
        logger.warning(f"Access denied: user {user_id} tried to access todo {todo_id} owned by {todo_data['userId']}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="ERR-TODO-002"
        )
    
    logger.info(f"Todo retrieved: {todo_id} by user {user_id}")
    return Todo.from_dict(todo_data)
```

---

### 5.2 TODO作成時のエラーハンドリング

**ファイル**: `apps/todo-app/backend/app/services/todo_service.py`

```python
import logging
from fastapi import HTTPException, status
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def create_todo(
    self,
    user_id: str,
    title: str,
    description: str = "",
    due_date: str | None = None
) -> Todo:
    """TODOを作成"""
    # バリデーション
    is_valid, error_message = self.validate_todo_data({
        "title": title,
        "description": description,
        "dueDate": due_date
    })
    if not is_valid:
        logger.warning(f"Validation error: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # TODO作成
    todo = Todo(
        id=str(uuid.uuid4()),
        userId=user_id,
        title=title,
        description=description,
        dueDate=due_date,
        completed=False,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    
    try:
        self.dal.insert(todo.to_dict())
        logger.info(f"Todo created: {todo.id} by user {user_id}")
        return todo
    except Exception as e:
        logger.exception(f"Failed to create todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ERR-SYS-SERV-002"  # システム共通基盤のエラーコード
        )
```

---

### 5.3 バリデーションエラーハンドリング

**ファイル**: `apps/todo-app/backend/app/services/todo_service.py`

```python
def validate_todo_data(self, data: dict) -> tuple[bool, str]:
    """TODOデータをバリデーション"""
    # タイトルチェック
    title = data.get("title", "")
    if "title" in data:
        if not title or title.strip() == "":
            return False, "ERR-TODO-003"
        if len(title) > 100:
            return False, "ERR-TODO-004"
    
    # 説明チェック
    description = data.get("description", "")
    if description and len(description) > 500:
        return False, "ERR-TODO-005"
    
    # 期限チェック
    due_date = data.get("dueDate")
    if due_date:
        try:
            datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False, "ERR-TODO-006"
    
    return True, ""
```

---

## 6. エラーハンドリングのベストプラクティス

### 6.1 原則

| 原則 | 説明 |
|------|------|
| **明確なエラーメッセージ** | ユーザーが理解できる日本語メッセージ |
| **エラーコードの一意性** | 同じエラーコードを複数の箇所で使わない |
| **詳細情報の提供** | `details` フィールドで追加情報を提供 |
| **ログ出力** | 全てのエラーをログに記録 |
| **セキュリティ** | 機密情報（TODO内容）を不必要にログに出力しない |
| **システム共通基盤との統一** | エラーレスポンス形式・ログ形式を統一 |

---

### 6.2 実装例

**良い例**:

```python
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

def delete_todo(self, todo_id: str, user_id: str) -> bool:
    # 権限チェック
    self.get_todo(todo_id, user_id)  # 存在確認 + 権限チェック
    
    try:
        result = self.dal.delete(todo_id)
        logger.info(f"Todo deleted: {todo_id} by user {user_id}")
        return result
    except Exception as e:
        logger.exception(f"Failed to delete todo: {todo_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ERR-SYS-SERV-002"
        )
```

**悪い例**:

```python
# エラーメッセージが不明瞭
raise HTTPException(status_code=404, detail="Not found")

# エラーコードなし
raise HTTPException(status_code=404, detail="TODOが見つかりません")

# 機密情報をログ出力
logger.error(f"Todo not found: {todo_id}, title: {todo_title}, description: {todo_description}")
```

---

## 7. エラーメッセージ一覧表

### 7.1 日本語メッセージ

| エラーコード | メッセージ |
|------------|-----------|
| `ERR-TODO-001` | TODOが見つかりません |
| `ERR-TODO-002` | このTODOにアクセスする権限がありません |
| `ERR-TODO-003` | タイトルは必須です |
| `ERR-TODO-004` | タイトルは100文字以内である必要があります |
| `ERR-TODO-005` | 説明は500文字以内である必要があります |
| `ERR-TODO-006` | 期限の形式が不正です |

---

### 7.2 多言語対応（将来）

将来的に英語などの多言語対応を行う場合、以下のような辞書を用意します：

**ファイル**: `apps/todo-app/backend/app/i18n/messages.json`

```json
{
  "ERR-TODO-001": {
    "ja": "TODOが見つかりません",
    "en": "Todo not found"
  },
  "ERR-TODO-002": {
    "ja": "このTODOにアクセスする権限がありません",
    "en": "Access denied to this todo"
  },
  "ERR-TODO-003": {
    "ja": "タイトルは必須です",
    "en": "Title is required"
  },
  "ERR-TODO-004": {
    "ja": "タイトルは100文字以内である必要があります",
    "en": "Title must be 100 characters or less"
  },
  "ERR-TODO-005": {
    "ja": "説明は500文字以内である必要があります",
    "en": "Description must be 500 characters or less"
  },
  "ERR-TODO-006": {
    "ja": "期限の形式が不正です",
    "en": "Invalid due date format"
  }
}
```

---

## 8. まとめ

### 8.1 エラーコード総数

| カテゴリ | エラーコード数 |
|---------|-------------|
| TODOエラー（`ERR-TODO-XXX`） | 6 |
| **合計** | **6** |

### 8.2 システム共通基盤との連携

- エラーレスポンス形式はシステム共通基盤と統一
- Exception Handler はシステム共通基盤を使用
- ログ設定はシステム共通基盤を使用
- サーバーエラー（500）はシステム共通基盤のエラーコード（`ERR-SYS-SERV-XXX`）を使用

### 8.3 次工程への引き継ぎ

- 工程4（コーディング）では、このエラーコード体系に基づいて実装
- 全てのAPIで `HTTPException` を使用してエラーを返す
- ログ出力は `logging` モジュールを使用
- バリデーションエラーは `validate_todo_data()` で一元管理

---

**トレーサビリティ**: この設計書は工程2の基本設計書（api-design.md）および工程3の `class-design.md`, `sequence-diagrams.md` に基づいています。
