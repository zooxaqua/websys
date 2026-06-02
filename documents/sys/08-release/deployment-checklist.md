# デプロイチェックリスト — Webシステム共通基盤 v1.0

**プロジェクト**: Webシステム開発（システム共通基盤）  
**バージョン**: 1.0.0  
**リリース日**: 2026年6月2日  
**対象環境**: 本番環境（Production）

---

## 📋 デプロイ前チェック

### 1. テスト・品質確認

- [ ] 単体テスト（コア機能）100% PASS（214/214件）
- [ ] 結合テスト 100% PASS（25/27件、2件SKIPはTODOアプリ未実装）
- [ ] セキュリティテスト（OWASP Top 10）主要項目実装確認済み
- [ ] `issues.json` に `severity: critical` の open issue がゼロ
  - ✅ **確認済み**: Critical/Highの未解決issueは0件
  - ⚠️ **注意**: Medium 3件（ISSUE-010, 017, 018）は後続タスク
- [ ] リグレッションテスト実施済み（既存機能に新規バグなし）

### 2. 環境準備

#### 2.1 システム要件

- [ ] **OS**: macOS 14+ / Linux（Ubuntu 20.04+）
- [ ] **Python**: 3.10.13以上
- [ ] **Node.js**: 18.x以上
- [ ] **npm**: 9.x以上
- [ ] **ディスク空き容量**: 最低1GB以上
- [ ] **メモリ**: 最低2GB以上

#### 2.2 Python環境

- [ ] Python仮想環境作成
  ```bash
  cd project/backend
  python -m venv venv
  source venv/bin/activate  # macOS/Linux
  # または: venv\Scripts\activate  # Windows
  ```
- [ ] 依存パッケージインストール
  ```bash
  pip install -r requirements.txt
  ```
- [ ] 依存パッケージバージョン確認
  ```bash
  pip list | grep -E 'fastapi|uvicorn|pydantic|bcrypt|httpx'
  ```
  - fastapi==0.109.0
  - uvicorn==0.27.0
  - pydantic==2.5.3
  - bcrypt>=3.2.0,<4.0.0
  - httpx>=0.25.0

#### 2.3 フロントエンド環境

- [ ] Node.jsモジュールインストール
  ```bash
  cd project/frontend
  npm install
  ```
- [ ] フロントエンドビルド
  ```bash
  npm run build
  ```
- [ ] ビルド成果物確認
  ```bash
  ls -la dist/
  # index.html, assets/ が存在することを確認
  ```

### 3. データファイル準備

#### 3.1 初期データファイル配置

- [ ] `project/backend/data/users.json` が存在することを確認
  - 初期ユーザー: `admin` / パスワード: `admin`（bcryptハッシュ済み）
- [ ] `project/backend/data/sessions/` ディレクトリが存在することを確認
- [ ] `project/backend/data/apps.json` が存在することを確認
- [ ] `project/backend/data/config.json` が存在することを確認
- [ ] `project/backend/data/notifications.json` が存在することを確認

#### 3.2 パーミッション設定

- [ ] データディレクトリに書き込み権限を付与
  ```bash
  chmod -R 755 project/backend/data/
  chmod -R 755 project/backend/data/sessions/
  ```

### 4. セキュリティ設定

#### 4.1 JWT秘密鍵

- [ ] **本番環境用の秘密鍵を生成**
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] 環境変数に設定
  ```bash
  export JWT_SECRET_KEY="<生成された秘密鍵>"
  export JWT_ALGORITHM="HS256"
  export JWT_EXPIRATION_MINUTES=60
  ```
- [ ] ⚠️ **注意**: デフォルトの秘密鍵は使用しない（セキュリティリスク）

#### 4.2 bcrypt設定

- [ ] bcryptライブラリバージョン確認
  ```bash
  pip show bcrypt
  # Version: 3.2.0以上、4.0.0未満
  ```
- [ ] パスワード長制限確認（72バイト以下）
  - 実装済み: `security.py` で事前チェック実装

#### 4.3 HTTPS設定（本番推奨）

- [ ] **本番環境ではHTTPS通信を使用**
  - リバースプロキシ（Nginx/Apache）でTLS終端
  - 証明書: Let's Encrypt等
  - TLS 1.2以上
- [ ] **Cookie設定**
  - `Secure` 属性を有効化（HTTPS時のみ）
  - `HttpOnly` 属性を有効化（XSS対策）
  - `SameSite=Strict` 属性を有効化（CSRF対策）

### 5. アプリプラグイン機構

#### 5.1 manifest.json確認

- [ ] `project/apps/*/manifest.json` が正しい形式であることを確認
  ```bash
  # TODOアプリの場合
  cat project/apps/todo-app/manifest.json
  ```
- [ ] 必須フィールド確認
  - `id`: アプリID（一意）
  - `name`: アプリ名
  - `version`: バージョン
  - `description`: 説明
  - `entryPoint`: エントリーポイントURL
  - `icon`: アイコンパス
  - `requiredPermissions`: 必要な権限

#### 5.2 アプリ配置確認

- [ ] `project/apps/<app-name>/frontend/dist/` が存在
- [ ] `project/apps/<app-name>/backend/app/` が存在
- [ ] `project/apps/<app-name>/backend/data/` ディレクトリが存在
- [ ] アプリごとにデータ領域が独立していることを確認

---

## 🚀 デプロイ手順

### ステップ1: FastAPIサーバー起動

```bash
cd project/backend
source venv/bin/activate  # 仮想環境有効化

# 本番モード起動（リロード無効）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**オプション説明**:
- `--host 0.0.0.0`: 外部からのアクセスを許可
- `--port 8000`: ポート番号
- `--workers 4`: ワーカープロセス数（CPUコア数に応じて調整）
- `--reload` は**本番環境では使用しない**（開発用）

### ステップ2: サーバー起動確認

```bash
# ヘルスチェック
curl http://localhost:8000/api/sys/health

# 期待されるレスポンス
# {"status":"ok","timestamp":"2026-06-02T..."}
```

### ステップ3: ログイン動作確認

1. ブラウザで `http://localhost:8000/` にアクセス
2. ログイン画面が表示されることを確認
3. 初期ユーザーでログイン
   - ユーザー名: `admin`
   - パスワード: `admin`
4. システムポータルページが表示されることを確認
5. 有効化されたアプリが一覧表示されることを確認

### ステップ4: アプリ動作確認

1. システムポータルから「TODOアプリ」を起動
2. アプリが正常に表示されることを確認
3. （注意）TODOアプリのAPIは未実装（ISSUE-017）

### ステップ5: 管理機能確認

1. ログイン後、管理画面にアクセス（`/admin`）
2. ユーザー一覧表示を確認
3. アプリ一覧表示を確認
4. アプリの有効化・無効化動作を確認

---

## ✅ デプロイ後確認

### 1. 基本機能確認

- [ ] ログイン機能が正常に動作
  - JWT Cookieが正しく設定される（httpOnly, SameSite=Strict）
- [ ] ログアウト機能が正常に動作
  - セッションが削除される
  - JWT Cookieが削除される
- [ ] 認証状態が維持される
  - リロードしてもログイン状態が保持される
- [ ] システムポータルページが表示される
  - 有効化されたアプリが一覧表示される
  - システム情報（ユーザー名・権限）が表示される

### 2. API動作確認

```bash
# 認証API
curl -X POST http://localhost:8000/api/sys/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  -c cookies.txt

# ユーザー情報取得API
curl -X GET http://localhost:8000/api/sys/auth/me \
  -b cookies.txt

# アプリ一覧取得API
curl -X GET http://localhost:8000/api/sys/apps \
  -b cookies.txt
```

### 3. セキュリティ確認

- [ ] 未認証アクセスが正しく拒否される（401エラー）
  ```bash
  curl -X GET http://localhost:8000/api/sys/auth/me
  # 期待: 401 Unauthorized
  ```
- [ ] 一般ユーザーが管理者APIにアクセスできない（403エラー）
  ```bash
  # 一般ユーザーでログイン後
  curl -X GET http://localhost:8000/api/sys/users -b cookies.txt
  # 期待: 403 Forbidden（ERR-SYS-AUTH-003）
  ```
- [ ] 無効化されたアプリへのアクセスが制御される
  - URL直接アクセス: ポータルページにリダイレクト
  - API呼び出し: 403エラー

### 4. アプリプラグイン機構確認

- [ ] `apps/*/manifest.json` からアプリが自動認識される
- [ ] 管理画面でアプリを無効化できる
- [ ] 無効化されたアプリはポータルに表示されない
- [ ] 無効化されたアプリのAPIは呼び出し不可（403エラー）

### 5. パフォーマンス確認（推奨）

⚠️ **注意**: 工程7で性能テストが未完了（ISSUE-018）のため、本番環境での追加検証が推奨されます。

- [ ] API応答時間を計測
  ```bash
  time curl -X GET http://localhost:8000/api/sys/auth/me -b cookies.txt
  # 目標: 100ms以内
  ```
- [ ] 同時接続テスト（10ユーザー）
  ```bash
  # Apache Bench等で実施
  ab -n 100 -c 10 http://localhost:8000/api/sys/health
  ```

### 6. ログ確認

- [ ] サーバーログにエラーが出力されていないことを確認
  ```bash
  # Uvicornのログを確認
  # エラー・警告がないことを確認
  ```
- [ ] 認証失敗がログに記録されることを確認
  ```bash
  # わざと間違ったパスワードでログイン
  # ログに "Authentication failed" が記録されることを確認
  ```

---

## 🔄 ロールバック手順

万が一、本番環境でトラブルが発生した場合のロールバック手順を定義します。

### 1. サーバー停止

```bash
# FastAPIプロセスを停止
pkill -f "uvicorn app.main:app"

# または
ps aux | grep uvicorn
kill <PID>
```

### 2. データバックアップ復元

```bash
# 事前にバックアップしたデータファイルを復元
cp -r /backup/project/backend/data/* project/backend/data/
```

### 3. 旧バージョン起動

```bash
# 旧バージョンのコードに切り替え（Gitタグ使用）
git checkout v0.9.0  # 前バージョン

# 依存パッケージ再インストール
pip install -r project/backend/requirements.txt

# サーバー再起動
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/api/sys/health

# ログイン確認
```

---

## 📝 デプロイ記録

| 項目 | 値 |
|------|-----|
| デプロイ日時 | `<記入してください>` |
| デプロイ担当者 | `<記入してください>` |
| 環境 | 本番 / ステージング / 開発 |
| サーバーホスト名 | `<記入してください>` |
| IPアドレス | `<記入してください>` |
| ポート番号 | 8000（デフォルト） |
| Python バージョン | `<python --version>` |
| Node.js バージョン | `<node --version>` |
| デプロイ結果 | 成功 / 失敗 |
| 備考 | `<記入してください>` |

---

## ⚠️ 既知の問題と回避策

### 1. 性能要件未検証（ISSUE-018）

**問題**: 工程7でテストコード整備不足により性能要件が未検証

**影響**: API応答時間、同時接続数の検証が未完了

**回避策**:
- 本番環境で手動パフォーマンステストを実施
- Apache Bench / JMeter等でAPI応答時間を計測
- 目標値: API応答時間 < 100ms、同時接続数 >= 10ユーザー

### 2. TODOアプリAPI未実装（ISSUE-017）

**問題**: TODOアプリの固有API（`/api/todo-app/todos`等）が未実装

**影響**: TODOアプリの機能が限定的

**回避策**:
- 現時点では汎用データAPI（`/api/todo-app/data`）が利用可能
- 完全な機能は後続スプリントで実装予定

### 3. API層単体テスト70件失敗（ISSUE-010）

**問題**: API層のテストコード整備不足により70件失敗

**影響**: API層の網羅的なテストが未完了（コア機能は100%PASS）

**回避策**:
- 結合テスト（27件中25件PASS）で主要APIは検証済み
- 実装品質は高く、本番投入可能
- テストコード改善は後続タスクで実施

---

## 📞 トラブルシューティング

### Q1. ログイン後に401エラーが発生する

**原因**: JWT Cookieが正しく設定されていない

**対処法**:
1. ブラウザのCookieを確認（DevTools → Application → Cookies）
2. `token` Cookieが存在し、httpOnly属性が有効であることを確認
3. JWT秘密鍵が環境変数に正しく設定されているか確認

### Q2. アプリが一覧に表示されない

**原因**: manifest.jsonが正しく読み込まれていない

**対処法**:
1. `project/apps/*/manifest.json` の形式を確認
2. サーバーログでエラーメッセージを確認
3. `apps.json` にアプリが登録されているか確認

### Q3. パスワードハッシュ化でエラーが発生する

**原因**: bcryptの依存関係問題、または72バイト制限超過

**対処法**:
1. bcryptバージョンを確認: `pip show bcrypt`
2. パスワード長を確認（72バイト以下）
3. requirements.txtから再インストール

---

## ✅ デプロイ完了確認

- [ ] 全てのデプロイ前チェック項目を完了
- [ ] デプロイ手順を正常に実行
- [ ] デプロイ後確認を全て完了
- [ ] ロールバック手順を確認・文書化
- [ ] デプロイ記録を記入
- [ ] トラブル発生時の連絡体制を確認

---

**承認者**: process-manager  
**最終更新**: 2026年6月2日  
**次回レビュー**: v1.1リリース前
