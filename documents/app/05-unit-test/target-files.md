# TODOアプリ 単体テスト 対象ファイル一覧

## 1. 概要

TODOアプリケーション専用コード（`project/apps/todo-app/`）の単体テスト対象ファイルを定義する。  
システム共通基盤（sys）は **モック化** し、アプリ固有ロジックに焦点を当てる。

---

## 2. テスト対象範囲

### 2.1 対象ファイル数
- **Backend（Python）**: 4ファイル
- **Frontend（TypeScript）**: 1ファイル
- **合計**: 5ファイル

### 2.2 対象外
- システム共通基盤（sys）のコード（別途システム側でテスト済み）
- エントリーポイント（`main.py`, `main.ts`）
- ビルド設定ファイル（`vite.config.ts`, `tsconfig.json`）
- データファイル（`data/todos.json`）

---

## 3. Backend（Python）— 4ファイル

### 3.1 API層（1ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 1 | `project/apps/todo-app/backend/app/api/todos.py` | **High** | TODO CRUD・バリデーション・権限チェック | 15 |

**テスト観点**:
- **正常系**: 
  - TODO作成（POST `/api/todos`）
  - TODO一覧取得（GET `/api/todos`）
  - TODO更新（PUT `/api/todos/{id}`）
  - TODO削除（DELETE `/api/todos/{id}`）
  - TODO完了切り替え（PATCH `/api/todos/{id}/toggle`）
- **異常系**: 
  - 認証エラー（401）
  - 権限エラー（403: 他人のTODOを操作）
  - バリデーションエラー（400: タイトル空、長すぎる）
  - 存在しないTODO（404）
- **境界値**: 
  - タイトル長（0, 1, 100, 101文字）
  - ページネーション（limit: 0, 1, 100, 101, offset: -1, 0, 1000）

**テストケース例**:
- TC-TODO-API-001: `POST /api/todos` with valid data → 201 Created
- TC-TODO-API-002: `POST /api/todos` with empty title → 400 Bad Request
- TC-TODO-API-003: `POST /api/todos` without auth → 401 Unauthorized
- TC-TODO-API-004: `GET /api/todos` → 200 OK with list
- TC-TODO-API-005: `PUT /api/todos/{id}` by owner → 200 OK
- TC-TODO-API-006: `PUT /api/todos/{id}` by other user → 403 Forbidden
- TC-TODO-API-007: `DELETE /api/todos/{id}` → 204 No Content
- TC-TODO-API-008: `PATCH /api/todos/{id}/toggle` → 200 OK

---

### 3.2 DAL層（1ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 2 | `project/apps/todo-app/backend/app/dal/todo_dal.py` | **High** | TODO CRUD・ファイルIO | 12 |

**テスト観点**:
- **正常系**: 
  - `create(todo)` → TODOを保存、IDを返す
  - `get(id)` → IDで検索、TODOを返す
  - `list(user_id, limit, offset)` → ユーザーのTODO一覧を返す
  - `update(todo)` → TODOを更新
  - `delete(id)` → TODOを削除
- **異常系**: 
  - `get(non_existent_id)` → None
  - ファイルIO失敗（モック化）
- **境界値**: 
  - 空リスト、単一TODO、大量TODO（1000件）

**テストケース例**:
- TC-TODO-DAL-001: `create()` saves TODO to JSON file
- TC-TODO-DAL-002: `get(id)` returns correct TODO
- TC-TODO-DAL-003: `get(non_existent_id)` returns None
- TC-TODO-DAL-004: `list(user_id)` returns only user's TODOs
- TC-TODO-DAL-005: `list(limit=10, offset=0)` returns paginated results
- TC-TODO-DAL-006: `update()` modifies existing TODO
- TC-TODO-DAL-007: `delete(id)` removes TODO from file

---

### 3.3 Models層（1ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 3 | `project/apps/todo-app/backend/app/models/todo.py` | **High** | バリデーション・シリアライズ | 10 |

**テスト観点**:
- **正常系**: 
  - 有効なデータでインスタンス生成
  - `dict()` でシリアライズ
  - `model_validate()` でデシリアライズ
- **異常系**: 
  - タイトル空（ValidationError）
  - タイトル長超過（ValidationError）
  - 不正な型（ValidationError）
- **境界値**: 
  - タイトル長（0, 1, 100, 101文字）

**テストケース例**:
- TC-TODO-MODEL-001: Valid data → instance created
- TC-TODO-MODEL-002: Empty title → ValidationError
- TC-TODO-MODEL-003: Title too long (101 chars) → ValidationError
- TC-TODO-MODEL-004: `dict()` returns correct structure
- TC-TODO-MODEL-005: `model_validate(dict)` deserializes correctly

---

### 3.4 Services層（1ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 4 | `project/apps/todo-app/backend/app/services/todo_service.py` | **High** | ビジネスロジック・権限チェック | 15 |

**テスト観点**:
- **正常系**: 
  - `create_todo(title, user_id)` → TODO作成
  - `get_user_todos(user_id)` → ユーザーのTODO一覧取得
  - `update_todo(id, data, user_id)` → TODO更新
  - `delete_todo(id, user_id)` → TODO削除
  - `toggle_completed(id, user_id)` → 完了状態切り替え
- **異常系**: 
  - 認証なし（PermissionError）
  - 他人のTODO操作（PermissionError）
  - 存在しないTODO（NotFoundError）
  - タイトルバリデーションエラー（ValueError）
- **境界値**: 
  - タイトル長（0, 1, 100, 101文字）

**テストケース例**:
- TC-TODO-SERVICE-001: `create_todo()` with valid data → success
- TC-TODO-SERVICE-002: `create_todo()` with empty title → ValueError
- TC-TODO-SERVICE-003: `create_todo()` without auth → PermissionError
- TC-TODO-SERVICE-004: `toggle_completed()` by owner → success
- TC-TODO-SERVICE-005: `toggle_completed()` by other user → PermissionError
- TC-TODO-SERVICE-006: `update_todo()` with valid data → success
- TC-TODO-SERVICE-007: `delete_todo()` by owner → success

---

## 4. Frontend（TypeScript）— 1ファイル

### 4.1 エントリーポイント（1ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 5 | `project/apps/todo-app/frontend/src/main.ts` | Medium | Alpine.js初期化・APIクライアント | 8 |

**テスト観点**:
- **正常系**: 
  - Alpine.js コンポーネントの初期化
  - TODO一覧取得API呼び出し
  - TODO作成API呼び出し
  - TODO更新API呼び出し
  - TODO削除API呼び出し
- **異常系**: 
  - API失敗時のエラーハンドリング
  - 認証エラー時のリダイレクト
- **境界値**: 
  - 空リスト、大量TODO

**テストケース例**:
- TC-TODO-FRONT-001: Alpine component initializes correctly
- TC-TODO-FRONT-002: `loadTodos()` fetches and displays TODOs
- TC-TODO-FRONT-003: `createTodo()` sends POST request
- TC-TODO-FRONT-004: `toggleTodo()` sends PATCH request
- TC-TODO-FRONT-005: API error displays error message
- TC-TODO-FRONT-006: 401 error redirects to login

---

## 5. システム共通基盤のモック化

### 5.1 モック対象
TODOアプリは システム共通基盤に直接依存しないが、以下をモック化：

| 対象 | モック方法 | 理由 |
|------|-----------|------|
| **認証チェック** | `user_service.is_authenticated()` をモック | テストデータ簡略化 |
| **JSONファイルIO** | `unittest.mock.mock_open()` | 環境依存排除 |
| **時刻取得** | `freezegun.freeze_time()` | テストの再現性確保 |
| **外部API** | `responses` パッケージ（不要：TODOアプリは外部API不使用） | - |

### 5.2 フィクスチャ
```
project/apps/todo-app/tests/unit/inputs/fixtures/
└── todos.json          ← テストTODOデータ

{
  "todos": [
    {
      "id": "todo-001",
      "title": "買い物",
      "user_id": "user-001",
      "completed": false,
      "created_at": "2026-05-29T10:00:00Z"
    },
    {
      "id": "todo-002",
      "title": "洗濯",
      "user_id": "user-001",
      "completed": true,
      "created_at": "2026-05-28T09:00:00Z"
    }
  ]
}
```

---

## 6. テスト実施順序

優先度順にテストを実施する：

1. **High 優先度**（合計4ファイル）
   - `models/todo.py`（依存なし）
   - `dal/todo_dal.py`（models に依存）
   - `services/todo_service.py`（dal, models に依存）
   - `api/todos.py`（services に依存）

2. **Medium 優先度**（1ファイル）
   - `frontend/src/main.ts`

---

## 7. 推定テストケース数

| レイヤー | ファイル数 | 推定TC数 |
|---------|----------|---------|
| **API** | 1 | 15 |
| **DAL** | 1 | 12 |
| **Models** | 1 | 10 |
| **Services** | 1 | 15 |
| **Frontend** | 1 | 8 |
| **合計** | **5** | **60** |

---

## 8. 承認基準（個別）

- [ ] 全5ファイルのテストが実装済み
- [ ] 全テストが PASS（FAIL が 0件）
- [ ] MCDC カバレッジ 100%（Backend: pytest-cov, Frontend: vitest）
- [ ] 境界値テストがすべて実装・PASS
- [ ] 重大バグ（Critical/High）が 0件
- [ ] テスト結果レポートが完成（`documents/app/05-unit-test-report.md`）

---

## 9. 参照ドキュメント

- `documents/common/05-unit-test/test-strategy.md` — テスト戦略（共通）
- `documents/common/05-unit-test/directory-structure.md` — ディレクトリ構造（共通）
- `documents/common/05-unit-test/tools-and-frameworks.md` — ツール詳細（共通）
- `documents/common/05-unit-test/check-program-spec.md` — チェックプログラム仕様（共通）
- `documents/app/03-detail-design/class-design.md` — 詳細設計（TODOアプリ）
