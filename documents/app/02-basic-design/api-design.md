# API設計書（TODOアプリ）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | TODOアプリ（app） |
| 工程 | 工程2: 基本設計 |

---

## 1. API概要

### 1.1 基本仕様

| 項目 | 仕様 |
|------|------|
| **プロトコル** | HTTP/1.1, HTTPS |
| **データフォーマット** | JSON |
| **文字エンコーディング** | UTF-8 |
| **認証方式** | JWT（httpOnly Cookie、システム共通基盤） |
| **ベースURL（開発）** | `http://localhost:8000` |
| **APIプレフィックス** | `/api/todo-app` |

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

## 2. TODO CRUD API

### API-TODO-001: TODO一覧取得

**エンドポイント**: `GET /api/todo-app/todos`

**説明**: ログイン中のユーザーのTODO一覧を取得する

**認証**: 必要

**クエリパラメータ**:

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| `completed` | boolean | No | 完了状態でフィルタ（`true`, `false`） |
| `search` | string | No | タイトル・内容で検索 |
| `sortBy` | string | No | ソート順（`createdAt`, `dueDate`, `title`）、デフォルト: `createdAt` |
| `order` | string | No | 昇順・降順（`asc`, `desc`）、デフォルト: `desc` |
| `limit` | integer | No | 取得件数、デフォルト: 100 |
| `offset` | integer | No | オフセット、デフォルト: 0 |

**レスポンス（成功: 200 OK）**:

```json
{
  "todos": [
    {
      "id": "todo_001",
      "userId": "user_001",
      "title": "プロジェクト計画書を作成",
      "description": "工程2の基本設計書を作成する",
      "dueDate": "2026-06-01T00:00:00Z",
      "completed": false,
      "createdAt": "2026-05-28T10:00:00Z",
      "updatedAt": "2026-05-28T10:00:00Z"
    },
    {
      "id": "todo_002",
      "userId": "user_001",
      "title": "テストコード作成",
      "description": "単体テストを作成する",
      "dueDate": "2026-06-05T00:00:00Z",
      "completed": true,
      "createdAt": "2026-05-28T11:00:00Z",
      "updatedAt": "2026-05-28T12:00:00Z"
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
| 401 | `AUTH_INVALID_TOKEN` | 認証トークンが無効です |

---

### API-TODO-002: TODO詳細取得

**エンドポイント**: `GET /api/todo-app/todos/{todo_id}`

**説明**: 特定TODOの詳細情報を取得する

**認証**: 必要

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `todo_id` | string | TODO ID |

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "todo_001",
  "userId": "user_001",
  "title": "プロジェクト計画書を作成",
  "description": "工程2の基本設計書を作成する",
  "dueDate": "2026-06-01T00:00:00Z",
  "completed": false,
  "createdAt": "2026-05-28T10:00:00Z",
  "updatedAt": "2026-05-28T10:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `TODO_NOT_FOUND` | TODOが見つかりません |
| 403 | `TODO_ACCESS_DENIED` | このTODOにアクセスする権限がありません |

---

### API-TODO-003: TODO作成

**エンドポイント**: `POST /api/todo-app/todos`

**説明**: 新しいTODOを作成する

**認証**: 必要

**リクエスト**:

```json
{
  "title": "プロジェクト計画書を作成",
  "description": "工程2の基本設計書を作成する",
  "dueDate": "2026-06-01T00:00:00Z"
}
```

**レスポンス（成功: 201 Created）**:

```json
{
  "id": "todo_003",
  "userId": "user_001",
  "title": "プロジェクト計画書を作成",
  "description": "工程2の基本設計書を作成する",
  "dueDate": "2026-06-01T00:00:00Z",
  "completed": false,
  "createdAt": "2026-05-28T13:00:00Z",
  "updatedAt": "2026-05-28T13:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 400 | `TODO_TITLE_REQUIRED` | タイトルは必須です |
| 400 | `TODO_TITLE_TOO_LONG` | タイトルは100文字以内である必要があります |
| 400 | `TODO_DESCRIPTION_TOO_LONG` | 説明は500文字以内である必要があります |
| 400 | `TODO_INVALID_DUE_DATE` | 期限の形式が不正です |

---

### API-TODO-004: TODO更新

**エンドポイント**: `PUT /api/todo-app/todos/{todo_id}`

**説明**: 既存TODOの情報を更新する

**認証**: 必要

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `todo_id` | string | TODO ID |

**リクエスト**:

```json
{
  "title": "プロジェクト計画書を作成（更新）",
  "description": "工程2の基本設計書を作成する（詳細追加）",
  "dueDate": "2026-06-02T00:00:00Z",
  "completed": false
}
```

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "todo_001",
  "userId": "user_001",
  "title": "プロジェクト計画書を作成（更新）",
  "description": "工程2の基本設計書を作成する（詳細追加）",
  "dueDate": "2026-06-02T00:00:00Z",
  "completed": false,
  "createdAt": "2026-05-28T10:00:00Z",
  "updatedAt": "2026-05-28T14:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `TODO_NOT_FOUND` | TODOが見つかりません |
| 403 | `TODO_ACCESS_DENIED` | このTODOにアクセスする権限がありません |
| 400 | `TODO_TITLE_REQUIRED` | タイトルは必須です |
| 400 | `TODO_TITLE_TOO_LONG` | タイトルは100文字以内である必要があります |
| 400 | `TODO_DESCRIPTION_TOO_LONG` | 説明は500文字以内である必要があります |

---

### API-TODO-005: TODO削除

**エンドポイント**: `DELETE /api/todo-app/todos/{todo_id}`

**説明**: TODOを削除する

**認証**: 必要

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `todo_id` | string | TODO ID |

**レスポンス（成功: 200 OK）**:

```json
{
  "success": true,
  "message": "TODOを削除しました"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `TODO_NOT_FOUND` | TODOが見つかりません |
| 403 | `TODO_ACCESS_DENIED` | このTODOにアクセスする権限がありません |

---

### API-TODO-006: TODO完了/未完了切り替え

**エンドポイント**: `PATCH /api/todo-app/todos/{todo_id}/toggle`

**説明**: TODOの完了状態を切り替える

**認証**: 必要

**パスパラメータ**:

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| `todo_id` | string | TODO ID |

**レスポンス（成功: 200 OK）**:

```json
{
  "id": "todo_001",
  "userId": "user_001",
  "title": "プロジェクト計画書を作成",
  "description": "工程2の基本設計書を作成する",
  "dueDate": "2026-06-01T00:00:00Z",
  "completed": true,
  "createdAt": "2026-05-28T10:00:00Z",
  "updatedAt": "2026-05-28T15:00:00Z"
}
```

**エラーレスポンス**:

| ステータス | コード | メッセージ |
|-----------|--------|-----------|
| 404 | `TODO_NOT_FOUND` | TODOが見つかりません |
| 403 | `TODO_ACCESS_DENIED` | このTODOにアクセスする権限がありません |

---

## 3. TODO統計API

### API-TODO-010: TODO統計情報取得

**エンドポイント**: `GET /api/todo-app/todos/stats`

**説明**: ユーザーのTODO統計情報を取得する

**認証**: 必要

**レスポンス（成功: 200 OK）**:

```json
{
  "total": 10,
  "completed": 3,
  "pending": 7,
  "overdue": 2
}
```

**統計項目**:

| 項目 | 説明 |
|------|------|
| `total` | 総TODO数 |
| `completed` | 完了済みTODO数 |
| `pending` | 未完了TODO数 |
| `overdue` | 期限切れTODO数（未完了 && 期限 < 現在日時） |

---

## 4. API実装例

### 4.1 FastAPI ルーター構成

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.app.sys.core.dependencies import get_current_user
from apps.todo_app.backend.app.models.todo import TodoCreate, TodoUpdate, TodoResponse
from apps.todo_app.backend.app.services.todo_service import TodoService

router = APIRouter(prefix="/api/todo-app/todos", tags=["todo"])

@router.get("/")
async def list_todos(
    completed: Optional[bool] = None,
    search: Optional[str] = None,
    sortBy: str = "createdAt",
    order: str = "desc",
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(get_current_user)
):
    """TODO一覧取得"""
    service = TodoService()
    todos = await service.list_todos(
        user_id=user.id,
        completed=completed,
        search=search,
        sort_by=sortBy,
        order=order,
        limit=limit,
        offset=offset
    )
    return {
        "todos": todos,
        "total": len(todos),
        "limit": limit,
        "offset": offset
    }

@router.get("/{todo_id}")
async def get_todo(
    todo_id: str,
    user: User = Depends(get_current_user)
):
    """TODO詳細取得"""
    service = TodoService()
    todo = await service.get_todo(todo_id, user.id)
    
    if not todo:
        raise HTTPException(status_code=404, detail={
            "error": {
                "code": "TODO_NOT_FOUND",
                "message": "TODOが見つかりません"
            }
        })
    
    return todo

@router.post("/", status_code=201)
async def create_todo(
    data: TodoCreate,
    user: User = Depends(get_current_user)
):
    """TODO作成"""
    service = TodoService()
    todo = await service.create_todo(data, user.id)
    return todo

@router.put("/{todo_id}")
async def update_todo(
    todo_id: str,
    data: TodoUpdate,
    user: User = Depends(get_current_user)
):
    """TODO更新"""
    service = TodoService()
    todo = await service.update_todo(todo_id, data, user.id)
    
    if not todo:
        raise HTTPException(status_code=404, detail={
            "error": {
                "code": "TODO_NOT_FOUND",
                "message": "TODOが見つかりません"
            }
        })
    
    return todo

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: str,
    user: User = Depends(get_current_user)
):
    """TODO削除"""
    service = TodoService()
    success = await service.delete_todo(todo_id, user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail={
            "error": {
                "code": "TODO_NOT_FOUND",
                "message": "TODOが見つかりません"
            }
        })
    
    return {"success": True, "message": "TODOを削除しました"}

@router.patch("/{todo_id}/toggle")
async def toggle_todo(
    todo_id: str,
    user: User = Depends(get_current_user)
):
    """TODO完了/未完了切り替え"""
    service = TodoService()
    todo = await service.toggle_todo(todo_id, user.id)
    
    if not todo:
        raise HTTPException(status_code=404, detail={
            "error": {
                "code": "TODO_NOT_FOUND",
                "message": "TODOが見つかりません"
            }
        })
    
    return todo

@router.get("/stats")
async def get_todo_stats(
    user: User = Depends(get_current_user)
):
    """TODO統計情報取得"""
    service = TodoService()
    stats = await service.get_stats(user.id)
    return stats
```

### 4.2 データモデル（Pydantic）

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    dueDate: Optional[datetime] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: str
    userId: str
    completed: bool
    createdAt: datetime
    updatedAt: datetime

class TodoListResponse(BaseModel):
    todos: list[TodoResponse]
    total: int
    limit: int
    offset: int

class TodoStatsResponse(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
```

### 4.3 サービス層（ビジネスロジック）

```python
from datetime import datetime
from typing import Optional
from backend.app.sys.dal.json_dal import get_dal

class TodoService:
    def __init__(self):
        self.dal = get_dal()
    
    async def list_todos(
        self,
        user_id: str,
        completed: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "createdAt",
        order: str = "desc",
        limit: int = 100,
        offset: int = 0
    ):
        """TODO一覧取得"""
        todos = await self.dal.list("todos", {"userId": user_id})
        
        # フィルタ適用
        if completed is not None:
            todos = [t for t in todos if t['completed'] == completed]
        
        if search:
            todos = [t for t in todos if search.lower() in t['title'].lower() or search.lower() in t.get('description', '').lower()]
        
        # ソート
        reverse = (order == "desc")
        todos.sort(key=lambda t: t.get(sort_by, ''), reverse=reverse)
        
        # ページネーション
        return todos[offset:offset+limit]
    
    async def get_todo(self, todo_id: str, user_id: str):
        """TODO詳細取得"""
        todo = await self.dal.get("todos", todo_id)
        
        if not todo:
            return None
        
        if todo['userId'] != user_id:
            raise HTTPException(status_code=403, detail={
                "error": {
                    "code": "TODO_ACCESS_DENIED",
                    "message": "このTODOにアクセスする権限がありません"
                }
            })
        
        return todo
    
    async def create_todo(self, data: TodoCreate, user_id: str):
        """TODO作成"""
        todo = {
            "id": f"todo_{datetime.utcnow().timestamp()}",
            "userId": user_id,
            "title": data.title,
            "description": data.description,
            "dueDate": data.dueDate.isoformat() if data.dueDate else None,
            "completed": False,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }
        
        await self.dal.create("todos", todo)
        return todo
    
    async def update_todo(self, todo_id: str, data: TodoUpdate, user_id: str):
        """TODO更新"""
        todo = await self.get_todo(todo_id, user_id)
        
        if not todo:
            return None
        
        todo['title'] = data.title
        todo['description'] = data.description
        todo['dueDate'] = data.dueDate.isoformat() if data.dueDate else None
        
        if data.completed is not None:
            todo['completed'] = data.completed
        
        todo['updatedAt'] = datetime.utcnow().isoformat() + "Z"
        
        await self.dal.update("todos", todo_id, todo)
        return todo
    
    async def delete_todo(self, todo_id: str, user_id: str):
        """TODO削除"""
        todo = await self.get_todo(todo_id, user_id)
        
        if not todo:
            return False
        
        await self.dal.delete("todos", todo_id)
        return True
    
    async def toggle_todo(self, todo_id: str, user_id: str):
        """TODO完了/未完了切り替え"""
        todo = await self.get_todo(todo_id, user_id)
        
        if not todo:
            return None
        
        todo['completed'] = not todo['completed']
        todo['updatedAt'] = datetime.utcnow().isoformat() + "Z"
        
        await self.dal.update("todos", todo_id, todo)
        return todo
    
    async def get_stats(self, user_id: str):
        """TODO統計情報取得"""
        todos = await self.dal.list("todos", {"userId": user_id})
        
        total = len(todos)
        completed = sum(1 for t in todos if t['completed'])
        pending = total - completed
        
        now = datetime.utcnow()
        overdue = sum(1 for t in todos if not t['completed'] and t.get('dueDate') and datetime.fromisoformat(t['dueDate'].replace('Z', '+00:00')) < now)
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "overdue": overdue
        }
```

---

## 関連ドキュメント

- [TODOアプリアーキテクチャ設計書](./architecture.md)
- [TODOアプリ画面設計書](./screen-design.md)
- [TODOアプリmanifest.json](./manifest-schema.md)
- [システム共通基盤API設計書](../../sys/02-basic-design/api-design.md)
- [工程1: 要件定義](../01-requirements/)
