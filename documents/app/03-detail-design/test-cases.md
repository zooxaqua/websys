# テストケース設計書（TODOアプリ）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | TODOアプリ（app） |
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

**配置先**: `apps/todo-app/tests/fixtures/`

| ファイル | 説明 |
|---------|------|
| `todos.json` | テスト用TODOデータ |
| `users.json` | テスト用ユーザーデータ（システム共通基盤から参照） |

---

## 2. 単体テストケース設計（工程5）

### 2.1 エンティティクラステスト

#### 2.1.1 Todo クラステスト

**テストファイル**: `apps/todo-app/tests/backend/models/test_todo.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 |
|--------------|----------|------|------|---------|
| `TODO-UT-TODO-001` | TODO作成（正常） | 正常系 | 有効なTODOデータ | Todo インスタンス生成成功 |
| `TODO-UT-TODO-002` | 辞書変換（正常） | 正常系 | Todo インスタンス | `to_dict()` で辞書が返る |
| `TODO-UT-TODO-003` | 辞書からインスタンス生成 | 正常系 | 有効な辞書 | `from_dict()` で Todo インスタンス生成 |
| `TODO-UT-TODO-004` | 期限切れ判定（期限切れ） | 正常系 | 未完了 + 期限が過去 | `is_overdue()` が `True` を返す |
| `TODO-UT-TODO-005` | 期限切れ判定（期限内） | 正常系 | 未完了 + 期限が未来 | `is_overdue()` が `False` を返す |
| `TODO-UT-TODO-006` | 期限切れ判定（完了済み） | 境界値 | 完了 + 期限が過去 | `is_overdue()` が `False` を返す |
| `TODO-UT-TODO-007` | 期限切れ判定（期限なし） | 境界値 | 未完了 + 期限なし | `is_overdue()` が `False` を返す |
| `TODO-UT-TODO-008` | 完了切り替え（未完了→完了） | 正常系 | `completed=False` | `toggle_completed()` で `completed=True` |
| `TODO-UT-TODO-009` | 完了切り替え（完了→未完了） | 正常系 | `completed=True` | `toggle_completed()` で `completed=False` |

**実装例**:

```python
import pytest
from apps.todo_app.backend.app.models.todo import Todo
from datetime import datetime, timedelta

def test_todo_create():
    """TODO-UT-TODO-001: TODO作成（正常）"""
    todo = Todo(
        id="todo_001",
        userId="user_001",
        title="テストTODO",
        description="テスト用の説明",
        dueDate="2026-06-01T00:00:00Z",
        completed=False,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    assert todo.id == "todo_001"
    assert todo.title == "テストTODO"
    assert todo.completed == False

def test_todo_to_dict():
    """TODO-UT-TODO-002: 辞書変換（正常）"""
    todo = Todo(
        id="todo_001",
        userId="user_001",
        title="テストTODO",
        description="テスト用の説明",
        dueDate="2026-06-01T00:00:00Z",
        completed=False,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    todo_dict = todo.to_dict()
    assert todo_dict["id"] == "todo_001"
    assert todo_dict["title"] == "テストTODO"

def test_todo_is_overdue_true():
    """TODO-UT-TODO-004: 期限切れ判定（期限切れ）"""
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    todo = Todo(
        id="todo_001",
        userId="user_001",
        title="期限切れTODO",
        description="",
        dueDate=past_date,
        completed=False,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    assert todo.is_overdue() == True

def test_todo_is_overdue_false_future():
    """TODO-UT-TODO-005: 期限切れ判定（期限内）"""
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    todo = Todo(
        id="todo_001",
        userId="user_001",
        title="期限内TODO",
        description="",
        dueDate=future_date,
        completed=False,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    assert todo.is_overdue() == False

def test_todo_toggle_completed():
    """TODO-UT-TODO-008: 完了切り替え（未完了→完了）"""
    todo = Todo(
        id="todo_001",
        userId="user_001",
        title="テストTODO",
        description="",
        dueDate=None,
        completed=False,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow()
    )
    todo.toggle_completed()
    assert todo.completed == True
```

---

### 2.2 サービス層テスト

#### 2.2.1 TodoService クラステスト

**テストファイル**: `apps/todo-app/tests/backend/services/test_todo_service.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 | エラーコード |
|--------------|----------|------|------|---------|------------|
| `TODO-UT-TSRV-001` | TODO一覧取得（正常） | 正常系 | `user_id` | TODOリストが返る | — |
| `TODO-UT-TSRV-002` | TODO一覧取得（完了フィルタ） | 正常系 | `completed=True` | 完了TODOのみ返る | — |
| `TODO-UT-TSRV-003` | TODO一覧取得（検索） | 正常系 | `search="テスト"` | 検索に一致するTODOが返る | — |
| `TODO-UT-TSRV-004` | TODO詳細取得（正常） | 正常系 | 有効なTODO ID + user_id | Todo インスタンスが返る | — |
| `TODO-UT-TSRV-005` | TODO詳細取得（未検出） | 異常系 | 存在しないTODO ID | `HTTPException(404)` 発生 | `ERR-TODO-001` |
| `TODO-UT-TSRV-006` | TODO詳細取得（権限なし） | 異常系 | 他ユーザーのTODO ID | `HTTPException(403)` 発生 | `ERR-TODO-002` |
| `TODO-UT-TSRV-007` | TODO作成（正常） | 正常系 | 有効なTODOデータ | Todo インスタンスが返る | — |
| `TODO-UT-TSRV-008` | TODO作成（タイトル未入力） | 異常系 | `title=""` | `HTTPException(400)` 発生 | `ERR-TODO-003` |
| `TODO-UT-TSRV-009` | TODO作成（タイトル長すぎ） | 異常系 | `title="a"*101` | `HTTPException(400)` 発生 | `ERR-TODO-004` |
| `TODO-UT-TSRV-010` | TODO作成（説明長すぎ） | 異常系 | `description="a"*501` | `HTTPException(400)` 発生 | `ERR-TODO-005` |
| `TODO-UT-TSRV-011` | TODO作成（期限形式不正） | 異常系 | `dueDate="invalid"` | `HTTPException(400)` 発生 | `ERR-TODO-006` |
| `TODO-UT-TSRV-012` | TODO更新（正常） | 正常系 | 有効なTODO ID + データ | Todo インスタンスが返る | — |
| `TODO-UT-TSRV-013` | TODO更新（権限なし） | 異常系 | 他ユーザーのTODO ID | `HTTPException(403)` 発生 | `ERR-TODO-002` |
| `TODO-UT-TSRV-014` | TODO削除（正常） | 正常系 | 有効なTODO ID + user_id | `True` が返る | — |
| `TODO-UT-TSRV-015` | TODO削除（権限なし） | 異常系 | 他ユーザーのTODO ID | `HTTPException(403)` 発生 | `ERR-TODO-002` |
| `TODO-UT-TSRV-016` | TODO完了切り替え（正常） | 正常系 | 有効なTODO ID + user_id | `completed` が反転したTodoが返る | — |
| `TODO-UT-TSRV-017` | TODO統計取得（正常） | 正常系 | `user_id` | `{total, completed, pending, overdue}` が返る | — |
| `TODO-UT-TSRV-018` | バリデーション（タイトル必須） | 異常系 | `title=""` | `(False, "ERR-TODO-003")` が返る | — |
| `TODO-UT-TSRV-019` | バリデーション（タイトル長すぎ） | 異常系 | `title="a"*101` | `(False, "ERR-TODO-004")` が返る | — |
| `TODO-UT-TSRV-020` | バリデーション（説明長すぎ） | 異常系 | `description="a"*501` | `(False, "ERR-TODO-005")` が返る | — |
| `TODO-UT-TSRV-021` | バリデーション（期限形式不正） | 異常系 | `dueDate="invalid"` | `(False, "ERR-TODO-006")` が返る | — |

**実装例**:

```python
import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from apps.todo_app.backend.app.services.todo_service import TodoService
from apps.todo_app.backend.app.models.todo import Todo
from datetime import datetime

@pytest.fixture
def todo_service():
    dal_mock = Mock()
    return TodoService(dal_mock)

def test_list_todos(todo_service):
    """TODO-UT-TSRV-001: TODO一覧取得（正常）"""
    todos_data = [
        {
            "id": "todo_001",
            "userId": "user_001",
            "title": "テストTODO1",
            "description": "",
            "dueDate": None,
            "completed": False,
            "createdAt": "2026-05-28T10:00:00Z",
            "updatedAt": "2026-05-28T10:00:00Z"
        }
    ]
    todo_service.dal.find_by_user.return_value = todos_data
    todo_service.dal.count_by_user.return_value = 1
    
    todos, total = todo_service.list_todos("user_001")
    
    assert len(todos) == 1
    assert total == 1
    assert todos[0].title == "テストTODO1"

def test_get_todo_success(todo_service):
    """TODO-UT-TSRV-004: TODO詳細取得（正常）"""
    todo_data = {
        "id": "todo_001",
        "userId": "user_001",
        "title": "テストTODO",
        "description": "",
        "dueDate": None,
        "completed": False,
        "createdAt": "2026-05-28T10:00:00Z",
        "updatedAt": "2026-05-28T10:00:00Z"
    }
    todo_service.dal.find_one.return_value = todo_data
    
    todo = todo_service.get_todo("todo_001", "user_001")
    
    assert todo.id == "todo_001"
    assert todo.title == "テストTODO"

def test_get_todo_not_found(todo_service):
    """TODO-UT-TSRV-005: TODO詳細取得（未検出）"""
    todo_service.dal.find_one.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        todo_service.get_todo("todo_999", "user_001")
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "ERR-TODO-001"

def test_get_todo_access_denied(todo_service):
    """TODO-UT-TSRV-006: TODO詳細取得（権限なし）"""
    todo_data = {
        "id": "todo_001",
        "userId": "user_002",  # 別ユーザー
        "title": "テストTODO",
        "description": "",
        "dueDate": None,
        "completed": False,
        "createdAt": "2026-05-28T10:00:00Z",
        "updatedAt": "2026-05-28T10:00:00Z"
    }
    todo_service.dal.find_one.return_value = todo_data
    
    with pytest.raises(HTTPException) as exc_info:
        todo_service.get_todo("todo_001", "user_001")
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "ERR-TODO-002"

def test_create_todo_title_required(todo_service):
    """TODO-UT-TSRV-008: TODO作成（タイトル未入力）"""
    with pytest.raises(HTTPException) as exc_info:
        todo_service.create_todo("user_001", "", "")
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "ERR-TODO-003"

def test_validate_todo_data_title_too_long(todo_service):
    """TODO-UT-TSRV-019: バリデーション（タイトル長すぎ）"""
    is_valid, error_code = todo_service.validate_todo_data({"title": "a" * 101})
    
    assert is_valid == False
    assert error_code == "ERR-TODO-004"
```

---

### 2.3 DAL層テスト

#### 2.3.1 TodoDAL クラステスト

**テストファイル**: `apps/todo-app/tests/backend/dal/test_todo_dal.py`

| テストケースID | テスト項目 | 観点 | 入力 | 期待結果 |
|--------------|----------|------|------|---------|
| `TODO-UT-DAL-001` | TODO挿入（正常） | 正常系 | 有効なTODOデータ | IDが返る |
| `TODO-UT-DAL-002` | ユーザーのTODO一覧取得（正常） | 正常系 | `user_id` | 該当ユーザーのTODOのみ返る |
| `TODO-UT-DAL-003` | TODO一覧取得（完了フィルタ） | 正常系 | `completed=True` | 完了TODOのみ返る |
| `TODO-UT-DAL-004` | TODO一覧取得（検索フィルタ） | 正常系 | `search="テスト"` | タイトル・説明に一致するTODOが返る |
| `TODO-UT-DAL-005` | TODO一覧取得（ソート：作成日降順） | 正常系 | `sort_by="createdAt", order="desc"` | 作成日降順でソートされる |
| `TODO-UT-DAL-006` | TODO一覧取得（ソート：期限昇順） | 正常系 | `sort_by="dueDate", order="asc"` | 期限昇順でソートされる |
| `TODO-UT-DAL-007` | TODO一覧取得（ページネーション） | 正常系 | `limit=2, offset=0` | 2件のみ返る |
| `TODO-UT-DAL-008` | TODOカウント（全体） | 正常系 | `user_id` | 該当ユーザーの総TODO数が返る |
| `TODO-UT-DAL-009` | TODOカウント（完了のみ） | 正常系 | `user_id, completed=True` | 完了TODO数が返る |
| `TODO-UT-DAL-010` | 期限切れTODOカウント | 正常系 | `user_id` | 期限切れTODO数が返る |
| `TODO-UT-DAL-011` | TODO更新（正常） | 正常系 | 有効なTODO ID + データ | `True` が返る |
| `TODO-UT-DAL-012` | TODO削除（正常） | 正常系 | 有効なTODO ID | `True` が返る |

---

## 3. MCDC カバレッジ設計

### 3.1 主要条件分岐のMCDCテストケース

#### 3.1.1 期限切れ判定の条件分岐

```python
if self.completed or not self.dueDate:
    return False
due_date = datetime.fromisoformat(self.dueDate.replace("Z", "+00:00"))
return due_date < datetime.utcnow()
```

| ケース | `completed` | `dueDate` 存在 | `dueDate < 現在日時` | 結果 | 影響する条件 |
|--------|------------|---------------|---------------------|------|------------|
| 1 | False | True | True | True（期限切れ） | — |
| 2 | False | True | False | False | `dueDate < 現在日時` |
| 3 | False | False | — | False | `dueDate` 存在 |
| 4 | True | True | True | False | `completed` |

**対応テストケース**: `TODO-UT-TODO-004`, `TODO-UT-TODO-005`, `TODO-UT-TODO-006`, `TODO-UT-TODO-007`

---

#### 3.1.2 権限チェックの条件分岐

```python
if not todo_data:
    raise HTTPException(status_code=404, detail="ERR-TODO-001")

if todo_data["userId"] != user_id:
    raise HTTPException(status_code=403, detail="ERR-TODO-002")
```

| ケース | `todo_data` 存在 | `userId` 一致 | 結果 | 影響する条件 |
|--------|----------------|-------------|------|------------|
| 1 | True | True | アクセス許可 | — |
| 2 | True | False | 403エラー | `userId` 一致 |
| 3 | False | — | 404エラー | `todo_data` 存在 |

**対応テストケース**: `TODO-UT-TSRV-004`, `TODO-UT-TSRV-005`, `TODO-UT-TSRV-006`

---

### 3.2 MCDCカバレッジツール

**pytest-cov 使用例**:

```bash
pytest --cov=apps/todo-app/backend/app --cov-report=html --cov-report=term
```

**カバレッジ目標**: 単体テストで MCDC 100% 達成

---

## 4. テストデータ設計

### 4.1 テスト用TODOデータ

**ファイル**: `apps/todo-app/tests/fixtures/todos.json`

```json
{
  "test_todo_001": {
    "id": "test_todo_001",
    "userId": "test_user",
    "title": "テストTODO1",
    "description": "テスト用TODO1",
    "dueDate": "2026-06-01T00:00:00Z",
    "completed": false,
    "createdAt": "2026-05-28T10:00:00Z",
    "updatedAt": "2026-05-28T10:00:00Z"
  },
  "test_todo_002": {
    "id": "test_todo_002",
    "userId": "test_user",
    "title": "テストTODO2（完了）",
    "description": "テスト用TODO2（完了済み）",
    "dueDate": "2026-06-05T00:00:00Z",
    "completed": true,
    "createdAt": "2026-05-28T11:00:00Z",
    "updatedAt": "2026-05-28T12:00:00Z"
  },
  "test_todo_003": {
    "id": "test_todo_003",
    "userId": "test_admin",
    "title": "管理者のTODO",
    "description": "管理者用TODO",
    "dueDate": null,
    "completed": false,
    "createdAt": "2026-05-28T13:00:00Z",
    "updatedAt": "2026-05-28T13:00:00Z"
  }
}
```

---

## 5. まとめ

### 5.1 単体テストケース総数

| カテゴリ | テストケース数 |
|---------|-------------|
| エンティティ（Todo） | 9 |
| サービス（TodoService） | 21 |
| DAL（TodoDAL） | 12 |
| **合計** | **42** |

### 5.2 次工程への引き継ぎ

- 工程5（単体評価）では、このテストケース設計に基づいてテストコードを実装
- pytest を使用してテスト実行
- MCDCカバレッジ 100% を目指す
- テストレポートは `documents/app/05-unit-test-report.md` に記載

---

**トレーサビリティ**: この設計書は工程2の基本設計書（api-design.md）および工程3の `class-design.md`, `sequence-diagrams.md`, `error-handling.md` に基づいています。
