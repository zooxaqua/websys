# ディレクトリ構成設計書（システム共通基盤）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | システム共通基盤（sys） |
| 工程 | 工程2: 基本設計 |

---

## 1. 全体ディレクトリ構成

```
websys/
├── agents.md                          ← エージェント構成定義
├── README.md                          ← プロジェクト概要
│
├── .github/                           ← GitHub設定・CI/CD・チェックプログラム
│   ├── agents/                        ← エージェント定義
│   ├── skills/                        ← スキル定義
│   ├── prompts/                       ← プロンプトテンプレート
│   └── checks/                        ← 工程チェックプログラム
│       └── common/
│           ├── phase-01-check.py      ← 工程1チェック
│           ├── phase-02-check.py      ← 工程2チェック
│           └── ...
│
├── requests/                          ← ユーザー要求仕様・議事録
│   └── minutes.md
│
├── documents/                         ← 設計書・テストレポート
│   ├── progress.json                  ← 工程進捗管理（process-manager）
│   ├── sys/                           ← システム共通基盤の設計書
│   │   ├── 01-requirements/           ← 工程1: 要件定義
│   │   ├── 02-basic-design/           ← 工程2: 基本設計
│   │   ├── 03-detail-design/          ← 工程3: 詳細設計
│   │   ├── 05-unit-test-report.md     ← 工程5: 単体評価レポート
│   │   ├── 06-integration-test-report.md  ← 工程6: 結合評価レポート
│   │   ├── 07-system-test-report.md   ← 工程7: システム評価レポート
│   │   └── 08-release/                ← 工程8: リリース
│   └── app/                           ← アプリケーションの設計書
│       ├── 01-requirements/
│       ├── 02-basic-design/
│       ├── 03-detail-design/
│       ├── 05-unit-test-report.md
│       ├── 06-integration-test-report.md
│       ├── 07-system-test-report.md
│       └── 08-release/
│
├── frontend/                          ← システム共通基盤フロントエンド
│   ├── src/
│   │   └── sys/                       ← システム共通基盤UI
│   │       ├── main.ts                ← エントリーポイント
│   │       ├── components/            ← 共通コンポーネント（Alpine.js）
│   │       │   ├── header.ts          ← ヘッダーコンポーネント
│   │       │   ├── navigation.ts      ← ナビゲーションメニュー
│   │       │   ├── notification.ts    ← 通知コンポーネント
│   │       │   └── portal.ts          ← ポータルページ
│   │       ├── pages/                 ← ページコンポーネント
│   │       │   ├── login.ts           ← ログイン画面
│   │       │   ├── users.ts           ← ユーザー管理画面
│   │       │   └── apps.ts            ← アプリ管理画面
│   │       ├── api/                   ← API呼び出しラッパー
│   │       │   ├── auth.ts            ← 認証API
│   │       │   ├── users.ts           ← ユーザー管理API
│   │       │   └── apps.ts            ← アプリ管理API
│   │       ├── utils/                 ← ユーティリティ
│   │       │   ├── http.ts            ← HTTPクライアント
│   │       │   └── validation.ts      ← バリデーション
│   │       └── styles/                ← スタイル（CSS）
│   │           └── main.css           ← メインスタイル
│   ├── public/                        ← 静的ファイル
│   │   ├── index.html                 ← HTMLテンプレート
│   │   └── favicon.ico
│   ├── dist/                          ← ビルド出力（Vite）
│   ├── package.json                   ← npm依存関係
│   ├── tsconfig.json                  ← TypeScript設定
│   └── vite.config.ts                 ← Vite設定
│
├── backend/                           ← システム共通基盤バックエンド
│   ├── venv/                          ← Python仮想環境（git除外）
│   ├── app/
│   │   └── sys/                       ← システム共通基盤
│   │       ├── main.py                ← FastAPIエントリーポイント
│   │       ├── api/                   ← APIエンドポイント
│   │       │   ├── __init__.py
│   │       │   ├── auth.py            ← 認証API
│   │       │   ├── users.py           ← ユーザー管理API
│   │       │   ├── apps.py            ← アプリ管理API
│   │       │   └── notifications.py   ← 通知API
│   │       ├── core/                  ← コア機能
│   │       │   ├── __init__.py
│   │       │   ├── config.py          ← 設定管理
│   │       │   ├── security.py        ← セキュリティ（JWT・パスワード）
│   │       │   ├── dependencies.py    ← FastAPI依存関係
│   │       │   └── middleware.py      ← ミドルウェア
│   │       ├── dal/                   ← データアクセス層（DAL）
│   │       │   ├── __init__.py
│   │       │   ├── base.py            ← DAL抽象クラス
│   │       │   ├── json_dal.py        ← JSON DB実装
│   │       │   └── sql_dal.py         ← RDB実装（将来対応）
│   │       ├── models/                ← データモデル（Pydantic）
│   │       │   ├── __init__.py
│   │       │   ├── user.py            ← ユーザーモデル
│   │       │   ├── app.py             ← アプリモデル
│   │       │   └── notification.py    ← 通知モデル
│   │       └── utils/                 ← ユーティリティ
│   │           ├── __init__.py
│   │           └── manifest_loader.py ← manifest.json読み込み
│   ├── data/                          ← システム共通データ（JSON DB）
│   │   ├── users.json                 ← ユーザー情報
│   │   ├── sessions/                  ← セッション情報
│   │   ├── apps.json                  ← アプリ設定
│   │   └── config.json                ← システム設定
│   ├── logs/                          ← ログファイル
│   ├── requirements.txt               ← Python依存関係
│   ├── pyproject.toml                 ← Python プロジェクト設定
│   └── .gitignore                     ← venv/, __pycache__/ 除外
│
├── apps/                              ← アプリケーション（完全独立構成）
│   └── <app-name>/                    ← 各アプリ
│       ├── manifest.json              ← アプリメタ情報
│       ├── frontend/                  ← アプリ専用フロントエンド
│       │   ├── src/
│       │   │   ├── main.ts            ← エントリーポイント
│       │   │   ├── components/        ← Alpine.jsコンポーネント
│       │   │   ├── api/               ← API呼び出しラッパー
│       │   │   └── styles/            ← カスタムCSS
│       │   ├── public/
│       │   │   └── index.html
│       │   ├── dist/                  ← ビルド出力
│       │   ├── package.json
│       │   ├── tsconfig.json
│       │   └── vite.config.ts
│       ├── backend/                   ← アプリ専用バックエンド
│       │   ├── app/
│       │   │   ├── main.py            ← FastAPIエントリーポイント
│       │   │   ├── api/               ← アプリ固有API
│       │   │   ├── models/            ← アプリ固有モデル
│       │   │   └── utils/             ← ユーティリティ
│       │   ├── data/                  ← アプリ固有データ（JSON DB）
│       │   └── requirements.txt
│       └── tests/                     ← アプリ専用テスト
│           ├── frontend/
│           │   └── unit/
│           └── backend/
│               ├── unit/
│               └── integration/
│
├── tests/                             ← システム共通基盤テスト
│   ├── frontend/
│   │   ├── unit/                      ← 単体テスト（Vitest）
│   │   └── e2e/                       ← E2Eテスト（Playwright）
│   └── backend/
│       ├── unit/                      ← 単体テスト（pytest）
│       └── integration/               ← 結合テスト（pytest）
│
├── issues/                            ← 課題管理（issue-manager）
│   └── issues.json
│
├── .gitignore                         ← Git無視設定
└── .env.example                       ← 環境変数サンプル
```

---

## 2. システム共通基盤（frontend/）

### 2.1 frontend/src/sys/ 構成

| ディレクトリ/ファイル | 役割 |
|---------------------|------|
| `main.ts` | エントリーポイント。Alpine.jsの初期化、ルーター設定。 |
| `components/` | 共通コンポーネント（ヘッダー・ナビゲーション・通知等）。Alpine.jsで実装。 |
| `pages/` | ページコンポーネント（ログイン・ユーザー管理・アプリ管理・ポータル）。 |
| `api/` | API呼び出しラッパー。`fetch` をラップし、エラーハンドリングを統一。 |
| `utils/` | ユーティリティ関数（HTTPクライアント・バリデーション・日付フォーマット等）。 |
| `styles/` | カスタムCSS。Bootstrap 5をベースに拡張。 |

### 2.2 ビルド設定（vite.config.ts）

```typescript
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  root: 'frontend',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './frontend/src'),
      '@sys': path.resolve(__dirname, './frontend/src/sys'),
    },
  },
  server: {
    port: 5173,
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

## 3. システム共通基盤（backend/）

### 3.1 backend/app/sys/ 構成

| ディレクトリ/ファイル | 役割 |
|---------------------|------|
| `main.py` | FastAPIエントリーポイント。ルーター登録、ミドルウェア設定、静的ファイル配信。 |
| `api/` | APIエンドポイント。各リソース（認証・ユーザー・アプリ・通知）ごとにファイル分割。 |
| `core/` | コア機能（設定・セキュリティ・依存関係・ミドルウェア）。 |
| `dal/` | データアクセス層。JSON DB実装とRDB実装を抽象化。 |
| `models/` | データモデル（Pydantic）。リクエスト/レスポンスの型定義。 |
| `utils/` | ユーティリティ（manifest.json読み込み等）。 |

### 3.2 FastAPIエントリーポイント（main.py）

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.app.sys.api import auth, users, apps, notifications
from backend.app.sys.core.config import settings

app = FastAPI(title="Webシステム", version="1.0.0")

# CORS設定（開発環境のみ）
if settings.ENV == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# APIルーター登録
app.include_router(auth.router, prefix="/api/sys/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/sys/users", tags=["users"])
app.include_router(apps.router, prefix="/api/sys/apps", tags=["apps"])
app.include_router(notifications.router, prefix="/api/sys/notifications", tags=["notifications"])

# 静的ファイル配信
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")
app.mount("/apps", StaticFiles(directory="apps"), name="apps")

# SPAルーティング対応
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse("frontend/dist/index.html")
```

### 3.3 DAL抽象化（dal/base.py）

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class DataAccessLayer(ABC):
    @abstractmethod
    async def get(self, collection: str, id: str) -> Optional[Dict[str, Any]]:
        """単一レコード取得"""
        pass
    
    @abstractmethod
    async def list(self, collection: str, filter: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """レコード一覧取得"""
        pass
    
    @abstractmethod
    async def create(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """レコード作成"""
        pass
    
    @abstractmethod
    async def update(self, collection: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """レコード更新"""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, id: str) -> bool:
        """レコード削除"""
        pass
```

---

## 4. アプリケーション（apps/）

### 4.1 アプリディレクトリ構成

```
apps/
└── todo-app/                          ← TODOアプリ
    ├── manifest.json                  ← アプリメタ情報
    │
    ├── frontend/                      ← フロントエンド（完全独立）
    │   ├── src/
    │   │   ├── main.ts                ← エントリーポイント
    │   │   ├── components/            ← Alpine.jsコンポーネント
    │   │   │   ├── todo-list.ts       ← TODOリスト
    │   │   │   └── todo-form.ts       ← TODO追加/編集フォーム
    │   │   ├── api/                   ← API呼び出し
    │   │   │   └── todo.ts            ← TODO API
    │   │   └── styles/
    │   │       └── app.css
    │   ├── public/
    │   │   └── index.html
    │   ├── dist/                      ← ビルド出力
    │   ├── package.json
    │   ├── tsconfig.json
    │   └── vite.config.ts
    │
    ├── backend/                       ← バックエンド（完全独立）
    │   ├── app/
    │   │   ├── main.py                ← FastAPIエントリーポイント
    │   │   ├── api/                   ← API
    │   │   │   └── todos.py           ← TODO CRUD API
    │   │   ├── models/                ← データモデル
    │   │   │   └── todo.py            ← TODOモデル
    │   │   └── utils/
    │   │       └── dal.py             ← DAL（システム共通基盤を利用）
    │   ├── data/                      ← アプリ固有データ
    │   │   └── todos.json             ← TODOデータ
    │   └── requirements.txt
    │
    └── tests/                         ← テスト（完全独立）
        ├── frontend/
        │   └── unit/
        │       └── todo-list.test.ts
        └── backend/
            ├── unit/
            │   └── test_todos.py
            └── integration/
                └── test_todos_api.py
```

### 4.2 アプリ開発規約

| 項目 | 規約 |
|------|------|
| **ディレクトリ名** | 英小文字・数字・ハイフン（例：`todo-app`） |
| **manifest.json** | 必須。スキーマに準拠すること。 |
| **フロントエンド** | TypeScript + Alpine.js + Bootstrap 5。Viteでビルド。 |
| **バックエンド** | Python FastAPI。APIプレフィックスは `/api/<app-name>` |
| **データ** | `backend/data/` に配置。DAL経由でアクセス。 |
| **テスト** | `tests/` に配置。フロントエンド（Vitest）、バックエンド（pytest）。 |
| **独立性** | 他のアプリのデータに直接アクセスしない。 |

---

## 5. テスト（tests/）

### 5.1 システム共通基盤テスト構成

```
tests/
├── frontend/
│   ├── unit/                          ← 単体テスト（Vitest）
│   │   ├── components/
│   │   │   ├── header.test.ts
│   │   │   ├── navigation.test.ts
│   │   │   └── notification.test.ts
│   │   └── api/
│   │       ├── auth.test.ts
│   │       └── users.test.ts
│   └── e2e/                           ← E2Eテスト（Playwright）
│       ├── login.spec.ts
│       ├── users.spec.ts
│       └── apps.spec.ts
│
└── backend/
    ├── unit/                          ← 単体テスト（pytest）
    │   ├── test_auth.py
    │   ├── test_users.py
    │   ├── test_apps.py
    │   └── test_dal.py
    └── integration/                   ← 結合テスト（pytest）
        ├── test_auth_api.py
        ├── test_users_api.py
        └── test_apps_api.py
```

### 5.2 テスト実行コマンド

| テスト種別 | コマンド |
|-----------|---------|
| フロントエンド単体テスト | `npm run test:unit` （Vitest） |
| フロントエンドE2Eテスト | `npm run test:e2e` （Playwright） |
| バックエンド単体テスト | `pytest tests/backend/unit/` |
| バックエンド結合テスト | `pytest tests/backend/integration/` |
| 全テスト実行 | `npm run test:all && pytest` |

---

## 6. 設計書・ドキュメント（documents/）

### 6.1 システム共通基盤（documents/sys/）

```
documents/sys/
├── 01-requirements/                   ← 工程1: 要件定義
│   ├── requirements.md                ← 機能要件・非機能要件
│   ├── use-cases.md                   ← ユースケース記述
│   └── acceptance-criteria.md         ← 受け入れ基準
│
├── 02-basic-design/                   ← 工程2: 基本設計
│   ├── architecture.md                ← システムアーキテクチャ設計
│   ├── api-design.md                  ← API設計
│   ├── screen-design.md               ← 画面設計・ワイヤーフレーム
│   ├── manifest-schema.md             ← manifest.jsonスキーマ
│   └── directory-structure.md         ← ディレクトリ構成
│
├── 03-detail-design/                  ← 工程3: 詳細設計
│   ├── class-design.md                ← クラス設計
│   ├── database-design.md             ← データベース設計（JSON構造）
│   ├── interface-design.md            ← インターフェース設計
│   └── sequence-diagrams.md           ← シーケンス図
│
├── 05-unit-test-report.md             ← 工程5: 単体評価レポート
├── 06-integration-test-report.md      ← 工程6: 結合評価レポート
├── 07-system-test-report.md           ← 工程7: システム評価レポート
│
└── 08-release/                        ← 工程8: リリース
    ├── release-notes.md               ← リリースノート
    └── deployment-guide.md            ← デプロイメントガイド
```

### 6.2 アプリケーション（documents/app/）

アプリケーションも同様の構成を持つ（`documents/app/01-requirements/` 〜 `08-release/`）。

---

## 7. データ配置（backend/data/）

### 7.1 システム共通データ

```
backend/data/
├── users.json                         ← ユーザー情報
├── sessions/                          ← セッション情報（ファイル分割）
│   ├── session_001.json
│   └── session_002.json
├── apps.json                          ← アプリ設定
└── config.json                        ← システム設定
```

### 7.2 ユーザー情報（users.json）

```json
{
  "users": [
    {
      "id": "user_001",
      "username": "admin",
      "passwordHash": "$2b$12$...",
      "displayName": "管理者",
      "role": "admin",
      "email": "admin@example.com",
      "createdAt": "2026-05-01T10:00:00Z",
      "lastLogin": "2026-05-28T09:00:00Z",
      "metadata": {}
    }
  ]
}
```

### 7.3 アプリ設定（apps.json）

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

### 7.4 アプリ固有データ（apps/todo-app/backend/data/）

```
apps/todo-app/backend/data/
└── todos.json                         ← TODOデータ
```

---

## 8. 環境変数（.env）

### 8.1 .env.example

```bash
# 環境（development, production）
ENV=development

# JWT設定
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400

# データベース（将来対応）
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# CORS設定（開発環境）
CORS_ORIGINS=http://localhost:5173

# ログレベル
LOG_LEVEL=INFO
```

---

## 9. 依存関係管理

### 9.1 フロントエンド（package.json）

```json
{
  "name": "websys-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test:unit": "vitest",
    "test:e2e": "playwright test"
  },
  "dependencies": {
    "alpinejs": "^3.13.0",
    "bootstrap": "^5.3.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "vitest": "^1.0.0",
    "@playwright/test": "^1.40.0"
  }
}
```

### 9.2 バックエンド（requirements.txt）

```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
aiofiles==23.2.1
sse-starlette==2.0.0
pytest==8.0.0
pytest-asyncio==0.23.0
httpx==0.26.0
```

---

## 関連ドキュメント

- [システムアーキテクチャ設計書](./architecture.md)
- [API設計書](./api-design.md)
- [画面設計書](./screen-design.md)
- [manifest.jsonスキーマ](./manifest-schema.md)
- [工程1: 要件定義](../01-requirements/)
