# テストケース設計書（システム共通基盤）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | システム共通基盤（sys） |
| 工程 | 工程3: 詳細設計 |

---

## 1. テスト戦略

### 1.1 テストレベル

| テストレベル | 対象 | 実施工程 | カバレッジ目標 |
|------------|------|---------|--------------|
| **単体テスト** | 個別クラス・メソッド | 工程5 | MCDC 100% |
| **結合テスト** | API・サービス間連携 | 工程6 | API 100% |
| **システムテスト** | エンドツーエンド | 工程7 | 要件 100% |

### 1.2 テストツール

| 用途 | ツール | バージョン |
|------|-------|----------|
| **Pythonテスト** | pytest | 7.x+ |
| **モック** | pytest-mock, unittest.mock | — |
| **カバレッジ** | pytest-cov | — |
| **TypeScriptテスト** | Vitest | 1.x+ |
| **E2Eテスト** | Playwright | 1.40+ |

### 1.3 テストデータ

**配置先**: `tests/fixtures/`

| ファイル | 説明 |
|---------|------|
| `users.json` | テスト用ユーザーデータ |
| `apps.json` | テスト用アプリデータ |
| `sessions.json` | テスト用セッションデータ |
| `notifications.json` | テスト用通知データ |

---

## 2. 単体テストケース設計（工程5）

### 2.1 エンティティクラステスト

#### 2.1.1 User クラステスト

**テストファイル**: `tests/backend/sys/models/test_user.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 |
|--------------|----------|------|------|---------|
| `SYS-UT-USER-001` | ユーザー作成（正常） | 正常系 | 有効なユーザーデータ | User インスタンス生成成功 |
| `SYS-UT-USER-002` | パスワード検証（正常） | 正常系 | 正しいパスワード | `validate_password()` が `True` を返す |
| `SYS-UT-USER-003` | パスワード検証（失敗） | 異常系 | 誤ったパスワード | `validate_password()` が `False` を返す |
| `SYS-UT-USER-004` | 辞書変換（正常） | 正常系 | User インスタンス | `to_dict()` でパスワードハッシュが除外される |
| `SYS-UT-USER-005` | 辞書変換（パスワード含む） | 正常系 | `include_password=True` | `to_dict()` でパスワードハッシュが含まれる |
| `SYS-UT-USER-006` | 辞書からインスタンス生成 | 正常系 | 有効な辞書 | `from_dict()` で User インスタンス生成 |
| `SYS-UT-USER-007` | ロール検証（admin） | 境界値 | `role="admin"` | ロールが `"admin"` |
| `SYS-UT-USER-008` | ロール検証（user） | 境界値 | `role="user"` | ロールが `"user"` |

**実装例**:

```python
import pytest
from backend.app.sys.models.user import User
import bcrypt

def test_user_create():
    """SYS-UT-USER-001: ユーザー作成（正常）"""
    user = User(
        id="user_001",
        username="testuser",
        passwordHash=bcrypt.hashpw("password".encode(), bcrypt.gensalt()).decode(),
        displayName="テストユーザー",
        role="user",
        email="test@example.com",
        createdAt="2026-05-28T10:00:00Z",
        updatedAt="2026-05-28T10:00:00Z"
    )
    assert user.id == "user_001"
    assert user.username == "testuser"
    assert user.role == "user"

def test_user_validate_password_success():
    """SYS-UT-USER-002: パスワード検証（正常）"""
    password = "password123"
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user = User(
        id="user_001",
        username="testuser",
        passwordHash=password_hash,
        displayName="テストユーザー",
        role="user",
        email="test@example.com",
        createdAt="2026-05-28T10:00:00Z",
        updatedAt="2026-05-28T10:00:00Z"
    )
    assert user.validate_password("password123") is True

def test_user_validate_password_failure():
    """SYS-UT-USER-003: パスワード検証（失敗）"""
    password_hash = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
    user = User(
        id="user_001",
        username="testuser",
        passwordHash=password_hash,
        displayName="テストユーザー",
        role="user",
        email="test@example.com",
        createdAt="2026-05-28T10:00:00Z",
        updatedAt="2026-05-28T10:00:00Z"
    )
    assert user.validate_password("wrongpassword") is False

def test_user_to_dict_exclude_password():
    """SYS-UT-USER-004: 辞書変換（正常）"""
    user = User(
        id="user_001",
        username="testuser",
        passwordHash="$2b$12$XXXXXX",
        displayName="テストユーザー",
        role="user",
        email="test@example.com",
        createdAt="2026-05-28T10:00:00Z",
        updatedAt="2026-05-28T10:00:00Z"
    )
    user_dict = user.to_dict()
    assert "passwordHash" not in user_dict
    assert user_dict["username"] == "testuser"
```

---

#### 2.1.2 JWTService クラステスト

**テストファイル**: `tests/backend/sys/core/test_jwt_service.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 |
|--------------|----------|------|------|---------|
| `SYS-UT-JWT-001` | JWT生成（正常） | 正常系 | User インスタンス | JWT文字列生成成功 |
| `SYS-UT-JWT-002` | JWT検証（正常） | 正常系 | 有効なJWT | ペイロードが返る |
| `SYS-UT-JWT-003` | JWT検証（期限切れ） | 異常系 | 期限切れJWT | `None` が返る |
| `SYS-UT-JWT-004` | JWT検証（署名不正） | 異常系 | 不正署名JWT | `None` が返る |
| `SYS-UT-JWT-005` | JWTデコード（検証なし） | 正常系 | JWT（検証なし） | ペイロードが返る |
| `SYS-UT-JWT-006` | JWTリフレッシュ（正常） | 正常系 | 有効なJWT | 新しいJWT生成 |
| `SYS-UT-JWT-007` | JWTリフレッシュ（期限切れ） | 異常系 | 期限切れJWT | `None` が返る |
| `SYS-UT-JWT-008` | ペイロード内容確認 | 境界値 | 生成したJWT | `sub`, `username`, `role`, `exp`, `iat` を含む |

---

### 2.2 サービス層テスト

#### 2.2.1 AuthService クラステスト

**テストファイル**: `tests/backend/sys/core/test_auth_service.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 | エラーコード |
|--------------|----------|------|------|---------|------------|
| `SYS-UT-AUTH-001` | 認証（正常） | 正常系 | 正しいユーザー名・パスワード | User と JWT が返る | — |
| `SYS-UT-AUTH-002` | 認証（ユーザー名不正） | 異常系 | 存在しないユーザー名 | `HTTPException(401)` 発生 | `ERR-SYS-AUTH-001` |
| `SYS-UT-AUTH-003` | 認証（パスワード不正） | 異常系 | 誤ったパスワード | `HTTPException(401)` 発生 | `ERR-SYS-AUTH-001` |
| `SYS-UT-AUTH-004` | セッション作成（正常） | 正常系 | User と JWT | Session インスタンス生成 | — |
| `SYS-UT-AUTH-005` | ログアウト（正常） | 正常系 | 有効なセッションID | `True` が返る | — |
| `SYS-UT-AUTH-006` | ログアウト（セッション不正） | 異常系 | 存在しないセッションID | `False` が返る | — |
| `SYS-UT-AUTH-007` | 現在のユーザー取得（正常） | 正常系 | 有効なJWT | User インスタンスが返る | — |
| `SYS-UT-AUTH-008` | 現在のユーザー取得（JWT不正） | 異常系 | 不正なJWT | `HTTPException(401)` 発生 | `ERR-SYS-AUTH-002` |
| `SYS-UT-AUTH-009` | パスワード変更（正常） | 正常系 | 正しい現在のパスワード | `True` が返る | — |
| `SYS-UT-AUTH-010` | パスワード変更（現在のパスワード不正） | 異常系 | 誤った現在のパスワード | `HTTPException(401)` 発生 | `ERR-SYS-AUTH-007` |
| `SYS-UT-AUTH-011` | パスワードハッシュ化 | 正常系 | 平文パスワード | bcrypt形式のハッシュが返る | — |
| `SYS-UT-AUTH-012` | パスワード検証（正常） | 正常系 | 正しいパスワードとハッシュ | `True` が返る | — |
| `SYS-UT-AUTH-013` | パスワード検証（失敗） | 異常系 | 誤ったパスワードとハッシュ | `False` が返る | — |

**実装例**:

```python
import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from backend.app.sys.core.auth import AuthService
from backend.app.sys.models.user import User

@pytest.fixture
def auth_service():
    user_dal_mock = Mock()
    jwt_service_mock = Mock()
    session_dal_mock = Mock()
    return AuthService(user_dal_mock, jwt_service_mock, session_dal_mock)

def test_authenticate_success(auth_service):
    """SYS-UT-AUTH-001: 認証（正常）"""
    user_data = {
        "id": "user_001",
        "username": "testuser",
        "passwordHash": bcrypt.hashpw("password".encode(), bcrypt.gensalt()).decode(),
        "displayName": "テストユーザー",
        "role": "user",
        "email": "test@example.com",
        "createdAt": "2026-05-28T10:00:00Z",
        "updatedAt": "2026-05-28T10:00:00Z"
    }
    auth_service.user_dal.find_by_username.return_value = user_data
    auth_service.jwt_service.create_token.return_value = "jwt_token"
    auth_service.user_dal.update_last_login.return_value = True
    
    user, token = auth_service.authenticate("testuser", "password")
    
    assert user.username == "testuser"
    assert token == "jwt_token"

def test_authenticate_user_not_found(auth_service):
    """SYS-UT-AUTH-002: 認証（ユーザー名不正）"""
    auth_service.user_dal.find_by_username.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        auth_service.authenticate("nonexistent", "password")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "ERR-SYS-AUTH-001"
```

---

#### 2.2.2 UserService クラステスト

**テストファイル**: `tests/backend/sys/services/test_user_service.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 | エラーコード |
|--------------|----------|------|------|---------|------------|
| `SYS-UT-USRV-001` | ユーザー一覧取得（正常） | 正常系 | `role=None, limit=100, offset=0` | ユーザー一覧が返る | — |
| `SYS-UT-USRV-002` | ユーザー一覧取得（ロールフィルタ） | 正常系 | `role="admin"` | 管理者のみ返る | — |
| `SYS-UT-USRV-003` | ユーザー詳細取得（正常） | 正常系 | 有効なユーザーID | User インスタンスが返る | — |
| `SYS-UT-USRV-004` | ユーザー詳細取得（未検出） | 異常系 | 存在しないユーザーID | `HTTPException(404)` 発生 | `ERR-SYS-USER-001` |
| `SYS-UT-USRV-005` | ユーザー作成（正常） | 正常系 | 有効なユーザーデータ | User インスタンスが返る | — |
| `SYS-UT-USRV-006` | ユーザー作成（ユーザー名重複） | 異常系 | 既存ユーザー名 | `HTTPException(409)` 発生 | `ERR-SYS-USER-002` |
| `SYS-UT-USRV-007` | ユーザー作成（メール重複） | 異常系 | 既存メールアドレス | `HTTPException(409)` 発生 | `ERR-SYS-USER-003` |
| `SYS-UT-USRV-008` | ユーザー更新（正常） | 正常系 | 有効な更新データ | User インスタンスが返る | — |
| `SYS-UT-USRV-009` | ユーザー削除（正常） | 正常系 | 有効なユーザーID | `True` が返る | — |
| `SYS-UT-USRV-010` | ユーザー削除（自分自身） | 異常系 | 自分のユーザーID | `HTTPException(400)` 発生 | `ERR-SYS-USER-007` |
| `SYS-UT-USRV-011` | バリデーション（ユーザー名短い） | 異常系 | `username="ab"` | `HTTPException(400)` 発生 | `ERR-SYS-USER-004` |
| `SYS-UT-USRV-012` | バリデーション（ユーザー名長い） | 異常系 | `username="a"*51` | `HTTPException(400)` 発生 | `ERR-SYS-USER-004` |
| `SYS-UT-USRV-013` | バリデーション（メール不正） | 異常系 | `email="invalid"` | `HTTPException(400)` 発生 | `ERR-SYS-USER-005` |
| `SYS-UT-USRV-014` | バリデーション（ロール不正） | 異常系 | `role="superuser"` | `HTTPException(400)` 発生 | `ERR-SYS-USER-006` |

---

#### 2.2.3 AppService クラステスト

**テストファイル**: `tests/backend/sys/services/test_app_service.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 | エラーコード |
|--------------|----------|------|------|---------|------------|
| `SYS-UT-APPS-001` | アプリスキャン（正常） | 正常系 | 有効なmanifest.json | アプリリストが返る | — |
| `SYS-UT-APPS-002` | アプリスキャン（manifest不正） | 異常系 | 不正なmanifest.json | エラーログ出力、スキップ | — |
| `SYS-UT-APPS-003` | アプリ一覧取得（正常） | 正常系 | `enabled=None` | 全アプリが返る | — |
| `SYS-UT-APPS-004` | アプリ一覧取得（有効のみ） | 正常系 | `enabled=True` | 有効アプリのみ返る | — |
| `SYS-UT-APPS-005` | アプリ詳細取得（正常） | 正常系 | 有効なアプリID | App インスタンスが返る | — |
| `SYS-UT-APPS-006` | アプリ詳細取得（未検出） | 異常系 | 存在しないアプリID | `HTTPException(404)` 発生 | `ERR-SYS-APPS-001` |
| `SYS-UT-APPS-007` | アプリ有効化（正常） | 正常系 | 無効なアプリID | `True` が返る | — |
| `SYS-UT-APPS-008` | アプリ有効化（既に有効） | 異常系 | 有効なアプリID | `HTTPException(400)` 発生 | `ERR-SYS-APPS-002` |
| `SYS-UT-APPS-009` | アプリ無効化（正常） | 正常系 | 有効なアプリID | `True` が返る | — |
| `SYS-UT-APPS-010` | アプリ無効化（既に無効） | 異常系 | 無効なアプリID | `HTTPException(400)` 発生 | `ERR-SYS-APPS-003` |
| `SYS-UT-APPS-011` | manifest検証（正常） | 正常系 | 有効なmanifest | `True` が返る | — |
| `SYS-UT-APPS-012` | manifest検証（必須フィールド欠落） | 異常系 | 不正なmanifest | `False` が返る | — |

---

#### 2.2.4 NotificationService クラステスト

**テストファイル**: `tests/backend/sys/services/test_notification_service.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 | エラーコード |
|--------------|----------|------|------|---------|------------|
| `SYS-UT-NOTF-001` | 通知作成（正常） | 正常系 | 有効な通知データ | Notification インスタンスが返る | — |
| `SYS-UT-NOTF-002` | 通知一覧取得（正常） | 正常系 | `unread_only=False` | 全通知が返る | — |
| `SYS-UT-NOTF-003` | 通知一覧取得（未読のみ） | 正常系 | `unread_only=True` | 未読通知のみ返る | — |
| `SYS-UT-NOTF-004` | 通知既読化（正常） | 正常系 | 有効な通知ID | `True` が返る | — |
| `SYS-UT-NOTF-005` | 通知既読化（未検出） | 異常系 | 存在しない通知ID | `HTTPException(404)` 発生 | `ERR-SYS-NOTF-001` |
| `SYS-UT-NOTF-006` | 通知既読化（権限なし） | 異常系 | 他ユーザーの通知ID | `HTTPException(403)` 発生 | `ERR-SYS-NOTF-002` |
| `SYS-UT-NOTF-007` | 通知削除（正常） | 正常系 | 有効な通知ID | `True` が返る | — |
| `SYS-UT-NOTF-008` | SSEストリーム生成 | 正常系 | 有効なユーザーID | AsyncGenerator が返る | — |
| `SYS-UT-NOTF-009` | SSE配信（正常） | 正常系 | 有効な通知 | キューに追加される | — |
| `SYS-UT-NOTF-010` | 期限切れ通知削除 | 正常系 | なし | 削除数が返る | — |

---

### 2.3 DAL層テスト

#### 2.3.1 JsonDAL クラステスト

**テストファイル**: `tests/backend/sys/dal/test_json_dal.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 |
|--------------|----------|------|------|---------|
| `SYS-UT-DAL-001` | レコード挿入（正常） | 正常系 | 有効なデータ | IDが返る |
| `SYS-UT-DAL-002` | レコード検索（正常） | 正常系 | 有効な条件 | レコードリストが返る |
| `SYS-UT-DAL-003` | レコード検索（条件一致なし） | 異常系 | 存在しない条件 | 空リストが返る |
| `SYS-UT-DAL-004` | レコード1件検索（正常） | 正常系 | 有効な条件 | 1件のレコードが返る |
| `SYS-UT-DAL-005` | レコード更新（正常） | 正常系 | 有効なID・データ | `True` が返る |
| `SYS-UT-DAL-006` | レコード更新（ID不正） | 異常系 | 存在しないID | `False` が返る |
| `SYS-UT-DAL-007` | レコード削除（正常） | 正常系 | 有効なID | `True` が返る |
| `SYS-UT-DAL-008` | レコード削除（ID不正） | 異常系 | 存在しないID | `False` が返る |
| `SYS-UT-DAL-009` | レコード数カウント | 正常系 | 有効な条件 | カウント数が返る |
| `SYS-UT-DAL-010` | レコード存在確認（存在） | 正常系 | 存在する条件 | `True` が返る |
| `SYS-UT-DAL-011` | レコード存在確認（不存在） | 異常系 | 存在しない条件 | `False` が返る |
| `SYS-UT-DAL-012` | ファイル保存・読み込み | 正常系 | データ保存 | 同じデータが読み込まれる |

---

## 3. MCDC カバレッジ設計

### 3.1 MCDC（Modified Condition/Decision Coverage）とは

**定義**: 全ての条件が独立して真偽の判定に影響することを確認するカバレッジ基準

**例**:

```python
if user.role == "admin" and app.enabled:
    # 処理A
```

**MCDCテストケース**:

| ケース | `user.role == "admin"` | `app.enabled` | 結果 | 影響する条件 |
|--------|----------------------|--------------|------|------------|
| 1 | True | True | True | — |
| 2 | True | False | False | `app.enabled` |
| 3 | False | True | False | `user.role == "admin"` |
| 4 | False | False | False | — |

**MCDC達成条件**:
- ケース1, 2, 3を実行すれば、両条件が独立して結果に影響することを確認できる

---

### 3.2 主要条件分岐のMCDCテストケース

#### 3.2.1 認証処理の条件分岐

```python
if user_data and user.validate_password(password):
    # 認証成功
```

| ケース | `user_data` 存在 | `validate_password()` | 結果 | 影響する条件 |
|--------|-----------------|---------------------|------|------------|
| 1 | True | True | 認証成功 | — |
| 2 | True | False | 認証失敗 | `validate_password()` |
| 3 | False | — | 認証失敗 | `user_data` 存在 |

**対応テストケース**: `SYS-UT-AUTH-001`, `SYS-UT-AUTH-002`, `SYS-UT-AUTH-003`

---

#### 3.2.2 JWT検証の条件分岐

```python
if payload and payload["exp"] > current_time and session_exists:
    # JWT有効
```

| ケース | `payload` 存在 | `exp > current_time` | `session_exists` | 結果 | 影響する条件 |
|--------|--------------|---------------------|-----------------|------|------------|
| 1 | True | True | True | 有効 | — |
| 2 | True | True | False | 無効 | `session_exists` |
| 3 | True | False | True | 無効 | `exp > current_time` |
| 4 | False | — | — | 無効 | `payload` 存在 |

**対応テストケース**: `SYS-UT-JWT-002`, `SYS-UT-JWT-003`, `SYS-UT-JWT-004`, `SYS-UT-AUTH-008`

---

### 3.3 MCDCカバレッジツール

**pytest-cov 使用例**:

```bash
pytest --cov=backend/app/sys --cov-report=html --cov-report=term
```

**カバレッジ目標**: 単体テストで MCDC 100% 達成

---

## 4. テストデータ設計

### 4.1 テスト用ユーザーデータ

**ファイル**: `tests/fixtures/users.json`

```json
{
  "test_admin": {
    "id": "test_admin",
    "username": "testadmin",
    "passwordHash": "$2b$12$TEST_ADMIN_PASSWORD_HASH",
    "displayName": "テスト管理者",
    "role": "admin",
    "email": "testadmin@example.com",
    "metadata": {},
    "createdAt": "2026-05-01T10:00:00Z",
    "updatedAt": "2026-05-01T10:00:00Z"
  },
  "test_user": {
    "id": "test_user",
    "username": "testuser",
    "passwordHash": "$2b$12$TEST_USER_PASSWORD_HASH",
    "displayName": "テストユーザー",
    "role": "user",
    "email": "testuser@example.com",
    "metadata": {},
    "createdAt": "2026-05-01T10:00:00Z",
    "updatedAt": "2026-05-01T10:00:00Z"
  }
}
```

---

### 4.2 テスト用アプリデータ

**ファイル**: `tests/fixtures/apps.json`

```json
{
  "test-app-enabled": {
    "id": "test-app-enabled",
    "name": "テストアプリ（有効）",
    "version": "1.0.0",
    "description": "テスト用アプリ（有効化済み）",
    "entryPoint": "/apps/test-app-enabled/",
    "apiPrefix": "/api/test-app-enabled",
    "enabled": true,
    "author": "Test Team",
    "manifest": {}
  },
  "test-app-disabled": {
    "id": "test-app-disabled",
    "name": "テストアプリ（無効）",
    "version": "1.0.0",
    "description": "テスト用アプリ（無効化済み）",
    "entryPoint": "/apps/test-app-disabled/",
    "apiPrefix": "/api/test-app-disabled",
    "enabled": false,
    "author": "Test Team",
    "manifest": {}
  }
}
```

---

## 5. まとめ

### 5.1 単体テストケース総数

| カテゴリ | テストケース数 |
|---------|-------------|
| エンティティ（User） | 8 |
| エンティティ（JWT） | 8 |
| サービス（AuthService） | 13 |
| サービス（UserService） | 14 |
| サービス（AppService） | 12 |
| サービス（NotificationService） | 10 |
| DAL（JsonDAL） | 12 |
| **合計** | **77** |

### 5.2 次工程への引き継ぎ

- 工程5（単体評価）では、このテストケース設計に基づいてテストコードを実装
- pytest を使用してテスト実行
- MCDCカバレッジ 100% を目指す
- テストレポートは `documents/sys/05-unit-test-report.md` に記載

---

**トレーサビリティ**: この設計書は工程2の基本設計書（api-design.md）および工程3の `class-design.md`, `sequence-diagrams.md`, `error-handling.md` に基づいています。
