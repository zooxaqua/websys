# Webシステム開発プロジェクト — 管理者向けセットアップガイド

| 項目 | 内容 |
|------|------|
| 対象者 | システム管理者 |
| 作成日 | 2026年5月29日 |
| バージョン | 1.0 |

---

## 📋 目次

1. [システム概要](#1-システム概要)
2. [前提条件](#2-前提条件)
3. [初回セットアップ](#3-初回セットアップ)
4. [システムの起動](#4-システムの起動)
5. [テストの実行](#5-テストの実行)
6. [トラブルシューティング](#6-トラブルシューティング)
7. [ディレクトリ構造](#7-ディレクトリ構造)

---

## 1. システム概要

### 1.1 システム構成

```
┌─────────────────────────────────────────────────────────────┐
│                        ブラウザ                              │
│  TypeScript SPA (Vite + Alpine.js + Bootstrap)             │
└───────────┬─────────────────────────────────────────────────┘
            │ REST API + SSE
            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI (Python 3.9+)                          │
│  - システム共通API（認証・ユーザー管理・アプリ管理）        │
│  - アプリケーションAPI（manifest.jsonベース）               │
└───────────┬─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                   データ層（JSONファイル）                   │
│  - ユーザー情報、セッション、アプリ設定                     │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 技術スタック

| カテゴリ | 技術 |
|---------|------|
| **フロントエンド** | TypeScript, Alpine.js, Bootstrap 5, Vite |
| **バックエンド** | Python 3.9+, FastAPI |
| **データベース** | JSON ファイル（将来: RDB対応） |
| **認証** | JWT (httpOnly Cookie) |
| **通信** | REST API, Server-Sent Events (SSE) |
| **テスト** | pytest, vitest |

---

## 2. 前提条件

### 2.1 必要なソフトウェア

| ソフトウェア | バージョン | 確認コマンド |
|------------|-----------|-------------|
| **Python** | 3.9 以上 | `python3 --version` |
| **Node.js** | 18.x 以上 | `node --version` |
| **npm** | 9.x 以上 | `npm --version` |
| **Git** | 2.x 以上 | `git --version` |

### 2.2 インストール方法（macOS）

```bash
# Homebrew（パッケージマネージャー）のインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python のインストール
brew install python@3.9

# Node.js のインストール
brew install node
```

---

## 3. 初回セットアップ

### 3.1 リポジトリのクローン

```bash
# リポジトリをクローン
git clone <repository-url> websys
cd websys
```

---

### 3.2 システム共通基盤（Backend）のセットアップ

#### 1. Python仮想環境の作成

```bash
# project/backend ディレクトリに移動
cd project/backend

# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate     # Windows

# pip を最新版にアップグレード
pip install --upgrade pip
```

#### 2. Python依存関係のインストール

```bash
# requirements.txt から依存関係をインストール
pip install -r requirements.txt
```

**インストールされるパッケージ**:
- `fastapi` — Webフレームワーク
- `uvicorn` — ASGIサーバー
- `pydantic` — データバリデーション
- `python-jose[cryptography]` — JWT処理
- `passlib[bcrypt]` — パスワードハッシュ化
- `pytest` — テストフレームワーク
- `pytest-cov` — カバレッジ計測
- `httpx` — HTTPクライアント

#### 3. データディレクトリの確認

```bash
# データディレクトリの確認
ls -la data/

# 初期データファイルが存在することを確認
# - users.json
# - sessions/
# - apps.json
# - config.json
```

---

### 3.3 システム共通基盤（Frontend）のセットアップ

#### 1. Node.js依存関係のインストール

```bash
# project/frontend ディレクトリに移動
cd ../frontend

# 依存関係をインストール
npm install
```

**インストールされるパッケージ**:
- `vite` — ビルドツール
- `typescript` — TypeScript
- `alpinejs` — リアクティブフレームワーク
- `bootstrap` — CSSフレームワーク
- `vitest` — テストフレームワーク

#### 2. フロントエンドのビルド

```bash
# 開発モード（ホットリロード）
npm run dev

# または、本番ビルド
npm run build
```

---

### 3.4 アプリケーション（例: todo-app）のセットアップ

#### 1. Backend

```bash
# アプリのbackendディレクトリに移動
cd ../../apps/todo-app/backend

# 仮想環境を作成
python3 -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate

# 依存関係をインストール
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. Frontend

```bash
# アプリのfrontendディレクトリに移動
cd ../frontend

# 依存関係をインストール
npm install

# ビルド
npm run build
```

---

## 4. システムの起動

### 4.1 バックエンドの起動

#### システム共通基盤

```bash
# project/backend ディレクトリに移動
cd project/backend

# 仮想環境をアクティベート
source venv/bin/activate

# FastAPI サーバーを起動
uvicorn app.sys.main:app --reload --host 0.0.0.0 --port 8000
```

**起動確認**:
- ブラウザで `http://localhost:8000/docs` を開く（Swagger UI）
- ブラウザで `http://localhost:8000/api/sys/health` を開く（ヘルスチェック）

---

### 4.2 フロントエンドの起動（開発モード）

```bash
# project/frontend ディレクトリに移動
cd project/frontend

# 開発サーバーを起動
npm run dev
```

**起動確認**:
- ブラウザで `http://localhost:5173` を開く
- ログイン画面が表示される

---

### 4.3 本番環境での起動

#### 1. フロントエンドのビルド

```bash
# project/frontend
cd project/frontend
npm run build

# ビルド結果が dist/ に出力される
ls -la dist/
```

#### 2. バックエンドで静的ファイルを配信

```bash
# project/backend
cd project/backend
source venv/bin/activate
uvicorn app.sys.main:app --host 0.0.0.0 --port 8000
```

→ `http://localhost:8000/` でフロントエンドが配信される

---

## 5. テストの実行

> **🚨 重要**: すべてのPythonテストは**必ず**仮想環境のPythonを使用してください。グローバルPythonでの実行は禁止されています。

### 5.1 単体テスト（Backend）

#### システム共通基盤

```bash
# リポジトリルートに移動
cd /path/to/websys

# 仮想環境のPythonで実行（必須）
PYTHONPATH=project/backend project/backend/venv/bin/python -m pytest \
  tests/unit/logic/backend/sys/ \
  --cov=project/backend/app/sys \
  --cov-branch \
  --cov-report=html:tests/unit/outputs/coverage-sys-html \
  --cov-report=json:tests/unit/outputs/coverage-sys.json \
  --junit-xml=tests/unit/outputs/test-report-sys.xml \
  -v
```

**または、仮想環境をアクティベートしてから実行**:
```bash
source project/backend/venv/bin/activate
pytest tests/unit/logic/backend/sys/ --cov=project/backend/app/sys -v
```

#### テスト結果の確認

```bash
# カバレッジレポート（HTML）をブラウザで開く
open tests/unit/outputs/coverage-sys-html/index.html

# テスト結果サマリー
cat tests/unit/outputs/test-result-user-model.md
```

---

### 5.2 単体テスト（Frontend）

```bash
# project/frontend ディレクトリに移動
cd project/frontend

# テスト実行
npm test

# カバレッジ付きでテスト実行
npm test -- --coverage
```

---

### 5.3 結合テスト

```bash
# リポジトリルートから実行
PYTHONPATH=project/backend project/backend/venv/bin/python -m pytest \
  tests/integration/ \
  --junit-xml=tests/integration/outputs/test-report-integration.xml \
  -v
```

---

### 5.4 システムテスト

```bash
# リポジトリルートから実行
PYTHONPATH=project/backend project/backend/venv/bin/python -m pytest \
  tests/system/ \
  --junit-xml=tests/system/outputs/test-report-system.xml \
  -v
```

---

## 6. トラブルシューティング

### 6.1 Python仮想環境関連

#### 問題: `python3: command not found`

**解決方法**:
```bash
# macOS の場合
brew install python@3.9

# パスを確認
which python3
```

---

#### 問題: `pip install -r requirements.txt` が失敗

**解決方法**:
```bash
# pip を最新版にアップグレード
pip install --upgrade pip

# 個別にインストール
pip install fastapi
pip install uvicorn
pip install pydantic
```

---

### 6.2 Node.js関連

#### 問題: `npm install` が失敗

**解決方法**:
```bash
# npm のキャッシュをクリア
npm cache clean --force

# node_modules を削除して再インストール
rm -rf node_modules package-lock.json
npm install
```

---

### 6.3 テスト実行関連

#### 問題: `ModuleNotFoundError: No module named 'project'`

**解決方法**:
```bash
# PYTHONPATH を正しく設定
export PYTHONPATH=/path/to/websys/project/backend

# または、コマンド実行時に指定
PYTHONPATH=project/backend pytest tests/unit/...
```

---

#### 問題: テストが失敗する

**解決方法**:
1. **テスト結果レポートを確認**:
   ```bash
   cat tests/unit/outputs/test-result-user-model.md
   ```

2. **カバレッジレポートを確認**:
   ```bash
   open tests/unit/outputs/coverage-sys-html/index.html
   ```

3. **詳細なエラーメッセージを確認**:
   ```bash
   pytest tests/unit/logic/backend/sys/ -vv
   ```

---

### 6.4 サーバー起動関連

#### 問題: `Address already in use`

**解決方法**:
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>

# または、別のポートで起動
uvicorn app.sys.main:app --port 8001
```

---

## 7. ディレクトリ構造

```
websys/
├── README.md                          ← プロジェクト概要
├── HOW2USE_ADMIN.md                   ← このファイル（管理者向けガイド）
├── agents.md                          ← エージェント構成定義
│
├── .github/                           ← GitHub設定・CI/CD・チェックプログラム
│   ├── agents/                        ← エージェント定義
│   ├── skills/                        ← スキル定義
│   ├── prompts/                       ← プロンプトテンプレート
│   └── checks/                        ← 工程チェックプログラム
│
├── requests/                          ← ユーザー要求仕様・議事録
│   └── minutes.md
│
├── documents/                         ← 設計書・テストレポート
│   ├── progress.json                  ← 工程進捗管理
│   ├── common/                        ← 共通ドキュメント
│   │   └── 05-unit-test/              ← 単体テスト方針書（共通）
│   ├── sys/                           ← システム共通基盤の設計書
│   │   ├── 01-requirements/           ← 工程1: 要件定義
│   │   ├── 02-basic-design/           ← 工程2: 基本設計
│   │   ├── 03-detail-design/          ← 工程3: 詳細設計
│   │   └── 05-unit-test/              ← 工程5: 単体テスト対象ファイル
│   └── app/                           ← アプリケーションの設計書
│       ├── 01-requirements/
│       ├── 02-basic-design/
│       ├── 03-detail-design/
│       └── 05-unit-test/
│
├── project/                           ← プロジェクトコード
│   ├── backend/                       ← システム共通基盤バックエンド
│   │   ├── venv/                      ← Python仮想環境（git除外）
│   │   ├── app/
│   │   │   └── sys/                   ← システム共通基盤
│   │   │       ├── main.py            ← FastAPIエントリーポイント
│   │   │       ├── api/               ← APIエンドポイント
│   │   │       ├── core/              ← コア機能（認証・セキュリティ）
│   │   │       ├── dal/               ← データアクセス層
│   │   │       ├── models/            ← データモデル
│   │   │       └── services/          ← ビジネスロジック
│   │   ├── data/                      ← JSONデータベース
│   │   │   ├── users.json
│   │   │   ├── sessions/
│   │   │   ├── apps.json
│   │   │   └── config.json
│   │   ├── requirements.txt           ← Python依存関係
│   │   └── .gitignore
│   │
│   ├── frontend/                      ← システム共通基盤フロントエンド
│   │   ├── src/
│   │   │   └── sys/                   ← システム共通UI
│   │   │       ├── main.ts
│   │   │       ├── components/        ← Alpine.jsコンポーネント
│   │   │       ├── pages/             ← ページ
│   │   │       ├── api/               ← API呼び出し
│   │   │       └── utils/             ← ユーティリティ
│   │   ├── public/
│   │   ├── dist/                      ← ビルド出力（git除外）
│   │   ├── package.json               ← npm依存関係
│   │   ├── tsconfig.json
│   │   ├── vite.config.ts
│   │   └── .gitignore
│   │
│   └── apps/                          ← アプリケーション
│       └── todo-app/                  ← TODOアプリ（サンプル）
│           ├── manifest.json          ← アプリメタ情報
│           ├── backend/
│           │   ├── venv/              ← Python仮想環境（git除外）
│           │   ├── app/
│           │   ├── data/
│           │   ├── requirements.txt
│           │   └── .gitignore
│           └── frontend/
│               ├── src/
│               ├── dist/
│               ├── package.json
│               └── .gitignore
│
├── tests/                             ← テストコード
│   ├── unit/                          ← 単体テスト
│   │   ├── inputs/                    ← テストデータ
│   │   │   ├── fixtures/              ← フィクスチャ（JSON）
│   │   │   ├── stubs/                 ← スタブ・モック
│   │   │   └── expected/              ← 期待値
│   │   ├── logic/                     ← テストコード
│   │   │   └── backend/
│   │   │       └── sys/
│   │   │           ├── test_runner.py ← テストランナー（スタブ）
│   │   │           ├── conftest.py
│   │   │           └── test_cases/    ← テストケース
│   │   └── outputs/                   ← テスト結果
│   │       ├── test-report-sys.xml    ← JUnit形式
│   │       ├── coverage-sys.json      ← カバレッジデータ
│   │       └── coverage-sys-html/     ← カバレッジレポート
│   ├── integration/                   ← 結合テスト
│   └── system/                        ← システムテスト
│
└── issues/                            ← 課題管理
    └── issues.json
```

---

## 8. よく使うコマンド一覧

### 8.1 開発時

```bash
# バックエンド起動（開発モード）
cd project/backend
source venv/bin/activate
uvicorn app.sys.main:app --reload --host 0.0.0.0 --port 8000

# フロントエンド起動（開発モード）
cd project/frontend
npm run dev
```

### 8.2 テスト実行

```bash
# 単体テスト（Backend）
PYTHONPATH=project/backend project/backend/venv/bin/python -m pytest tests/unit/logic/backend/sys/ --cov=project/backend/app/sys -v

# 単体テスト（Frontend）
cd project/frontend
npm test
```

### 8.3 ビルド

```bash
# フロントエンドビルド
cd project/frontend
npm run build

# ビルド結果の確認
ls -la dist/
```

### 8.4 仮想環境の再作成

```bash
# 既存の仮想環境を削除
cd project/backend
rm -rf venv

# 再作成
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 9. 参考ドキュメント

| ドキュメント | 説明 |
|------------|------|
| [README.md](README.md) | プロジェクト概要 |
| [agents.md](agents.md) | エージェント構成・連携フロー |
| [documents/sys/02-basic-design/architecture.md](documents/sys/02-basic-design/architecture.md) | システムアーキテクチャ |
| [documents/sys/02-basic-design/directory-structure.md](documents/sys/02-basic-design/directory-structure.md) | ディレクトリ構造詳細 |
| [documents/common/05-unit-test/test-strategy.md](documents/common/05-unit-test/test-strategy.md) | テスト戦略書 |

---

## 10. サポート

### 問い合わせ先
- **プロジェクトリーダー**: [連絡先]
- **技術サポート**: [連絡先]

### エスカレーション
重大な問題が発生した場合は、以下の手順でエスカレーションしてください：
1. `issues/issues.json` に問題を記録
2. プロジェクトリーダーに報告
3. 必要に応じて process-manager（開発統括エージェント）に相談

---

**最終更新**: 2026年5月29日  
**バージョン**: 1.0
