# データベーススキーマ設計書（TODOアプリ）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | TODOアプリ（app） |
| 工程 | 工程3: 詳細設計 |

---

## 1. データベース概要

### 1.1 現状（JSON DB）

| 項目 | 内容 |
|------|------|
| **形式** | JSONファイル |
| **配置** | `apps/todo-app/backend/data/` |
| **エンコーディング** | UTF-8 |
| **インデント** | 2スペース |
| **アクセス方法** | システム共通基盤の `JsonDAL` を継承した `TodoDAL` 経由 |

### 1.2 将来対応（RDB）

| 項目 | 内容 |
|------|------|
| **候補** | MySQL 8.0+, PostgreSQL 14+ |
| **移行方法** | システム共通基盤のDAL抽象化により透過的に切り替え |
| **テーブル設計** | JSON構造をそのままテーブルに変換 |
| **インデックス** | 主キー・外部キー・検索頻度の高いカラムに設定 |

---

## 2. JSON DB スキーマ（現状）

### 2.1 todos.json

**ファイルパス**: `apps/todo-app/backend/data/todos.json`

**説明**: TODO情報を格納

**構造**:

```json
{
  "todo_001": {
    "id": "todo_001",
    "userId": "user_001",
    "title": "プロジェクト計画書を作成",
    "description": "工程2の基本設計書を作成する",
    "dueDate": "2026-06-01T00:00:00Z",
    "completed": false,
    "createdAt": "2026-05-28T10:00:00Z",
    "updatedAt": "2026-05-28T10:00:00Z"
  },
  "todo_002": {
    "id": "todo_002",
    "userId": "user_001",
    "title": "テストコード作成",
    "description": "単体テストを作成する",
    "dueDate": "2026-06-05T00:00:00Z",
    "completed": true,
    "createdAt": "2026-05-28T11:00:00Z",
    "updatedAt": "2026-05-28T12:00:00Z"
  },
  "todo_003": {
    "id": "todo_003",
    "userId": "user_002",
    "title": "デプロイ準備",
    "description": "本番環境の構築",
    "dueDate": null,
    "completed": false,
    "createdAt": "2026-05-28T13:00:00Z",
    "updatedAt": "2026-05-28T13:00:00Z"
  }
}
```

**フィールド定義**:

| フィールド名 | 型 | 必須 | 説明 | 制約 |
|-------------|-----|------|------|------|
| `id` | string | Yes | TODO ID（UUID） | 主キー、一意 |
| `userId` | string | Yes | 所有ユーザーID | 外部キー（system users.id） |
| `title` | string | Yes | タイトル | 1〜100文字 |
| `description` | string | No | 内容 | 0〜500文字 |
| `dueDate` | string | No | 期限 | ISO8601形式（YYYY-MM-DDTHH:MM:SSZ） |
| `completed` | boolean | Yes | 完了フラグ | `true` or `false` |
| `createdAt` | string | Yes | 作成日時 | ISO8601形式 |
| `updatedAt` | string | Yes | 更新日時 | ISO8601形式 |

**インデックス（将来のRDB用）**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `userId` REFERENCES `users(id)` ON DELETE CASCADE
- INDEX: `userId`, `completed`
- INDEX: `dueDate`

---

## 3. RDB テーブル設計（将来対応）

### 3.1 todos テーブル

```sql
CREATE TABLE todos (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    due_date TIMESTAMP,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_completed (completed),
    INDEX idx_due_date (due_date),
    INDEX idx_user_completed (user_id, completed)
);
```

**テーブル説明**:
- **主キー**: `id`（UUID）
- **外部キー**: `user_id` → システム共通基盤の `users(id)`
- **インデックス**:
  - `user_id`: ユーザーごとのTODO一覧取得で使用
  - `completed`: 完了状態フィルタで使用
  - `due_date`: 期限順ソートで使用
  - `user_id, completed`: ユーザー・完了状態の組み合わせフィルタで使用

---

## 4. データ検証ルール

### 4.1 必須フィールド

| フィールド | 検証ルール |
|-----------|-----------|
| `id` | 必須、UUID形式 |
| `userId` | 必須、システム共通基盤の `users.id` に存在する |
| `title` | 必須、1文字以上100文字以内 |
| `completed` | 必須、`true` or `false` |
| `createdAt` | 必須、ISO8601形式 |
| `updatedAt` | 必須、ISO8601形式 |

### 4.2 任意フィールド

| フィールド | 検証ルール |
|-----------|-----------|
| `description` | 任意、0〜500文字 |
| `dueDate` | 任意、ISO8601形式（指定時のみ） |

### 4.3 バリデーション実装

**ファイル**: `apps/todo-app/backend/app/services/todo_service.py`

```python
def validate_todo_data(self, data: dict) -> tuple[bool, str]:
    """TODOデータをバリデーション"""
    # タイトルチェック
    title = data.get("title", "")
    if "title" in data:
        if not title or title.strip() == "":
            return False, "ERR-TODO-003"  # タイトルは必須です
        if len(title) > 100:
            return False, "ERR-TODO-004"  # タイトルは100文字以内である必要があります
    
    # 説明チェック
    description = data.get("description", "")
    if description and len(description) > 500:
        return False, "ERR-TODO-005"  # 説明は500文字以内である必要があります
    
    # 期限チェック
    due_date = data.get("dueDate")
    if due_date:
        try:
            datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return False, "ERR-TODO-006"  # 期限の形式が不正です
    
    return True, ""
```

---

## 5. データクエリパターン

### 5.1 主要クエリ

#### 5.1.1 ユーザーのTODO一覧取得（フィルタ・ソート対応）

**JSON DB実装**:

```python
def find_by_user(
    self,
    user_id: str,
    completed: bool | None = None,
    search: str | None = None,
    sort_by: str = "createdAt",
    order: str = "desc",
    limit: int = 100,
    offset: int = 0
) -> list[dict]:
    """ユーザーのTODO一覧を取得"""
    all_data = self._load_data()
    results = []
    
    for todo in all_data.values():
        # ユーザーIDフィルタ
        if todo["userId"] != user_id:
            continue
        
        # 完了状態フィルタ
        if completed is not None and todo["completed"] != completed:
            continue
        
        # 検索フィルタ
        if search:
            search_lower = search.lower()
            if search_lower not in todo["title"].lower() and search_lower not in todo["description"].lower():
                continue
        
        results.append(todo)
    
    # ソート
    reverse = (order == "desc")
    results.sort(key=lambda t: t.get(sort_by, ""), reverse=reverse)
    
    # ページネーション
    return results[offset:offset + limit]
```

**RDB実装（MySQL）**:

```sql
SELECT *
FROM todos
WHERE user_id = ?
  AND (? IS NULL OR completed = ?)
  AND (? IS NULL OR (LOWER(title) LIKE ? OR LOWER(description) LIKE ?))
ORDER BY
  CASE WHEN ? = 'createdAt' THEN created_at END DESC,
  CASE WHEN ? = 'dueDate' THEN due_date END DESC,
  CASE WHEN ? = 'title' THEN title END ASC
LIMIT ? OFFSET ?;
```

---

#### 5.1.2 TODO統計情報取得

**JSON DB実装**:

```python
def count_by_user(self, user_id: str, completed: bool | None = None) -> int:
    """ユーザーのTODO数をカウント"""
    criteria = {"userId": user_id}
    if completed is not None:
        criteria["completed"] = completed
    return self.count(criteria)

def count_overdue(self, user_id: str) -> int:
    """ユーザーの期限切れTODO数をカウント"""
    all_data = self._load_data()
    now = datetime.utcnow().isoformat()
    count = 0
    
    for todo in all_data.values():
        if todo["userId"] != user_id:
            continue
        if todo["completed"]:
            continue
        if not todo.get("dueDate"):
            continue
        if todo["dueDate"] < now:
            count += 1
    
    return count
```

**RDB実装（MySQL）**:

```sql
-- 総TODO数
SELECT COUNT(*) FROM todos WHERE user_id = ?;

-- 完了TODO数
SELECT COUNT(*) FROM todos WHERE user_id = ? AND completed = TRUE;

-- 未完了TODO数
SELECT COUNT(*) FROM todos WHERE user_id = ? AND completed = FALSE;

-- 期限切れTODO数
SELECT COUNT(*)
FROM todos
WHERE user_id = ?
  AND completed = FALSE
  AND due_date IS NOT NULL
  AND due_date < NOW();
```

---

#### 5.1.3 TODO詳細取得（権限チェック）

**JSON DB実装**:

```python
def get_todo(self, todo_id: str, user_id: str) -> Todo:
    """TODO詳細を取得（権限チェック）"""
    todo_data = self.dal.find_one({"id": todo_id})
    if not todo_data:
        raise HTTPException(status_code=404, detail="ERR-TODO-001")
    
    # 権限チェック
    if todo_data["userId"] != user_id:
        raise HTTPException(status_code=403, detail="ERR-TODO-002")
    
    return Todo.from_dict(todo_data)
```

**RDB実装（MySQL）**:

```sql
SELECT *
FROM todos
WHERE id = ? AND user_id = ?;
```

---

## 6. データ整合性チェック

### 6.1 チェック項目

| チェック項目 | 説明 |
|------------|------|
| **外部キー整合性** | `todos.userId` がシステム共通基盤の `users.id` に存在するか |
| **必須フィールド** | 必須フィールドが null や空文字列でないか |
| **データ型** | 各フィールドが期待する型（文字列・真偽値）か |
| **日時フォーマット** | ISO8601形式（YYYY-MM-DDTHH:MM:SSZ）か |
| **タイトル長** | 1〜100文字か |
| **説明長** | 0〜500文字か |

---

### 6.2 整合性チェックスクリプト

**ファイル**: `apps/todo-app/backend/scripts/check_data_integrity.py`

```python
import json
import os
from datetime import datetime

def check_todos():
    with open("apps/todo-app/backend/data/todos.json", "r") as f:
        todos = json.load(f)
    
    # システムユーザー読み込み
    with open("backend/data/users.json", "r") as f:
        users = json.load(f)
    
    errors = []
    
    for todo_id, todo in todos.items():
        # 必須フィールドチェック
        required_fields = ["id", "userId", "title", "completed", "createdAt", "updatedAt"]
        for field in required_fields:
            if field not in todo:
                errors.append(f"Todo {todo_id}: Missing field '{field}'")
        
        # 外部キー整合性チェック
        if todo["userId"] not in users:
            errors.append(f"Todo {todo_id}: Invalid userId '{todo['userId']}'")
        
        # タイトル長チェック
        if len(todo["title"]) == 0 or len(todo["title"]) > 100:
            errors.append(f"Todo {todo_id}: Title length invalid (1-100 required)")
        
        # 説明長チェック
        if "description" in todo and len(todo["description"]) > 500:
            errors.append(f"Todo {todo_id}: Description too long (max 500)")
        
        # 日時フォーマットチェック
        for date_field in ["createdAt", "updatedAt", "dueDate"]:
            if date_field in todo and todo[date_field]:
                try:
                    datetime.fromisoformat(todo[date_field].replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    errors.append(f"Todo {todo_id}: Invalid date format in '{date_field}'")
    
    return errors

if __name__ == "__main__":
    errors = check_todos()
    
    if errors:
        print("Data integrity errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Data integrity check passed!")
```

---

## 7. データ移行方法（JSON → RDB）

### 7.1 移行手順

1. **RDBテーブル作成**: 上記SQLを実行
2. **DAL切り替え**: `JsonDAL` → `MysqlDAL` or `PostgresDAL`
3. **データ移行スクリプト実行**:

```python
from apps.todo_app.backend.app.dal.json_dal import TodoDAL
from apps.todo_app.backend.app.dal.mysql_dal import TodoMysqlDAL
import json

def migrate_todos():
    json_dal = TodoDAL("apps/todo-app/backend/data")
    mysql_dal = TodoMysqlDAL(connection_string)
    
    todos = json_dal._load_data()
    for todo_id, todo_data in todos.items():
        mysql_dal.insert(todo_data)

if __name__ == "__main__":
    migrate_todos()
```

4. **動作確認**: RDBに切り替えて全機能をテスト
5. **JSONファイルのバックアップ・削除**

---

## 8. バックアップ・リカバリ戦略

### 8.1 JSON DB（現状）

| 項目 | 方法 |
|------|------|
| **バックアップ** | `apps/todo-app/backend/data/` ディレクトリ全体をコピー |
| **頻度** | 1日1回（cron） |
| **保存先** | `apps/todo-app/backend/data/backups/YYYY-MM-DD/` |
| **世代管理** | 30日分保存、それ以前は削除 |
| **リカバリ** | バックアップディレクトリから復元 |

**バックアップスクリプト例**:

```bash
#!/bin/bash
BACKUP_DIR="apps/todo-app/backend/data/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"
cp apps/todo-app/backend/data/todos.json "$BACKUP_DIR/"
# 30日以前のバックアップを削除
find apps/todo-app/backend/data/backups -type d -mtime +30 -exec rm -rf {} \;
```

---

### 8.2 RDB（将来対応）

| 項目 | 方法 |
|------|------|
| **バックアップ** | `mysqldump` or `pg_dump` |
| **頻度** | 1日1回（cron） + トランザクションログ |
| **保存先** | 外部ストレージ（S3、GCS等） |
| **世代管理** | フルバックアップ: 7日分、差分: 30日分 |
| **リカバリ** | フルバックアップ + 差分バックアップを適用 |

---

## 9. まとめ

### 9.1 データベーススキーマ一覧

| ファイル/テーブル | 説明 | 主キー | 外部キー |
|-----------------|------|--------|---------|
| `todos.json` / `todos` | TODO情報 | `id` | `userId` → システム共通 `users(id)` |

### 9.2 設計ポイント

- **システム共通基盤との連携**: `userId` がシステム共通基盤の `users.id` を参照
- **DAL抽象化**: JSON DB → RDB移行を透過的に実現
- **インデックス設計**: 検索頻度の高いフィールドにインデックスを設定
- **外部キー制約**: ユーザー削除時にTODOも削除（CASCADE）
- **バックアップ戦略**: 定期バックアップ + 世代管理

### 9.3 次工程への引き継ぎ

- 工程4（コーディング）では、このスキーマに基づいてDAL実装を行う
- テストデータは `tests/fixtures/` に配置
- データ整合性チェックは `apps/todo-app/backend/scripts/check_data_integrity.py` で実施

---

**トレーサビリティ**: この設計書は工程2の基本設計書（architecture.md）および工程3の `class-design.md` に基づいています。
