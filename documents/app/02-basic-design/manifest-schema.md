# manifest.json 設計書（TODOアプリ）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | TODOアプリ（app） |
| 工程 | 工程2: 基本設計 |

---

## 1. TODOアプリ manifest.json

### 1.1 完全版 manifest.json

**ファイルパス**: `apps/todo-app/manifest.json`

```json
{
  "name": "todo-app",
  "displayName": "TODO管理",
  "version": "1.0.0",
  "description": "タスクの追加・編集・削除・完了管理を行うアプリケーション",
  "entryPoint": "/apps/todo-app/",
  "apiPrefix": "/api/todo-app",
  "icon": "icon.png",
  "author": "System Team",
  "requiredPermissions": ["read", "write"],
  "dependencies": [],
  "metadata": {
    "category": "productivity",
    "tags": ["task", "todo", "management"],
    "supportedLanguages": ["ja"],
    "minSystemVersion": "1.0.0"
  }
}
```

---

## 2. フィールド詳細

### 2.1 必須フィールド

| フィールド | 値 | 説明 |
|-----------|-----|------|
| `name` | `"todo-app"` | アプリの識別名。ディレクトリ名と一致。 |
| `displayName` | `"TODO管理"` | ナビゲーションメニュー・ポータルページに表示される名前。 |
| `version` | `"1.0.0"` | セマンティックバージョニング形式。 |
| `description` | `"タスクの追加・編集・削除・完了管理を行うアプリケーション"` | アプリの説明文。ポータルページのアプリカードに表示。 |
| `entryPoint` | `"/apps/todo-app/"` | フロントエンドのエントリーポイント（URLパス）。 |
| `apiPrefix` | `"/api/todo-app"` | バックエンドAPIのプレフィックス。 |

### 2.2 オプションフィールド

| フィールド | 値 | 説明 |
|-----------|-----|------|
| `icon` | `"icon.png"` | アプリアイコンのパス。`apps/todo-app/icon.png` に配置。 |
| `author` | `"System Team"` | アプリ作成者名。 |
| `requiredPermissions` | `["read", "write"]` | 必要な権限。一般ユーザーでも利用可能。 |
| `dependencies` | `[]` | 依存する他のアプリ。TODOアプリは単独で動作するため空配列。 |
| `metadata` | `{...}` | アプリ固有のメタデータ。 |

### 2.3 metadata フィールド

| フィールド | 値 | 説明 |
|-----------|-----|------|
| `category` | `"productivity"` | アプリのカテゴリ。生産性向上アプリ。 |
| `tags` | `["task", "todo", "management"]` | 検索用タグ。 |
| `supportedLanguages` | `["ja"]` | 対応言語。日本語のみ。 |
| `minSystemVersion` | `"1.0.0"` | 最低限必要なシステムバージョン。 |

---

## 3. バリデーション確認

### 3.1 必須項目チェック

| 項目 | チェック結果 |
|------|------------|
| `name` 存在 | ✓ `"todo-app"` |
| `displayName` 存在 | ✓ `"TODO管理"` |
| `version` 存在 | ✓ `"1.0.0"` |
| `description` 存在 | ✓ （説明文あり） |
| `entryPoint` 存在 | ✓ `"/apps/todo-app/"` |
| `apiPrefix` 存在 | ✓ `"/api/todo-app"` |

### 3.2 形式チェック

| 項目 | 形式 | チェック結果 |
|------|------|------------|
| `name` | 英小文字・数字・ハイフン | ✓ `todo-app` |
| `version` | セマンティックバージョニング | ✓ `1.0.0` |
| `entryPoint` | `/apps/<name>/` 形式 | ✓ `/apps/todo-app/` |
| `apiPrefix` | `/api/<name>` 形式 | ✓ `/api/todo-app` |

### 3.3 ディレクトリ名一致チェック

| 項目 | 確認 |
|------|------|
| ディレクトリ名 | `apps/todo-app/` |
| manifest.json の `name` | `"todo-app"` |
| 一致 | ✓ |

---

## 4. アイコン仕様

### 4.1 アイコンファイル

**ファイルパス**: `apps/todo-app/icon.png`

**仕様**:
- サイズ: 128x128px
- フォーマット: PNG
- 背景: 透過推奨

**デザイン案**:
- チェックボックスとタスクリストのアイコン
- カラー: 青系（Bootstrap primary色）

---

## 5. システム側での manifest.json 利用

### 5.1 読み込みタイミング

- システム起動時に `apps/*/manifest.json` を自動読み込み
- アプリ管理画面で「再読み込み」ボタンをクリック時

### 5.2 利用箇所

| 利用箇所 | 利用フィールド |
|---------|--------------|
| ナビゲーションメニュー | `displayName`, `icon`, `entryPoint` |
| ポータルページのアプリカード | `displayName`, `icon`, `description`, `entryPoint` |
| アプリ管理画面 | `name`, `displayName`, `version`, `enabled` |
| APIルーティング | `apiPrefix` |
| 権限チェック | `requiredPermissions` |

### 5.3 有効化・無効化制御

**backend/data/apps.json に登録**:

```json
{
  "apps": [
    {
      "id": "todo-app",
      "name": "TODO管理",
      "version": "1.0.0",
      "enabled": true,
      "manifest_path": "apps/todo-app/manifest.json",
      "lastUpdated": "2026-05-28T10:00:00Z"
    }
  ]
}
```

- 管理画面で `enabled: true` に設定 → ナビゲーションメニュー・ポータルに表示
- 管理画面で `enabled: false` に設定 → 非表示、APIアクセス拒否

---

## 6. 開発者向けチェックリスト

- [x] `name` がディレクトリ名 `todo-app` と一致している
- [x] `name` が英小文字・数字・ハイフンのみ使用している
- [x] `version` がセマンティックバージョニング形式（`1.0.0`）
- [x] `entryPoint` が `/apps/todo-app/` 形式
- [x] `apiPrefix` が `/api/todo-app` 形式
- [x] `description` が200文字以内
- [x] `icon.png` ファイルが `apps/todo-app/` に配置されている
- [x] 必須フィールドがすべて記載されている

---

## 関連ドキュメント

- [TODOアプリアーキテクチャ設計書](./architecture.md)
- [TODOアプリAPI設計書](./api-design.md)
- [TODOアプリ画面設計書](./screen-design.md)
- [TODOアプリディレクトリ構成](./directory-structure.md)
- [システム共通基盤manifest.jsonスキーマ](../../sys/02-basic-design/manifest-schema.md)
- [工程1: 要件定義](../01-requirements/)
