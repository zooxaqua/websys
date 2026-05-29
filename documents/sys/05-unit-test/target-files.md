# 単体テスト 対象ファイル一覧

## 1. システム共通基盤（sys）

### 1.1 Backend（Python）— 29ファイル

#### API層（6ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 1 | `project/backend/app/sys/api/auth.py` | **High** | 認証・ログイン・ログアウト・トークン検証 | 15 |
| 2 | `project/backend/app/sys/api/users.py` | **High** | ユーザーCRUD・権限チェック | 12 |
| 3 | `project/backend/app/sys/api/apps.py` | Medium | アプリ一覧・登録・削除 | 10 |
| 4 | `project/backend/app/sys/api/notifications.py` | Medium | 通知取得・既読処理 | 8 |
| 5 | `project/backend/app/sys/api/config.py` | Low | 設定取得 | 5 |
| 6 | `project/backend/app/sys/api/health.py` | Low | ヘルスチェック | 3 |

**テスト観点**:
- 正常系: 有効なリクエストで正しいレスポンス
- 異常系: 認証エラー、権限エラー、バリデーションエラー
- 境界値: パラメータの上限・下限

---

#### Core層（5ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 7 | `project/backend/app/sys/core/security.py` | **High** | パスワードハッシュ化・検証・トークン生成 | 15 |
| 8 | `project/backend/app/sys/core/exceptions.py` | Medium | カスタム例外の動作確認 | 8 |
| 9 | `project/backend/app/sys/core/middleware.py` | Medium | リクエスト/レスポンスの変換処理 | 10 |
| 10 | `project/backend/app/sys/core/dependencies.py` | Medium | 依存性注入の動作確認 | 6 |
| 11 | `project/backend/app/sys/core/config.py` | Low | 設定読み込み | 5 |

**テスト観点**:
- セキュリティ: パスワード強度、トークン有効期限
- 異常系: 不正なトークン、設定ファイル欠損
- 境界値: 有効期限の境界、パスワード長

---

#### DAL層（7ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 12 | `project/backend/app/sys/dal/user_dal.py` | **High** | ユーザーCRUD・検索・更新 | 12 |
| 13 | `project/backend/app/sys/dal/session_dal.py` | **High** | セッション管理・有効性チェック | 12 |
| 14 | `project/backend/app/sys/dal/json_dal.py` | **High** | JSONファイル読み書き（基盤） | 15 |
| 15 | `project/backend/app/sys/dal/base_dal.py` | Medium | 基底DALの汎用メソッド | 10 |
| 16 | `project/backend/app/sys/dal/app_dal.py` | Medium | アプリCRUD | 10 |
| 17 | `project/backend/app/sys/dal/notification_dal.py` | Medium | 通知CRUD | 10 |
| 18 | `project/backend/app/sys/dal/base.py` | Low | 基底クラス | 5 |

**テスト観点**:
- 正常系: CRUD操作が正しく動作
- 異常系: ファイルIO失敗、データ不整合
- 境界値: 空配列、最大件数、NULL値

---

#### Models層（4ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 19 | `project/backend/app/sys/models/user.py` | **High** | バリデーション・シリアライズ | 10 |
| 20 | `project/backend/app/sys/models/session.py` | **High** | セッション有効性チェック | 8 |
| 21 | `project/backend/app/sys/models/app.py` | Medium | アプリメタ情報 | 6 |
| 22 | `project/backend/app/sys/models/notification.py` | Medium | 通知データ | 6 |

**テスト観点**:
- 正常系: 有効なデータでインスタンス生成
- 異常系: バリデーションエラー
- 境界値: 文字列長、日時の境界

---

#### Services層（5ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 23 | `project/backend/app/sys/services/auth_service.py` | **High** | 認証ロジック・トークン管理 | 15 |
| 24 | `project/backend/app/sys/services/user_service.py` | **High** | ユーザー管理ビジネスロジック | 12 |
| 25 | `project/backend/app/sys/services/jwt_service.py` | **High** | JWT生成・検証・リフレッシュ | 12 |
| 26 | `project/backend/app/sys/services/app_service.py` | Medium | アプリ登録・管理 | 10 |
| 27 | `project/backend/app/sys/services/notification_service.py` | Medium | 通知送信・既読処理 | 10 |

**テスト観点**:
- 正常系: ビジネスルール通りの処理
- 異常系: 権限不足、データ不整合
- 境界値: トークン有効期限、通知件数上限

---

### 1.2 Frontend（TypeScript）— 13ファイル

#### API層（4ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 28 | `project/frontend/src/sys/api/auth.ts` | **High** | ログイン・ログアウトAPI呼び出し | 10 |
| 29 | `project/frontend/src/sys/api/users.ts` | **High** | ユーザー管理API呼び出し | 8 |
| 30 | `project/frontend/src/sys/api/apps.ts` | Medium | アプリ管理API呼び出し | 6 |
| 31 | `project/frontend/src/sys/api/notifications.ts` | Medium | 通知取得API呼び出し | 6 |

**テスト観点**:
- 正常系: APIレスポンスの正しい処理
- 異常系: ネットワークエラー、401/403/500エラー
- 境界値: タイムアウト、リトライ

---

#### Utils層（4ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 32 | `project/frontend/src/sys/utils/http.ts` | **High** | HTTPリクエスト・エラーハンドリング | 12 |
| 33 | `project/frontend/src/sys/utils/fetch.ts` | **High** | Fetch APIラッパー | 10 |
| 34 | `project/frontend/src/sys/utils/storage.ts` | Medium | LocalStorage操作 | 8 |
| 35 | `project/frontend/src/sys/utils/validation.ts` | Medium | フォームバリデーション | 10 |

**テスト観点**:
- 正常系: ユーティリティ関数の正しい動作
- 異常系: NULL値、undefined、不正な型
- 境界値: 文字列長、配列サイズ

---

#### Components層（2ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 36 | `project/frontend/src/sys/components/header.ts` | Medium | ヘッダー表示・ログアウト | 6 |
| 37 | `project/frontend/src/sys/components/navigation.ts` | Medium | ナビゲーション表示・遷移 | 6 |

**テスト観点**:
- 正常系: コンポーネントの正しいレンダリング
- 異常系: データ欠損時のフォールバック
- 境界値: 長いユーザー名、多数のメニュー項目

---

#### Pages層（4ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 38 | `project/frontend/src/sys/pages/login.ts` | **High** | ログインフォーム・エラー表示 | 10 |
| 39 | `project/frontend/src/sys/pages/portal.ts` | Medium | ポータル画面・アプリ一覧 | 8 |
| 40 | `project/frontend/src/sys/pages/apps.ts` | Medium | アプリ管理画面 | 8 |
| 41 | `project/frontend/src/sys/pages/users.ts` | Medium | ユーザー管理画面 | 8 |

**テスト観点**:
- 正常系: ページのライフサイクル・データ取得
- 異常系: API失敗時のエラー表示
- 境界値: 空データ、大量データ

---

#### その他（1ファイル）
| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 42 | `project/frontend/src/sys/main.ts` | Low | エントリーポイント・初期化 | 5 |

**テスト観点**:
- 正常系: アプリケーションの正しい起動
- 異常系: 初期化失敗時の処理

---

### 1.3 システム共通基盤サマリー

| カテゴリ | ファイル数 | 推定TC合計 |
|---------|-----------|-----------|
| **Backend API** | 6 | 53 |
| **Backend Core** | 5 | 44 |
| **Backend DAL** | 7 | 74 |
| **Backend Models** | 4 | 30 |
| **Backend Services** | 5 | 59 |
| **Frontend API** | 4 | 30 |
| **Frontend Utils** | 4 | 40 |
| **Frontend Components** | 2 | 12 |
| **Frontend Pages** | 4 | 34 |
| **Frontend Other** | 1 | 5 |
| **合計** | **42** | **381** |

---

## 2. TODOアプリ（app）

### 2.1 Backend（Python）— 4ファイル

| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 43 | `project/apps/todo-app/backend/app/models/todo.py` | **High** | TODOデータモデル・バリデーション | 8 |
| 44 | `project/apps/todo-app/backend/app/dal/todo_dal.py` | **High** | TODO CRUD・検索・フィルタ | 12 |
| 45 | `project/apps/todo-app/backend/app/services/todo_service.py` | **High** | TODO作成・更新・削除・完了切替 | 15 |
| 46 | `project/apps/todo-app/backend/app/api/todos.py` | **High** | TODO API エンドポイント | 12 |

**テスト観点**:
- 正常系: TODO CRUD操作、完了/未完了切替
- 異常系: 認証エラー、権限エラー、タイトル空白
- 境界値: タイトル長（0, 1, 100, 101文字）、TODO件数（0, 1, 1000件）

---

### 2.2 Frontend（TypeScript）— 1ファイル

| # | ファイルパス | 優先度 | テスト観点 | 推定TC数 |
|---|------------|-------|-----------|---------|
| 47 | `project/apps/todo-app/frontend/src/main.ts` | **High** | TODO UI・イベントハンドリング | 10 |

**テスト観点**:
- 正常系: TODO追加・削除・完了チェック
- 異常系: API失敗時のエラー表示
- 境界値: 空入力、長いタイトル

---

### 2.3 TODOアプリサマリー

| カテゴリ | ファイル数 | 推定TC合計 |
|---------|-----------|-----------|
| **Backend Models** | 1 | 8 |
| **Backend DAL** | 1 | 12 |
| **Backend Services** | 1 | 15 |
| **Backend API** | 1 | 12 |
| **Frontend** | 1 | 10 |
| **合計** | **5** | **57** |

---

## 3. 全体サマリー

| カテゴリ | ファイル数 | 推定TC合計 |
|---------|-----------|-----------|
| **システム共通基盤** | 42 | 381 |
| **TODOアプリ** | 5 | 57 |
| **総合計** | **47** | **438** |

---

## 4. 優先度別内訳

| 優先度 | ファイル数 | 推定TC合計 | 備考 |
|-------|-----------|-----------|------|
| **High** | 20 | 233 | 認証・データアクセス・ビジネスロジック |
| **Medium** | 22 | 180 | API・画面・通知 |
| **Low** | 5 | 25 | 設定・ヘルスチェック・初期化 |

---

## 5. テスト実装の推奨順序

### フェーズ1: 基盤層（High優先度）
1. **Security & Auth**（1-2週目）
   - `core/security.py`
   - `services/auth_service.py`
   - `services/jwt_service.py`
   - `api/auth.py`
   - `frontend/api/auth.ts`
   - `frontend/pages/login.ts`

2. **データアクセス層**（2-3週目）
   - `dal/json_dal.py`
   - `dal/user_dal.py`
   - `dal/session_dal.py`
   - `models/user.py`
   - `models/session.py`

3. **ビジネスロジック層**（3-4週目）
   - `services/user_service.py`
   - `api/users.py`
   - `frontend/api/users.ts`
   - `frontend/utils/http.ts`
   - `frontend/utils/fetch.ts`

### フェーズ2: アプリケーション層（High優先度）
4. **TODOアプリ**（4-5週目）
   - `apps/todo-app/backend/models/todo.py`
   - `apps/todo-app/backend/dal/todo_dal.py`
   - `apps/todo-app/backend/services/todo_service.py`
   - `apps/todo-app/backend/api/todos.py`
   - `apps/todo-app/frontend/src/main.ts`

### フェーズ3: 残りの機能（Medium/Low優先度）
5. **その他機能**（5-6週目）
   - アプリ管理（`app_service.py`, `api/apps.py`）
   - 通知（`notification_service.py`, `api/notifications.py`）
   - 画面コンポーネント（`components/*`, `pages/*`）
   - ユーティリティ（`utils/*`）

---

## 6. テスト観点の詳細例

### 6.1 正常系テスト
- **目的**: 仕様通りの動作を確認
- **例**:
  - ログイン成功（正しい認証情報）
  - TODO作成成功（有効なタイトル）
  - セッション有効性チェック（期限内）

### 6.2 異常系テスト
- **目的**: エラーハンドリングの確認
- **例**:
  - ログイン失敗（誤ったパスワード）
  - TODO作成失敗（タイトル空白）
  - セッション無効（期限切れ）
  - 権限エラー（他人のTODO操作）
  - ネットワークエラー（API失敗）

### 6.3 境界値テスト
- **目的**: 境界条件での動作確認
- **例**:
  - タイトル長: 0文字、1文字、100文字、101文字
  - TODO件数: 0件、1件、1000件
  - セッション期限: 期限切れ1秒前、期限切れ、期限切れ1秒後
  - パスワード長: 7文字（下限未満）、8文字（下限）、72文字（上限）、73文字（超過）

---

## 7. 推定工数

| フェーズ | ファイル数 | 推定TC数 | 推定工数 |
|---------|-----------|---------|---------|
| フェーズ1（基盤層） | 15 | 140 | 3-4週間 |
| フェーズ2（アプリ層） | 5 | 57 | 1-2週間 |
| フェーズ3（その他） | 27 | 241 | 4-5週間 |
| **合計** | **47** | **438** | **8-11週間** |

**前提条件**:
- 1人・1日あたり: 5-8テストケース実装
- カバレッジ確認・修正: 各フェーズ終了時に1週間

---

## 8. 参考資料

- システムテスト戦略: `documents/sys/05-unit-test/test-strategy.md`
- アプリテスト戦略: `documents/app/05-unit-test/test-strategy.md`
- ディレクトリ構造: `documents/sys/05-unit-test/directory-structure.md`
- 詳細設計書: `documents/sys/03-detail-design/class-design.md`
