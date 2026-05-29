# manifest.json スキーマ設計書（システム共通基盤）

| 項目 | 内容 |
|------|------|
| 作成日 | 2026年5月28日 |
| バージョン | 1.0 |
| 対象 | システム共通基盤（sys） |
| 工程 | 工程2: 基本設計 |

---

## 1. 概要

各アプリケーションは `apps/<app-name>/manifest.json` にメタ情報を定義します。システム起動時にこのファイルを読み込み、アプリを自動認識・登録します。

---

## 2. manifest.json スキーマ

### 2.1 JSON Schema定義

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "App Manifest Schema",
  "type": "object",
  "required": ["name", "displayName", "version", "description", "entryPoint", "apiPrefix"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "description": "アプリの識別名（英小文字・数字・ハイフン）"
    },
    "displayName": {
      "type": "string",
      "minLength": 1,
      "maxLength": 50,
      "description": "ナビゲーションメニューに表示される名前"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "セマンティックバージョニング形式（例：1.0.0）"
    },
    "description": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "アプリの説明文"
    },
    "entryPoint": {
      "type": "string",
      "pattern": "^/apps/[a-z0-9-]+/$",
      "description": "フロントエンドのエントリーポイント（URLパス）"
    },
    "apiPrefix": {
      "type": "string",
      "pattern": "^/api/[a-z0-9-]+$",
      "description": "バックエンドAPIのプレフィックス"
    },
    "icon": {
      "type": "string",
      "description": "アプリアイコンのパス（アプリディレクトリからの相対パス）"
    },
    "author": {
      "type": "string",
      "description": "アプリ作成者名"
    },
    "requiredPermissions": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["read", "write", "admin", "delete"]
      },
      "description": "必要な権限のリスト"
    },
    "dependencies": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "依存する他のアプリのリスト（アプリ名）"
    },
    "metadata": {
      "type": "object",
      "description": "アプリ固有のメタデータ（自由形式）"
    }
  }
}
```

---

## 3. フィールド詳細

### 3.1 必須フィールド

| フィールド | 型 | 説明 | 例 |
|-----------|-----|------|-----|
| `name` | string | アプリの識別名。ディレクトリ名と一致させる。英小文字・数字・ハイフンのみ使用可能。 | `"todo-app"` |
| `displayName` | string | ナビゲーションメニュー・ポータルページに表示される名前。日本語可能。最大50文字。 | `"TODO管理"` |
| `version` | string | セマンティックバージョニング形式（`major.minor.patch`）。 | `"1.0.0"` |
| `description` | string | アプリの説明文。ポータルページのアプリカードに表示される。最大200文字。 | `"タスク管理アプリケーション"` |
| `entryPoint` | string | フロントエンドのエントリーポイント（URLパス）。`/apps/<app-name>/` 形式。 | `"/apps/todo-app/"` |
| `apiPrefix` | string | バックエンドAPIのプレフィックス。`/api/<app-name>` 形式。 | `"/api/todo-app"` |

### 3.2 オプションフィールド

| フィールド | 型 | 説明 | 例 |
|-----------|-----|------|-----|
| `icon` | string | アプリアイコンのパス。アプリディレクトリからの相対パス。未指定時はデフォルトアイコン。 | `"icon.png"` |
| `author` | string | アプリ作成者名。 | `"System Team"` |
| `requiredPermissions` | array | 必要な権限のリスト。システム側で権限チェックに使用。 | `["read", "write"]` |
| `dependencies` | array | 依存する他のアプリのリスト。依存アプリが無効化されている場合、警告を表示。 | `["base-app"]` |
| `metadata` | object | アプリ固有のメタデータ。自由形式。システム側では使用しない。 | `{"category": "productivity"}` |

---

## 4. manifest.json 例

### 4.1 TODOアプリの例

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
    "tags": ["task", "todo", "management"]
  }
}
```

### 4.2 カレンダーアプリの例

```json
{
  "name": "calendar-app",
  "displayName": "カレンダー",
  "version": "1.0.0",
  "description": "スケジュール管理とイベント登録を行うアプリケーション",
  "entryPoint": "/apps/calendar-app/",
  "apiPrefix": "/api/calendar-app",
  "icon": "icon.png",
  "author": "System Team",
  "requiredPermissions": ["read", "write"],
  "dependencies": [],
  "metadata": {
    "category": "productivity",
    "tags": ["calendar", "schedule", "event"]
  }
}
```

### 4.3 管理者専用アプリの例

```json
{
  "name": "admin-dashboard",
  "displayName": "管理ダッシュボード",
  "version": "1.0.0",
  "description": "システム全体の統計情報・ログ閲覧を行う管理者専用アプリ",
  "entryPoint": "/apps/admin-dashboard/",
  "apiPrefix": "/api/admin-dashboard",
  "icon": "icon.png",
  "author": "System Team",
  "requiredPermissions": ["admin"],
  "dependencies": [],
  "metadata": {
    "category": "admin",
    "restrictedToRole": "admin"
  }
}
```

---

## 5. バリデーション仕様

### 5.1 必須項目チェック

システム起動時に以下をチェックします：

| 項目 | チェック内容 | エラー時の動作 |
|------|------------|--------------|
| 必須フィールド存在 | `name`, `displayName`, `version`, `description`, `entryPoint`, `apiPrefix` が存在するか | アプリを「エラー」状態で登録、警告ログ出力 |
| `name` 形式 | 英小文字・数字・ハイフンのみ | アプリを「エラー」状態で登録 |
| `version` 形式 | セマンティックバージョニング形式（`\d+\.\d+\.\d+`） | アプリを「エラー」状態で登録 |
| `entryPoint` 形式 | `/apps/<name>/` 形式 | アプリを「エラー」状態で登録 |
| `apiPrefix` 形式 | `/api/<name>` 形式 | アプリを「エラー」状態で登録 |
| ディレクトリ名一致 | manifest.jsonの `name` とディレクトリ名が一致するか | 警告ログ出力（アプリは登録） |

### 5.2 重複チェック

| 項目 | チェック内容 | エラー時の動作 |
|------|------------|--------------|
| `name` 重複 | 同じ `name` のアプリが既に登録されているか | 後から読み込まれたアプリを無視、警告ログ出力 |
| `entryPoint` 重複 | 同じ `entryPoint` のアプリが既に登録されているか | 後から読み込まれたアプリを無視、警告ログ出力 |
| `apiPrefix` 重複 | 同じ `apiPrefix` のアプリが既に登録されているか | 後から読み込まれたアプリを無視、警告ログ出力 |

---

## 6. システム側の処理

### 6.1 manifest.json読み込みフロー

```python
import json
from pathlib import Path

def load_manifests(apps_dir: Path = Path("apps")) -> list[dict]:
    """
    apps/ディレクトリをスキャンし、manifest.jsonを読み込む
    """
    manifests = []
    
    for app_path in apps_dir.iterdir():
        if not app_path.is_dir():
            continue
        
        manifest_path = app_path / "manifest.json"
        
        if not manifest_path.exists():
            print(f"Warning: {app_path.name} にmanifest.jsonが見つかりません")
            continue
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # バリデーション
            if validate_manifest(manifest):
                manifests.append(manifest)
            else:
                print(f"Error: {app_path.name}/manifest.json のバリデーションに失敗しました")
        
        except json.JSONDecodeError as e:
            print(f"Error: {app_path.name}/manifest.json の解析に失敗しました: {e}")
        
        except Exception as e:
            print(f"Error: {app_path.name}/manifest.json の読み込みに失敗しました: {e}")
    
    return manifests

def validate_manifest(manifest: dict) -> bool:
    """
    manifest.jsonのバリデーション
    """
    required_fields = ["name", "displayName", "version", "description", "entryPoint", "apiPrefix"]
    
    # 必須フィールドチェック
    for field in required_fields:
        if field not in manifest:
            print(f"Error: 必須フィールド '{field}' がありません")
            return False
    
    # name形式チェック
    import re
    if not re.match(r'^[a-z0-9-]+$', manifest['name']):
        print(f"Error: 'name' は英小文字・数字・ハイフンのみ使用できます: {manifest['name']}")
        return False
    
    # version形式チェック
    if not re.match(r'^\d+\.\d+\.\d+$', manifest['version']):
        print(f"Error: 'version' はセマンティックバージョニング形式である必要があります: {manifest['version']}")
        return False
    
    # entryPoint形式チェック
    expected_entry = f"/apps/{manifest['name']}/"
    if manifest['entryPoint'] != expected_entry:
        print(f"Warning: 'entryPoint' は '{expected_entry}' が推奨されます: {manifest['entryPoint']}")
    
    # apiPrefix形式チェック
    expected_api = f"/api/{manifest['name']}"
    if not manifest['apiPrefix'].startswith(expected_api):
        print(f"Warning: 'apiPrefix' は '{expected_api}' で始まることが推奨されます: {manifest['apiPrefix']}")
    
    return True
```

### 6.2 アプリ登録処理

```python
async def register_apps():
    """
    manifest.jsonを読み込み、backend/data/apps.jsonに登録
    """
    manifests = load_manifests()
    
    # 既存のアプリ設定を読み込み
    dal = get_dal()
    existing_apps = await dal.list("apps") or []
    
    registered_apps = []
    
    for manifest in manifests:
        app_id = manifest['name']
        
        # 既存アプリの有効化状態を維持
        existing_app = next((app for app in existing_apps if app['id'] == app_id), None)
        enabled = existing_app['enabled'] if existing_app else False
        
        app = {
            "id": app_id,
            "name": manifest['displayName'],
            "version": manifest['version'],
            "description": manifest['description'],
            "icon": f"/apps/{app_id}/{manifest.get('icon', 'icon.png')}",
            "entryPoint": manifest['entryPoint'],
            "apiPrefix": manifest['apiPrefix'],
            "enabled": enabled,
            "author": manifest.get('author', ''),
            "requiredPermissions": manifest.get('requiredPermissions', []),
            "dependencies": manifest.get('dependencies', []),
            "manifest": manifest,
            "lastUpdated": datetime.utcnow().isoformat() + "Z"
        }
        
        registered_apps.append(app)
    
    # backend/data/apps.json に保存
    await dal.update("apps", {"apps": registered_apps})
    
    return registered_apps
```

### 6.3 アプリ有効化・無効化

```python
async def enable_app(app_id: str):
    """
    アプリを有効化
    """
    dal = get_dal()
    apps_data = await dal.get("apps")
    
    for app in apps_data['apps']:
        if app['id'] == app_id:
            app['enabled'] = True
            app['lastUpdated'] = datetime.utcnow().isoformat() + "Z"
            break
    
    await dal.update("apps", apps_data)

async def disable_app(app_id: str):
    """
    アプリを無効化
    """
    dal = get_dal()
    apps_data = await dal.get("apps")
    
    for app in apps_data['apps']:
        if app['id'] == app_id:
            app['enabled'] = False
            app['lastUpdated'] = datetime.utcnow().isoformat() + "Z"
            break
    
    await dal.update("apps", apps_data)
```

---

## 7. アプリ開発者向けガイド

### 7.1 manifest.json作成手順

1. **アプリディレクトリ作成**

```bash
mkdir -p apps/my-app
cd apps/my-app
```

2. **manifest.json作成**

```bash
cat > manifest.json << 'EOF'
{
  "name": "my-app",
  "displayName": "マイアプリ",
  "version": "1.0.0",
  "description": "アプリの説明",
  "entryPoint": "/apps/my-app/",
  "apiPrefix": "/api/my-app",
  "icon": "icon.png",
  "author": "Your Name",
  "requiredPermissions": ["read", "write"],
  "dependencies": []
}
EOF
```

3. **バリデーション確認**

```bash
# システム起動時に自動的にバリデーションされる
python backend/app/main.py
```

### 7.2 チェックリスト

- [ ] `name` がディレクトリ名と一致している
- [ ] `name` が英小文字・数字・ハイフンのみ使用している
- [ ] `version` がセマンティックバージョニング形式（`1.0.0`）
- [ ] `entryPoint` が `/apps/<name>/` 形式
- [ ] `apiPrefix` が `/api/<name>` 形式
- [ ] `description` が200文字以内
- [ ] `icon` ファイルが存在する（オプション）
- [ ] 必須フィールドがすべて記載されている

---

## 8. エラーメッセージ一覧

| エラーコード | メッセージ | 原因 |
|------------|-----------|------|
| `MANIFEST_NOT_FOUND` | manifest.jsonが見つかりません | manifest.jsonファイルが存在しない |
| `MANIFEST_PARSE_ERROR` | manifest.jsonの解析に失敗しました | JSON形式が不正 |
| `MANIFEST_VALIDATION_ERROR` | manifest.jsonのバリデーションに失敗しました | 必須フィールド欠如、形式不正 |
| `MANIFEST_NAME_INVALID` | nameは英小文字・数字・ハイフンのみ使用できます | `name` フィールドの形式不正 |
| `MANIFEST_VERSION_INVALID` | versionはセマンティックバージョニング形式である必要があります | `version` フィールドの形式不正 |
| `MANIFEST_DUPLICATE_NAME` | 同じnameのアプリが既に登録されています | `name` の重複 |
| `MANIFEST_DUPLICATE_ENTRY` | 同じentryPointのアプリが既に登録されています | `entryPoint` の重複 |
| `MANIFEST_DUPLICATE_API` | 同じapiPrefixのアプリが既に登録されています | `apiPrefix` の重複 |

---

## 関連ドキュメント

- [システムアーキテクチャ設計書](./architecture.md)
- [API設計書](./api-design.md)
- [画面設計書](./screen-design.md)
- [ディレクトリ構成](./directory-structure.md)
- [工程1: 要件定義](../01-requirements/)
