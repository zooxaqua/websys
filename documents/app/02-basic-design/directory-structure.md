# ディレクトリ構成設計書（TODOアプリ）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | TODOアプリ（app） |
| 工程 | 工程2: 基本設計 |

---

## 1. TODOアプリディレクトリ構成

```
apps/todo-app/
├── manifest.json                      ← アプリメタ情報
├── icon.png                           ← アプリアイコン（128x128px）
│
├── frontend/                          ← フロントエンド（完全独立）
│   ├── src/
│   │   ├── main.ts                    ← エントリーポイント
│   │   ├── components/                ← Alpine.jsコンポーネント
│   │   │   ├── todo-list.ts           ← TODOリストコンポーネント
│   │   │   ├── todo-add-dialog.ts     ← TODO追加ダイアログ
│   │   │   └── todo-edit-dialog.ts    ← TODO編集ダイアログ
│   │   ├── api/                       ← API呼び出しラッパー
│   │   │   └── todo.ts                ← TODO API呼び出し
│   │   ├── utils/                     ← ユーティリティ
│   │   │   ├── date.ts                ← 日付フォーマット
│   │   │   └── validation.ts          ← バリデーション
│   │   └── styles/                    ← カスタムCSS
│   │       └── app.css                ← アプリ固有スタイル
│   ├── public/
│   │   └── index.html                 ← HTMLテンプレート
│   ├── dist/                          ← ビルド出力（Vite）
│   │   ├── index.html
│   │   └── assets/
│   │       ├── main-[hash].js
│   │       └── main-[hash].css
│   ├── package.json                   ← npm依存関係
│   ├── tsconfig.json                  ← TypeScript設定
│   └── vite.config.ts                 ← Vite設定
│
├── backend/                           ← バックエンド（完全独立）
│   ├── venv/                          ← Python仮想環境（git除外）
│   ├── app/
│   │   ├── main.py                    ← FastAPIエントリーポイント
│   │   ├── api/                       ← APIエンドポイント
│   │   │   └── todos.py               ← TODO CRUD API
│   │   ├── models/                    ← データモデル（Pydantic）
│   │   │   └── todo.py                ← TODOモデル
│   │   ├── services/                  ← ビジネスロジック
│   │   │   └── todo_service.py        ← TODOサービス
│   │   └── utils/                     ← ユーティリティ
│   │       └── dal.py                 ← DAL（システム共通基盤を利用）
│   ├── data/                          ← アプリ固有データ（JSON DB）
│   │   └── todos.json                 ← TODOデータ
│   ├── requirements.txt               ← Python依存関係
│   └── .gitignore                     ← venv/, __pycache__/ 除外
│
└── tests/                             ← テスト（完全独立）
    ├── frontend/
    │   └── unit/
    │       ├── todo-list.test.ts
    │       ├── todo-add-dialog.test.ts
    │       └── todo-edit-dialog.test.ts
    └── backend/
        ├── unit/
        │   ├── test_todos_api.py
        │   └── test_todo_service.py
        └── integration/
            └── test_todos_integration.py
```

---

## 2. フロントエンド（frontend/）

### 2.1 frontend/src/ 構成

| ディレクトリ/ファイル | 役割 |
|---------------------|------|
| `main.ts` | エントリーポイント。Alpine.jsの初期化、コンポーネント登録。 |
| `components/` | Alpine.jsコンポーネント（TODOリスト・追加/編集ダイアログ）。 |
| `api/` | API呼び出しラッパー。`fetch` をラップし、エラーハンドリングを統一。 |
| `utils/` | ユーティリティ関数（日付フォーマット・バリデーション）。 |
| `styles/` | カスタムCSS。Bootstrap 5をベースに拡張。 |

### 2.2 主要ファイルの役割

#### `frontend/src/main.ts`

```typescript
import Alpine from 'alpinejs';
import todoList from './components/todo-list';
import todoAddDialog from './components/todo-add-dialog';
import todoEditDialog from './components/todo-edit-dialog';
import './styles/app.css';

// Alpine.jsコンポーネント登録
Alpine.data('todoList', todoList);
Alpine.data('todoAddDialog', todoAddDialog);
Alpine.data('todoEditDialog', todoEditDialog);

// Alpine.js起動
Alpine.start();
```

#### `frontend/src/components/todo-list.ts`

```typescript
import { getTodos, toggleTodo, deleteTodo } from '../api/todo';

export default () => ({
  todos: [],
  stats: {},
  filter: '',
  search: '',
  
  async init() {
    await this.loadTodos();
    await this.loadStats();
  },
  
  async loadTodos() {
    const params = new URLSearchParams();
    if (this.filter) params.append('completed', this.filter);
    if (this.search) params.append('search', this.search);
    
    this.todos = await getTodos(params.toString());
  },
  
  async loadStats() {
    this.stats = await fetch('/api/todo-app/todos/stats').then(r => r.json());
  },
  
  async toggleTodo(todoId: string) {
    await toggleTodo(todoId);
    await this.loadTodos();
    await this.loadStats();
  },
  
  async deleteTodo(todoId: string) {
    if (!confirm('本当にこのTODOを削除しますか?')) return;
    
    await deleteTodo(todoId);
    await this.loadTodos();
    await this.loadStats();
  },
  
  formatDate(dateStr: string) {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('ja-JP');
  },
  
  isOverdue(dateStr: string) {
    if (!dateStr) return false;
    return new Date(dateStr) < new Date();
  }
});
```

#### `frontend/src/api/todo.ts`

```typescript
export async function getTodos(params: string = ''): Promise<any[]> {
  const response = await fetch(`/api/todo-app/todos?${params}`);
  if (!response.ok) throw new Error('Failed to fetch todos');
  const data = await response.json();
  return data.todos;
}

export async function createTodo(data: any): Promise<any> {
  const response = await fetch('/api/todo-app/todos', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to create todo');
  return response.json();
}

export async function updateTodo(todoId: string, data: any): Promise<any> {
  const response = await fetch(`/api/todo-app/todos/${todoId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  if (!response.ok) throw new Error('Failed to update todo');
  return response.json();
}

export async function deleteTodo(todoId: string): Promise<void> {
  const response = await fetch(`/api/todo-app/todos/${todoId}`, {
    method: 'DELETE'
  });
  if (!response.ok) throw new Error('Failed to delete todo');
}

export async function toggleTodo(todoId: string): Promise<any> {
  const response = await fetch(`/api/todo-app/todos/${todoId}/toggle`, {
    method: 'PATCH'
  });
  if (!response.ok) throw new Error('Failed to toggle todo');
  return response.json();
}
```

### 2.3 ビルド設定（vite.config.ts）

```typescript
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: '.',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5174,  // システム共通基盤とポート被りを避ける
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

---

## 3. バックエンド（backend/）

### 3.1 backend/app/ 構成

| ディレクトリ/ファイル | 役割 |
|---------------------|------|
| `main.py` | FastAPIエントリーポイント。ルーター登録。 |
| `api/` | APIエンドポイント。TODO CRUD処理。 |
| `models/` | データモデル（Pydantic）。リクエスト/レスポンスの型定義。 |
| `services/` | ビジネスロジック。TODO操作・権限チェック。 |
| `utils/` | ユーティリティ。DAL（システム共通基盤を利用）。 |

### 3.2 主要ファイルの役割

#### `backend/app/main.py`

```python
from fastapi import FastAPI
from backend.app.sys.core.middleware import setup_middleware
from apps.todo_app.backend.app.api import todos

app = FastAPI(title="TODOアプリ", version="1.0.0")

# ミドルウェア設定（システム共通基盤）
setup_middleware(app)

# APIルーター登録
app.include_router(todos.router, prefix="/api/todo-app/todos", tags=["todo"])
```

#### `backend/app/api/todos.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from backend.app.sys.core.dependencies import get_current_user
from apps.todo_app.backend.app.models.todo import TodoCreate, TodoUpdate, TodoResponse
from apps.todo_app.backend.app.services.todo_service import TodoService

router = APIRouter()

@router.get("/")
async def list_todos(user: User = Depends(get_current_user)):
    service = TodoService()
    todos = await service.list_todos(user.id)
    return {"todos": todos}

@router.post("/", status_code=201)
async def create_todo(data: TodoCreate, user: User = Depends(get_current_user)):
    service = TodoService()
    todo = await service.create_todo(data, user.id)
    return todo

@router.put("/{todo_id}")
async def update_todo(todo_id: str, data: TodoUpdate, user: User = Depends(get_current_user)):
    service = TodoService()
    todo = await service.update_todo(todo_id, data, user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODOが見つかりません")
    return todo

@router.delete("/{todo_id}")
async def delete_todo(todo_id: str, user: User = Depends(get_current_user)):
    service = TodoService()
    success = await service.delete_todo(todo_id, user.id)
    if not success:
        raise HTTPException(status_code=404, detail="TODOが見つかりません")
    return {"success": True, "message": "TODOを削除しました"}

@router.patch("/{todo_id}/toggle")
async def toggle_todo(todo_id: str, user: User = Depends(get_current_user)):
    service = TodoService()
    todo = await service.toggle_todo(todo_id, user.id)
    if not todo:
        raise HTTPException(status_code=404, detail="TODOが見つかりません")
    return todo
```

#### `backend/app/models/todo.py`

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
```

---

## 4. データ（backend/data/）

### 4.1 TODOデータ（todos.json）

**ファイルパス**: `apps/todo-app/backend/data/todos.json`

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
    }
  ]
}
```

---

## 5. テスト（tests/）

### 5.1 テスト構成

```
tests/
├── frontend/
│   └── unit/
│       ├── todo-list.test.ts           ← TODOリストコンポーネントのテスト
│       ├── todo-add-dialog.test.ts     ← TODO追加ダイアログのテスト
│       └── todo-edit-dialog.test.ts    ← TODO編集ダイアログのテスト
└── backend/
    ├── unit/
    │   ├── test_todos_api.py           ← TODO API単体テスト
    │   └── test_todo_service.py        ← TODOサービス単体テスト
    └── integration/
        └── test_todos_integration.py   ← TODO API結合テスト
```

### 5.2 テスト実行コマンド

| テスト種別 | コマンド |
|-----------|---------|
| フロントエンド単体テスト | `cd apps/todo-app/frontend && npm run test:unit` |
| バックエンド単体テスト | `pytest apps/todo-app/tests/backend/unit/` |
| バックエンド結合テスト | `pytest apps/todo-app/tests/backend/integration/` |

---

## 6. 依存関係管理

### 6.1 フロントエンド（package.json）

```json
{
  "name": "todo-app-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test:unit": "vitest"
  },
  "dependencies": {
    "alpinejs": "^3.13.0",
    "bootstrap": "^5.3.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0"
  }
}
```

### 6.2 バックエンド（requirements.txt）

```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pytest==8.0.0
pytest-asyncio==0.23.0
httpx==0.26.0
```

---

## 関連ドキュメント

- [TODOアプリアーキテクチャ設計書](./architecture.md)
- [TODOアプリAPI設計書](./api-design.md)
- [TODOアプリ画面設計書](./screen-design.md)
- [TODOアプリmanifest.json](./manifest-schema.md)
- [システム共通基盤ディレクトリ構成](../../sys/02-basic-design/directory-structure.md)
- [工程1: 要件定義](../01-requirements/)
