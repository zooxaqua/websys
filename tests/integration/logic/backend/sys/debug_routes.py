"""デバッグ: 利用可能なエンドポイントを確認"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent / "project" / "backend"))

from app.sys.main import app

print("=== FastAPI エンドポイント一覧 ===")
for route in app.routes:
    if hasattr(route, "path") and hasattr(route, "methods"):
        print(f"{list(route.methods)[0] if route.methods else 'GET':<7} {route.path}")
