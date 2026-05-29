---
name: websys-conventions
description: 'Webシステム開発プロジェクトの技術規約・コーディング規約・ディレクトリ構成。Use when: writing TypeScript, Alpine.js, Bootstrap, Python FastAPI, CSS, implementing DAL, designing APIs, working on websys project.'
argument-hint: '確認したい規約の種類（typescript, alpinejs, bootstrap, python, dal, api, directory）'
---

# Websys プロジェクト規約

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| TypeScript + Vite | メインロジック・ビルドツール |
| Alpine.js | UIの動的制御・リアクティブな振る舞い（15KB軽量） |
| Bootstrap 5 | レスポンシブUI・コンポーネント |
| CSS | カスタムスタイル |
| Python (FastAPI) | REST API・認証・データ処理・静的ファイル配信 |
| DB | JSONファイル（DAL抽象化、RDB移行対応） |
| 通信 | REST API（メイン）+ SSE（リアルタイム通知） |
| 認証 | JWT（httpOnly Cookie）、FastAPIで管理 |

## ディレクトリ構成（完全独立型）

```
websys/
  frontend/                    ← システム共通基盤フロントエンド
    src/
      sys/                     ← システム共通基盤UI
        auth/                  ← 認証UI（ログイン・セッション）
        components/            ← 共通UIコンポーネント
        api/                   ← API通信モジュール
      main.ts                  ← エントリーポイント
    public/
      index.html
    package.json
    tsconfig.json
    vite.config.ts
  backend/                     ← システム共通基盤バックエンド
    app/
      main.py                  ← FastAPIエントリー
      sys/                     ← システム共通基盤
        api/                   ← システム共通API
          auth.py              ← 認証エンドポイント
        dal/                   ← データアクセス層（JSON/RDB抽象化）
        core/                  ← 認証・共通機能
        models/                ← データモデル（Pydantic）
    data/                      ← システム共通データ
      sessions/                ← セッションデータ
      users/                   ← ユーザーデータ
    requirements.txt
  apps/                        ← アプリケーション（完全独立構成）
    app-a/
      manifest.json            ← 必須（アプリメタ情報）
      frontend/                ← アプリA専用フロント
        src/
          components/          ← アプリA固有コンポーネント
          pages/               ← アプリA固有ページ
          main.ts
        package.json
        vite.config.ts
      backend/                 ← アプリA専用バックエンド
        app/
          api/                 ← アプリA固有API
          models/              ← アプリA固有モデル
        data/                  ← アプリA固有JSONデータ（他アプリ直アクセス禁止）
        requirements.txt
      tests/                   ← アプリA専用テスト
        frontend/
        backend/
    app-b/
      manifest.json
      frontend/
      backend/
      tests/
  tests/                       ← システム共通基盤テスト
    frontend/
    backend/
  documents/
    sys/
      01-requirements/
      02-basic-design/
      03-detail-design/
      05-unit-test-report.md
      06-integration-test-report.md
      07-system-test-report.md
      08-release/
    app/
      01-requirements/
      02-basic-design/
      03-detail-design/
      05-unit-test-report.md
      06-integration-test-report.md
      07-system-test-report.md
      08-release/
    progress.json
  issues/
    issues.json
```

## 各技術の規約詳細

- [TypeScript コーディング規約](./references/typescript-conventions.md)
- [Alpine.js 使用規約](./references/alpinejs-conventions.md)
- [Bootstrap カスタマイズ規約](./references/bootstrap-conventions.md)
- [Python / FastAPI 規約](./references/python-conventions.md)
- [DAL パターン](./references/dal-patterns.md)

## manifest.json スキーマ

```json
{
  "name": "string（lowercase-hyphen、アプリID）",
  "version": "string（semver: 1.0.0）",
  "displayName": "string（表示名）",
  "entryPoint": "pages/index",
  "apiPrefix": "/api/app/<name>",
  "requiredPermissions": ["user.read"],
  "description": "string",
  "uiComponents": ["components/dashboard.ts"]
}
```

## REST API 設計規則

- URL は `kebab-case`、名詞（複数形）を使う: `GET /api/users`, `POST /api/apps`
- 認証が必要なエンドポイントは `Authorization: Bearer <JWT>` または Cookie セッション
- エラーレスポンスは統一形式: `{ "error": { "code": "AUTH_FAILED", "message": "..." } }`
- SSE エンドポイント: `GET /api/events`（`Content-Type: text/event-stream`）

## セキュリティ必須事項

### バックエンド（Python FastAPI）
- パスワード: `passlib` の `bcrypt` ハッシュ
- JWT: httpOnly Cookie に格納（JS から読み取り不可）、`python-jose` 使用
- CSRF: 状態変更エンドポイントにCSRFトークン検証を実装
- ファイルパス: ユーザー入力をパスに使う場合は `Path.resolve()` + 許可ディレクトリ確認
- SQL/NoSQLインジェクション: DAL経由のみ、パラメータ化必須

### フロントエンド（TypeScript + Alpine.js）
- XSS: Alpine.js は自動エスケープ。`x-html` 使用時は必ず `DOMPurify` でサニタイズ
- CSRF: API呼び出しに CSRF トークンをヘッダー付与
- 認証: JWT は httpOnly Cookie に保存（localStorage 禁止）
- Content Security Policy (CSP): inline script 禁止
