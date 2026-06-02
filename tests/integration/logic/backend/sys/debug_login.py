"""デバッグ: ログイン失敗原因の調査"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "project" / "backend"))

from fastapi.testclient import TestClient
from app.sys.main import app
import json
import os
import tempfile
import shutil

# テンポラリディレクトリ作成
tmpdir = tempfile.mkdtemp()

# フィクスチャをコピー
test_data_dir = Path(__file__).parent.parent.parent.parent / "inputs" / "fixtures"
shutil.copy(test_data_dir / "test_users.json", Path(tmpdir) / "users.json")
shutil.copy(test_data_dir / "test_apps.json", Path(tmpdir) / "apps.json")
Path(tmpdir, "sessions").mkdir()
Path(tmpdir, "notifications.json").write_text("[]")
Path(tmpdir, "config.json").write_text(json.dumps({
    "systemName": "Test",
    "version": "1.0.0",
    "environment": "test",
    "features": {"enableRegistration": False, "enableNotifications": True}
}))

os.environ["DATA_DIR"] = tmpdir

# テストクライアント作成
client = TestClient(app)

print("=== ユーザーデータ確認 ===")
with open(Path(tmpdir) / "users.json") as f:
    users = json.load(f)
    for user in users:
        print(f"ID: {user['id']}, Username: {user['username']}, Role: {user['role']}")

print("\n=== ログイン試行（test_admin / password） ===")
response = client.post(
    "/api/sys/auth/login",
    json={"username": "test_admin", "password": "password"}
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print(f"Cookies: {response.cookies}")

# クリーンアップ
shutil.rmtree(tmpdir)
