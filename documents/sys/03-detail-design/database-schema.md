# データベーススキーマ設計書（システム共通基盤）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | システム共通基盤（sys） |
| 工程 | 工程3: 詳細設計 |

---

## 1. データベース概要

### 1.1 現状（JSON DB）

| 項目 | 内容 |
|------|------|
| **形式** | JSONファイル |
| **配置** | `backend/data/` |
| **エンコーディング** | UTF-8 |
| **インデント** | 2スペース |
| **アクセス方法** | `JsonDAL` クラス経由 |

### 1.2 将来対応（RDB）

| 項目 | 内容 |
|------|------|
| **候補** | MySQL 8.0+, PostgreSQL 14+ |
| **移行方法** | DAL抽象化により透過的に切り替え |
| **テーブル設計** | JSON構造をそのままテーブルに変換 |
| **インデックス** | 主キー・外部キー・検索頻度の高いカラムに設定 |

---

## 2. JSON DB スキーマ（現状）

### 2.1 users.json

**ファイルパス**: `backend/data/users.json`

**説明**: ユーザー情報を格納

**構造**:

```json
{
  "user_001": {
    "id": "user_001",
    "username": "admin",
    "passwordHash": "$2b$12$XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "displayName": "管理者",
    "role": "admin",
    "email": "admin@example.com",
    "metadata": {
      "department": "システム管理部",
      "phone": "090-1234-5678"
    },
    "createdAt": "2026-05-01T10:00:00Z",
    "updatedAt": "2026-05-28T09:00:00Z",
    "lastLogin": "2026-05-28T09:00:00Z"
  },
  "user_002": {
    "id": "user_002",
    "username": "user1",
    "passwordHash": "$2b$12$YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY",
    "displayName": "ユーザー1",
    "role": "user",
    "email": "user1@example.com",
    "metadata": {},
    "createdAt": "2026-05-10T12:00:00Z",
    "updatedAt": "2026-05-27T15:30:00Z",
    "lastLogin": "2026-05-27T15:30:00Z"
  }
}
```

**フィールド定義**:

| フィールド名 | 型 | 必須 | 説明 | 制約 |
|-------------|-----|------|------|------|
| `id` | string | Yes | ユーザーID（UUID） | 主キー、一意 |
| `username` | string | Yes | ユーザー名 | 一意、3〜50文字、英数字・アンダースコアのみ |
| `passwordHash` | string | Yes | パスワードハッシュ（bcrypt） | bcrypt形式（$2b$） |
| `displayName` | string | Yes | 表示名 | 1〜100文字 |
| `role` | string | Yes | ロール | `"admin"` or `"user"` |
| `email` | string | Yes | メールアドレス | 有効なメールアドレス形式 |
| `metadata` | object | No | 任意のメタデータ | JSONオブジェクト |
| `createdAt` | string | Yes | 作成日時 | ISO8601形式 |
| `updatedAt` | string | Yes | 更新日時 | ISO8601形式 |
| `lastLogin` | string | No | 最終ログイン日時 | ISO8601形式 |

**インデックス（将来のRDB用）**:
- PRIMARY KEY: `id`
- UNIQUE KEY: `username`
- UNIQUE KEY: `email`
- INDEX: `role`

---

### 2.2 apps.json

**ファイルパス**: `backend/data/apps.json`

**説明**: アプリケーション情報を格納

**構造**:

```json
{
  "todo-app": {
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
  },
  "calendar-app": {
    "id": "calendar-app",
    "name": "カレンダー",
    "version": "1.0.0",
    "description": "スケジュール管理アプリケーション",
    "icon": "/apps/calendar-app/icon.png",
    "entryPoint": "/apps/calendar-app/",
    "apiPrefix": "/api/calendar-app",
    "enabled": false,
    "author": "System Team",
    "requiredPermissions": ["read", "write"],
    "dependencies": [],
    "manifest": {
      "name": "calendar-app",
      "displayName": "カレンダー",
      "version": "1.0.0",
      "description": "スケジュール管理アプリケーション",
      "entryPoint": "/apps/calendar-app/",
      "apiPrefix": "/api/calendar-app",
      "icon": "icon.png",
      "author": "System Team",
      "requiredPermissions": ["read", "write"],
      "dependencies": []
    },
    "lastUpdated": "2026-05-28T10:00:00Z"
  }
}
```

**フィールド定義**:

| フィールド名 | 型 | 必須 | 説明 | 制約 |
|-------------|-----|------|------|------|
| `id` | string | Yes | アプリID（manifest.jsonの `name`） | 主キー、一意 |
| `name` | string | Yes | アプリ表示名 | 1〜100文字 |
| `version` | string | Yes | バージョン | セマンティックバージョニング（例: `1.0.0`） |
| `description` | string | No | 説明 | 0〜500文字 |
| `icon` | string | No | アイコンパス | URLパス |
| `entryPoint` | string | Yes | エントリーポイントURL | URLパス |
| `apiPrefix` | string | Yes | APIプレフィックス | URLパス（例: `/api/todo-app`） |
| `enabled` | boolean | Yes | 有効化状態 | `true` or `false` |
| `author` | string | No | 作成者 | 0〜100文字 |
| `requiredPermissions` | array | No | 必要な権限リスト | 文字列の配列 |
| `dependencies` | array | No | 依存アプリリスト | アプリIDの配列 |
| `manifest` | object | Yes | manifest.json全体 | JSONオブジェクト |
| `lastUpdated` | string | Yes | 最終更新日時 | ISO8601形式 |

**インデックス（将来のRDB用）**:
- PRIMARY KEY: `id`
- INDEX: `enabled`

---

### 2.3 sessions/ （ディレクトリ）

**ディレクトリパス**: `backend/data/sessions/`

**説明**: セッション情報を個別ファイルで格納

**ファイル構造**: `sessions/{session_id}.json`

**例**: `backend/data/sessions/session_001.json`

```json
{
  "sessionId": "session_001",
  "userId": "user_001",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzAwMSIsInVzZXJuYW1lIjoiYWRtaW4iLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3MTY5MDAwMDB9.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "createdAt": "2026-05-28T09:00:00Z",
  "expiresAt": "2026-05-29T09:00:00Z",
  "metadata": {
    "ipAddress": "192.168.1.100",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
  }
}
```

**フィールド定義**:

| フィールド名 | 型 | 必須 | 説明 | 制約 |
|-------------|-----|------|------|------|
| `sessionId` | string | Yes | セッションID（UUID） | 主キー、一意 |
| `userId` | string | Yes | ユーザーID | 外部キー（users.id） |
| `token` | string | Yes | JWTトークン | JWT形式 |
| `createdAt` | string | Yes | 作成日時 | ISO8601形式 |
| `expiresAt` | string | Yes | 有効期限 | ISO8601形式 |
| `metadata` | object | No | 任意のメタデータ | JSONオブジェクト（IPアドレス・User-Agent） |

**インデックス（将来のRDB用）**:
- PRIMARY KEY: `sessionId`
- UNIQUE KEY: `token`
- FOREIGN KEY: `userId` REFERENCES `users(id)` ON DELETE CASCADE
- INDEX: `expiresAt`

**自動クリーンアップ**: 
- 定期実行（cron）で `expiresAt < 現在日時` のセッションを削除
- 実行頻度: 1時間ごと

---

### 2.4 notifications.json

**ファイルパス**: `backend/data/notifications.json`

**説明**: 通知情報を格納

**構造**:

```json
{
  "notif_001": {
    "id": "notif_001",
    "userId": "user_001",
    "type": "info",
    "title": "新しいTODOが追加されました",
    "message": "「プロジェクト計画書を作成」が追加されました",
    "metadata": {
      "todoId": "todo_001",
      "link": "/apps/todo-app/#todo_001"
    },
    "read": false,
    "createdAt": "2026-05-28T10:00:00Z",
    "expiresAt": "2026-06-27T10:00:00Z"
  },
  "notif_002": {
    "id": "notif_002",
    "userId": "user_001",
    "type": "success",
    "title": "TODOが完了しました",
    "message": "「テストコード作成」が完了しました",
    "metadata": {
      "todoId": "todo_002",
      "link": "/apps/todo-app/#todo_002"
    },
    "read": true,
    "createdAt": "2026-05-28T12:00:00Z",
    "expiresAt": "2026-06-27T12:00:00Z"
  }
}
```

**フィールド定義**:

| フィールド名 | 型 | 必須 | 説明 | 制約 |
|-------------|-----|------|------|------|
| `id` | string | Yes | 通知ID（UUID） | 主キー、一意 |
| `userId` | string | Yes | 宛先ユーザーID | 外部キー（users.id） |
| `type` | string | Yes | 通知タイプ | `"info"`, `"warning"`, `"error"`, `"success"` |
| `title` | string | Yes | タイトル | 1〜200文字 |
| `message` | string | Yes | メッセージ本文 | 1〜1000文字 |
| `metadata` | object | No | 任意のメタデータ | JSONオブジェクト（リンク・アクション情報） |
| `read` | boolean | Yes | 既読フラグ | `true` or `false` |
| `createdAt` | string | Yes | 作成日時 | ISO8601形式 |
| `expiresAt` | string | No | 有効期限 | ISO8601形式 |

**インデックス（将来のRDB用）**:
- PRIMARY KEY: `id`
- FOREIGN KEY: `userId` REFERENCES `users(id)` ON DELETE CASCADE
- INDEX: `userId`, `read`
- INDEX: `expiresAt`

**自動クリーンアップ**: 
- 定期実行（cron）で `expiresAt < 現在日時` の通知を削除
- 実行頻度: 1日1回

---

### 2.5 config.json

**ファイルパス**: `backend/data/config.json`

**説明**: システム設定を格納

**構造**:

```json
{
  "system": {
    "name": "Webシステム共通基盤",
    "version": "1.0.0",
    "environment": "development",
    "baseUrl": "http://localhost:8000"
  },
  "jwt": {
    "secretKey": "your-secret-key-here-change-in-production",
    "algorithm": "HS256",
    "expirationHours": 24
  },
  "security": {
    "bcryptRounds": 12,
    "passwordMinLength": 8,
    "sessionTimeout": 86400
  },
  "notifications": {
    "defaultExpirationDays": 30,
    "maxNotificationsPerUser": 100
  },
  "apps": {
    "autoScanOnStartup": true,
    "scanInterval": 3600
  }
}
```

**フィールド定義**:

| セクション | フィールド名 | 型 | 説明 | デフォルト値 |
|-----------|-------------|-----|------|-------------|
| `system` | `name` | string | システム名 | `"Webシステム共通基盤"` |
| `system` | `version` | string | システムバージョン | `"1.0.0"` |
| `system` | `environment` | string | 環境（`development`, `production`） | `"development"` |
| `system` | `baseUrl` | string | ベースURL | `"http://localhost:8000"` |
| `jwt` | `secretKey` | string | JWT署名鍵（本番では環境変数から取得） | — |
| `jwt` | `algorithm` | string | JWT署名アルゴリズム | `"HS256"` |
| `jwt` | `expirationHours` | int | JWT有効期限（時間） | `24` |
| `security` | `bcryptRounds` | int | bcryptコスト | `12` |
| `security` | `passwordMinLength` | int | パスワード最小長 | `8` |
| `security` | `sessionTimeout` | int | セッションタイムアウト（秒） | `86400`（24時間） |
| `notifications` | `defaultExpirationDays` | int | 通知デフォルト有効期限（日） | `30` |
| `notifications` | `maxNotificationsPerUser` | int | ユーザーあたり最大通知数 | `100` |
| `apps` | `autoScanOnStartup` | bool | 起動時にアプリ自動スキャン | `true` |
| `apps` | `scanInterval` | int | アプリ再スキャン間隔（秒） | `3600`（1時間） |

---

## 3. RDB テーブル設計（将来対応）

### 3.1 users テーブル

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    email VARCHAR(255) UNIQUE NOT NULL,
    metadata JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
);
```

---

### 3.2 apps テーブル

```sql
CREATE TABLE apps (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description VARCHAR(500),
    icon VARCHAR(255),
    entry_point VARCHAR(255) NOT NULL,
    api_prefix VARCHAR(255) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    author VARCHAR(100),
    required_permissions JSON,
    dependencies JSON,
    manifest JSON NOT NULL,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_enabled (enabled)
);
```

---

### 3.3 sessions テーブル

```sql
CREATE TABLE sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    token TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    metadata JSON,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY idx_token (token(255)),
    INDEX idx_expires_at (expires_at)
);
```

**自動クリーンアップ（MySQL Event）**:

```sql
CREATE EVENT cleanup_expired_sessions
ON SCHEDULE EVERY 1 HOUR
DO
DELETE FROM sessions WHERE expires_at < NOW();
```

---

### 3.4 notifications テーブル

```sql
CREATE TABLE notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    type ENUM('info', 'warning', 'error', 'success') NOT NULL,
    title VARCHAR(200) NOT NULL,
    message VARCHAR(1000) NOT NULL,
    metadata JSON,
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, read),
    INDEX idx_expires_at (expires_at)
);
```

**自動クリーンアップ（MySQL Event）**:

```sql
CREATE EVENT cleanup_expired_notifications
ON SCHEDULE EVERY 1 DAY
DO
DELETE FROM notifications WHERE expires_at IS NOT NULL AND expires_at < NOW();
```

---

### 3.5 config テーブル

```sql
CREATE TABLE config (
    key VARCHAR(100) PRIMARY KEY,
    value JSON NOT NULL,
    description VARCHAR(500),
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**初期データ投入**:

```sql
INSERT INTO config (key, value, description) VALUES
('system', '{"name": "Webシステム共通基盤", "version": "1.0.0", "environment": "development", "baseUrl": "http://localhost:8000"}', 'システム設定'),
('jwt', '{"secretKey": "your-secret-key-here", "algorithm": "HS256", "expirationHours": 24}', 'JWT設定'),
('security', '{"bcryptRounds": 12, "passwordMinLength": 8, "sessionTimeout": 86400}', 'セキュリティ設定'),
('notifications', '{"defaultExpirationDays": 30, "maxNotificationsPerUser": 100}', '通知設定'),
('apps', '{"autoScanOnStartup": true, "scanInterval": 3600}', 'アプリ設定');
```

---

## 4. データ移行方法（JSON → RDB）

### 4.1 移行手順

1. **RDBテーブル作成**: 上記SQLを実行
2. **DAL切り替え**: `JsonDAL` → `MysqlDAL` or `PostgresDAL`
3. **データ移行スクリプト実行**:

```python
from backend.app.sys.dal.json_dal import JsonDAL
from backend.app.sys.dal.mysql_dal import MysqlDAL
import json

def migrate_users():
    json_dal = JsonDAL("backend/data")
    mysql_dal = MysqlDAL(connection_string)
    
    users = json_dal.find_all_from_file("users.json")
    for user_id, user_data in users.items():
        mysql_dal.insert_user(user_data)

def migrate_apps():
    # 同様の処理

def migrate_sessions():
    # 同様の処理

def migrate_notifications():
    # 同様の処理

if __name__ == "__main__":
    migrate_users()
    migrate_apps()
    migrate_sessions()
    migrate_notifications()
```

4. **動作確認**: RDBに切り替えて全機能をテスト
5. **JSONファイルのバックアップ・削除**

---

### 4.2 DAL抽象化の利点

| 利点 | 説明 |
|------|------|
| **透過的な切り替え** | サービス層のコードを変更せずにDB切り替え可能 |
| **テストの容易性** | モックDALを注入してテスト可能 |
| **段階的移行** | 一部のテーブルだけRDB化することも可能 |
| **複数DB対応** | MySQL, PostgreSQL, SQLiteなどを統一インターフェースで扱える |

---

## 5. バックアップ・リカバリ戦略

### 5.1 JSON DB（現状）

| 項目 | 方法 |
|------|------|
| **バックアップ** | `backend/data/` ディレクトリ全体をコピー |
| **頻度** | 1日1回（cron） |
| **保存先** | `backend/data/backups/YYYY-MM-DD/` |
| **世代管理** | 30日分保存、それ以前は削除 |
| **リカバリ** | バックアップディレクトリから復元 |

**バックアップスクリプト例**:

```bash
#!/bin/bash
BACKUP_DIR="backend/data/backups/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"
cp -r backend/data/*.json "$BACKUP_DIR/"
cp -r backend/data/sessions "$BACKUP_DIR/"
# 30日以前のバックアップを削除
find backend/data/backups -type d -mtime +30 -exec rm -rf {} \;
```

---

### 5.2 RDB（将来対応）

| 項目 | 方法 |
|------|------|
| **バックアップ** | `mysqldump` or `pg_dump` |
| **頻度** | 1日1回（cron） + トランザクションログ |
| **保存先** | 外部ストレージ（S3、GCS等） |
| **世代管理** | フルバックアップ: 7日分、差分: 30日分 |
| **リカバリ** | フルバックアップ + 差分バックアップを適用 |

**MySQLバックアップスクリプト例**:

```bash
#!/bin/bash
BACKUP_FILE="backup-$(date +%Y%m%d-%H%M%S).sql.gz"
mysqldump -u root -p'password' websys_db | gzip > "$BACKUP_FILE"
aws s3 cp "$BACKUP_FILE" s3://websys-backups/
```

---

## 6. データ整合性チェック

### 6.1 チェック項目

| チェック項目 | 説明 |
|------------|------|
| **外部キー整合性** | `sessions.userId` が `users.id` に存在するか |
| **ユニーク制約** | `users.username`, `users.email` が重複していないか |
| **必須フィールド** | 必須フィールドが null や空文字列でないか |
| **データ型** | 各フィールドが期待する型（文字列・数値・真偽値）か |
| **日時フォーマット** | ISO8601形式（YYYY-MM-DDTHH:MM:SSZ）か |
| **bcrypt形式** | `users.passwordHash` が `$2b$` で始まるか |

---

### 6.2 整合性チェックスクリプト

**ファイル**: `backend/scripts/check_data_integrity.py`

```python
import json
import os
from datetime import datetime

def check_users():
    with open("backend/data/users.json", "r") as f:
        users = json.load(f)
    
    errors = []
    usernames = set()
    emails = set()
    
    for user_id, user in users.items():
        # 必須フィールドチェック
        required_fields = ["id", "username", "passwordHash", "displayName", "role", "email", "createdAt", "updatedAt"]
        for field in required_fields:
            if field not in user:
                errors.append(f"User {user_id}: Missing field '{field}'")
        
        # ユニーク制約チェック
        if user["username"] in usernames:
            errors.append(f"User {user_id}: Duplicate username '{user['username']}'")
        usernames.add(user["username"])
        
        if user["email"] in emails:
            errors.append(f"User {user_id}: Duplicate email '{user['email']}'")
        emails.add(user["email"])
        
        # bcrypt形式チェック
        if not user["passwordHash"].startswith("$2b$"):
            errors.append(f"User {user_id}: Invalid bcrypt format")
    
    return errors

def check_sessions():
    # 同様の処理
    pass

if __name__ == "__main__":
    errors = check_users()
    errors += check_sessions()
    
    if errors:
        print("Data integrity errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Data integrity check passed!")
```

---

## 7. まとめ

### 7.1 データベーススキーマ一覧

| ファイル/テーブル | 説明 | 主キー | 外部キー |
|-----------------|------|--------|---------|
| `users.json` / `users` | ユーザー情報 | `id` | — |
| `apps.json` / `apps` | アプリケーション情報 | `id` | — |
| `sessions/{session_id}.json` / `sessions` | セッション情報 | `sessionId` | `userId` → `users(id)` |
| `notifications.json` / `notifications` | 通知情報 | `id` | `userId` → `users(id)` |
| `config.json` / `config` | システム設定 | `key` | — |

### 7.2 設計ポイント

- **DAL抽象化**: JSON DB → RDB移行を透過的に実現
- **インデックス設計**: 検索頻度の高いフィールドにインデックスを設定
- **外部キー制約**: 参照整合性を保証（RDB）
- **自動クリーンアップ**: 期限切れデータを定期削除
- **バックアップ戦略**: 定期バックアップ + 世代管理

### 7.3 次工程への引き継ぎ

- 工程4（コーディング）では、このスキーマに基づいてDAL実装を行う
- テストデータは `tests/fixtures/` に配置
- データ整合性チェックは `backend/scripts/check_data_integrity.py` で実施

---

**トレーサビリティ**: この設計書は工程2の基本設計書（architecture.md）および工程3の `class-design.md` に基づいています。
