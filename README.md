# Webシステム開発プロジェクト

## プロジェクト構成

このプロジェクトは、システム共通基盤とアプリケーションから構成されています。

### システム共通基盤
- **フロントエンド**: TypeScript + Alpine.js + Bootstrap 5
- **バックエンド**: Python FastAPI
- **認証**: JWT (httpOnly Cookie)
- **データベース**: JSON (将来的にRDB対応)

### TODOアプリ
- タスク管理アプリケーション
- システム共通基盤の認証を利用

## セットアップ

### バックエンド

```bash
cd project/backend
pip install -r requirements.txt

# 開発サーバー起動
python -m app.sys.main
```

### フロントエンド

```bash
cd project/frontend
npm install

# 開発サーバー起動
npm run dev
```

### TODOアプリ

```bash
# バックエンド
cd project/apps/todo-app/backend
pip install -r requirements.txt

# フロントエンド
cd project/apps/todo-app/frontend
npm install
npm run dev
```

## 初期ユーザー

開発環境では初回起動時に管理者ユーザーが自動作成されます：

- **ユーザー名**: admin
- **パスワード**: admin123

## API ドキュメント

バックエンド起動後、以下のURLでAPIドキュメントを参照できます：

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)
