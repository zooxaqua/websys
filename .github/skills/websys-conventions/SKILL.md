---
name: websys-conventions
description: 'Webシステム開発プロジェクトの技術規約・コーディング規約・ディレクトリ構成。Use when: writing PHP, TypeScript, Python FastAPI, CSS, implementing DAL, designing APIs, working on websys project.'
argument-hint: '確認したい規約の種類（php, typescript, python, dal, api, directory）'
---

# Websys プロジェクト規約

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| PHP | Webアプリ全般（ページレンダリング・Web処理） |
| TypeScript | UIの動的制御・REST APIコール |
| CSS | レイアウト・デザイン（BEM命名） |
| Python (FastAPI) | AI・データ分析などの特定処理 |
| DB | JSONファイル（DAL抽象化、RDB移行対応） |
| 通信 | REST API（メイン）+ SSE（リアルタイム通知） |
| 認証 | PHPセッション（Web画面）+ JWT / httpOnly Cookie（API） |

## ディレクトリ構成

```
websys/
  src/
    system/           ← 共通基盤
      auth/           ← 認証（ログイン・セッション・JWT）
      api/            ← 共通API
      dal/            ← データアクセス層（JSON/RDB抽象化）
      ui/             ← 共通UIコンポーネント
    apps/             ← アプリ配置ルート
      <app-name>/
        manifest.json ← 必須（アプリメタ情報）
        index.php     ← エントリーポイント
        api/          ← アプリ固有API
        data/         ← アプリ固有JSONデータ（他アプリ直アクセス禁止）
  python/             ← FastAPI バックエンド
    src/
    tests/
  tests/
    unit/
    integration/
    system/
  documents/
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

## 各言語の規約詳細

- [PHP コーディング規約](./references/php-conventions.md)
- [TypeScript コーディング規約](./references/typescript-conventions.md)
- [Python / FastAPI 規約](./references/python-conventions.md)
- [DAL パターン](./references/dal-patterns.md)

## manifest.json スキーマ

```json
{
  "name": "string（lowercase-hyphen、アプリID）",
  "version": "string（semver: 1.0.0）",
  "displayName": "string（表示名）",
  "entryPoint": "index.php",
  "apiPrefix": "/api/<name>",
  "requiredPermissions": ["user.read"],
  "description": "string"
}
```

## REST API 設計規則

- URL は `kebab-case`、名詞（複数形）を使う: `GET /api/users`, `POST /api/apps`
- 認証が必要なエンドポイントは `Authorization: Bearer <JWT>` または Cookie セッション
- エラーレスポンスは統一形式: `{ "error": { "code": "AUTH_FAILED", "message": "..." } }`
- SSE エンドポイント: `GET /api/events`（`Content-Type: text/event-stream`）

## セキュリティ必須事項

- パスワード: `password_hash()` (PASSWORD_BCRYPT) / `password_verify()`
- JWT: httpOnly Cookie に格納（JS から読み取り不可）
- 出力エスケープ: PHP では `htmlspecialchars($v, ENT_QUOTES, 'UTF-8')` を全箇所に
- CSRF: 状態変更リクエストにはCSRFトークン検証を実装
- ファイルパス: ユーザー入力をパスに使う場合は `realpath()` + 許可ディレクトリ確認
