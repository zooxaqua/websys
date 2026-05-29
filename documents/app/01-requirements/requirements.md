# 要件定義書（アプリケーション）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | アプリケーション（app） |
| 技術スタック | TypeScript + Alpine.js + Bootstrap 5 + Python FastAPI |

---

## 1. アプリケーション共通要件

アプリケーションは、システム共通基盤（sys）を利用して構築される独立したWebアプリケーションです。

### 1.1 アプリ構成

| ID | 要件 | 優先度 | 説明 |
|----|------|--------|------|
| FR-APP-001 | 完全独立構成 | 必須 | 各アプリは `frontend/`, `backend/`, `tests/`, `data/` を持つ完全独立構成とする |
| FR-APP-002 | manifest.json定義 | 必須 | アプリのメタ情報をmanifest.jsonで定義する |
| FR-APP-003 | エントリーポイント定義 | 必須 | manifest.jsonでフロントエンドのエントリーポイントを定義する |
| FR-APP-004 | APIプレフィックス定義 | 必須 | manifest.jsonでアプリ固有のAPIプレフィックスを定義する |
| FR-APP-005 | バージョン管理 | 必須 | manifest.jsonでアプリのバージョンを管理する |

### 1.2 システム共通基盤連携

| ID | 要件 | 優先度 | 説明 |
|----|------|--------|------|
| FR-APP-010 | 認証API利用 | 必須 | システム共通基盤の認証API（`/api/sys/auth/me`）を利用する |
| FR-APP-011 | 共通UI部品利用 | 推奨 | システム共通基盤のヘッダー・ナビゲーション・通知UIを利用する |
| FR-APP-012 | 通知API利用 | 推奨 | システム共通基盤の通知API（SSE）を利用する |

### 1.3 データ管理

| ID | 要件 | 優先度 | 説明 |
|----|------|--------|------|
| FR-APP-020 | 独立データ領域 | 必須 | アプリのデータは `apps/<app-name>/backend/data/` に保存する |
| FR-APP-021 | DAL利用 | 必須 | データアクセスはDAL経由で行う |
| FR-APP-022 | 他アプリデータ直接参照禁止 | 必須 | 他のアプリのデータに直接アクセスしない |
| FR-APP-023 | アプリ間データ共有 | 推奨 | 他アプリとデータを共有する場合は、システム共通APIを経由する |

### 1.4 フロントエンド

| ID | 要件 | 優先度 | 説明 |
|----|------|--------|------|
| FR-APP-030 | TypeScript + Alpine.js | 必須 | フロントエンドはTypeScript + Alpine.jsで実装する |
| FR-APP-031 | Bootstrap 5利用 | 必須 | UIデザインはBootstrap 5を利用する |
| FR-APP-032 | レスポンシブデザイン | 推奨 | Bootstrap 5のグリッドシステムでレスポンシブ対応する |
| FR-APP-033 | Viteビルド | 必須 | Viteでビルドし、`frontend/dist/` に出力する |

### 1.5 バックエンド

| ID | 要件 | 優先度 | 説明 |
|----|------|--------|------|
| FR-APP-040 | FastAPI実装 | 必須 | バックエンドはFastAPIで実装する |
| FR-APP-041 | REST API提供 | 必須 | `/api/<app-name>/<endpoint>` 形式でREST APIを提供する |
| FR-APP-042 | JWT認証 | 必須 | システム共通基盤のJWT（httpOnly Cookie）を検証する |
| FR-APP-043 | エラーハンドリング | 必須 | 適切なHTTPステータスコードとエラーメッセージを返す |

---

## 2. 個別アプリケーション要件：TODOアプリ

システムで使用する正式なアプリケーションとして「TODOアプリ」の要件を定義します。

### 2.1 機能要件

| ID | 要件 | 優先度 | 説明 |
|----|------|--------|------|
| FR-TODO-001 | TODO追加 | 必須 | ユーザーが新しいTODOを追加できる |
| FR-TODO-002 | TODO一覧表示 | 必須 | ユーザーのTODO一覧を表示する |
| FR-TODO-003 | TODO編集 | 必須 | TODOのタイトル・内容を編集できる |
| FR-TODO-004 | TODO削除 | 必須 | TODOを削除できる |
| FR-TODO-005 | TODO完了/未完了切り替え | 必須 | TODOの完了状態を切り替えできる |
| FR-TODO-006 | TODOフィルタ表示 | 推奨 | 完了/未完了でTODOをフィルタ表示できる |
| FR-TODO-007 | TODO検索 | 推奨 | タイトル・内容でTODOを検索できる |

### 2.2 非機能要件

| ID | カテゴリ | 要件 | 基準値 |
|----|---------|------|--------|
| NFR-TODO-001 | セキュリティ | ユーザーは自分のTODOのみ参照・編集できる | アクセス制御必須 |
| NFR-TODO-002 | 性能 | TODO一覧表示が1秒以内に完了する | 100件まで |
| NFR-TODO-003 | データ永続化 | TODOデータは `apps/todo-app/backend/data/todos.json` に保存する | JSON形式 |

---

## 3. manifest.json仕様

各アプリケーションは以下の形式でmanifest.jsonを定義する：

```json
{
  "name": "アプリ名（英数字・ハイフン）",
  "displayName": "表示名（日本語可）",
  "version": "1.0.0",
  "description": "アプリの説明",
  "entryPoint": "/apps/<app-name>/",
  "apiPrefix": "/api/<app-name>",
  "icon": "icon.png",
  "author": "作成者名",
  "requiredPermissions": ["read", "write", "admin"],
  "dependencies": []
}
```

### 3.1 フィールド定義

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `name` | ✓ | アプリの識別名（英数字・ハイフン、ディレクトリ名と一致） |
| `displayName` | ✓ | ナビゲーションメニューに表示される名前 |
| `version` | ✓ | セマンティックバージョニング形式（例：1.0.0） |
| `description` | ✓ | アプリの説明文 |
| `entryPoint` | ✓ | フロントエンドのエントリーポイント（URLパス） |
| `apiPrefix` | ✓ | バックエンドAPIのプレフィックス |
| `icon` | − | アプリアイコンのパス（アプリディレクトリからの相対パス） |
| `author` | − | アプリ作成者名 |
| `requiredPermissions` | − | 必要な権限のリスト（read, write, admin等） |
| `dependencies` | − | 依存する他のアプリのリスト |

---

## 4. アプリ開発規約

### 4.1 ディレクトリ構成

```
apps/<app-name>/
├── manifest.json         ← アプリメタ情報
├── frontend/             ← フロントエンド（TypeScript + Alpine.js + Bootstrap）
│   ├── src/
│   │   ├── main.ts      ← エントリーポイント
│   │   ├── components/  ← Alpine.jsコンポーネント
│   │   └── styles/      ← カスタムCSS
│   ├── index.html       ← HTMLテンプレート
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── backend/              ← バックエンド（FastAPI）
│   ├── app/
│   │   ├── main.py      ← FastAPIエントリーポイント
│   │   ├── api/         ← APIエンドポイント
│   │   ├── models/      ← データモデル
│   │   └── dal/         ← データアクセス層
│   ├── data/            ← アプリ固有データ（JSON）
│   └── requirements.txt
└── tests/                ← テスト
    ├── frontend/
    └── backend/
```

### 4.2 コーディング規約

| 項目 | 規約 |
|------|------|
| TypeScript | Prettierでフォーマット、ESLintで静的解析 |
| Python | Blackでフォーマット、Ruffで静的解析 |
| 命名規則 | TypeScript: camelCase、Python: snake_case |
| ファイル名 | TypeScript: kebab-case、Python: snake_case |

### 4.3 API設計規約

| 項目 | 規約 |
|------|------|
| エンドポイント | `/api/<app-name>/<resource>` 形式 |
| HTTPメソッド | GET（取得）、POST（作成）、PUT（更新）、DELETE（削除） |
| レスポンス形式 | JSON `{"data": {...}, "error": null}` |
| エラーレスポンス | JSON `{"data": null, "error": {"code": "...", "message": "..."}}` |
| 認証 | JWT（httpOnly Cookie）必須 |

---

## 5. 非機能要件

### 5.1 セキュリティ

| ID | カテゴリ | 要件 | 基準値 |
|----|---------|------|--------|
| NFR-APP-001 | 認証 | 全APIでJWT認証を実施する | 必須 |
| NFR-APP-002 | 認可 | ユーザーは自分のデータのみアクセスできる | アクセス制御必須 |
| NFR-APP-003 | XSS防止 | 入力値をエスケープして表示する | 必須 |
| NFR-APP-004 | CSRF対策 | 状態変更APIでCSRFトークンを検証する | 必須 |

### 5.2 性能

| ID | カテゴリ | 要件 | 基準値 |
|----|---------|------|--------|
| NFR-APP-010 | レスポンスタイム | API応答時間が100ms以内である | 平均値 |
| NFR-APP-011 | フロントエンド読み込み | 画面初回読み込みが2秒以内である | 平均値 |

### 5.3 保守性

| ID | カテゴリ | 要件 | 基準値 |
|----|---------|------|--------|
| NFR-APP-020 | テストカバレッジ | 単体テストカバレッジが80%以上である | 必須 |
| NFR-APP-021 | コーディング規約 | TypeScript・Pythonのコーディング規約に準拠する | 必須 |
| NFR-APP-022 | ドキュメント | README.mdでアプリの説明・セットアップ手順を記載する | 必須 |

### 5.4 拡張性

| ID | カテゴリ | 要件 | 基準値 |
|----|---------|------|--------|
| NFR-APP-030 | システム共通基盤非依存 | アプリはシステム共通基盤の実装詳細に依存しない | 公開APIのみ利用 |
| NFR-APP-031 | 他アプリ非依存 | アプリは他のアプリに依存しない | 独立動作 |

---

## 6. 対象外事項

以下は本工程の対象外とする：

- 個別アプリの詳細仕様（各アプリごとに定義）
- アプリ固有のAI機能の実装詳細
- 外部サービス連携の詳細仕様
- モバイルアプリ対応
- WebSocket通信（将来検討）
