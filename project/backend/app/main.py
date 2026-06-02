"""
FastAPIメインアプリケーション

システム共通基盤とアプリケーションを統合するメインエントリーポイントです。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.sys.api.middleware import error_handler_middleware
from app.sys.api import auth, users, apps, notifications, config, health
from pathlib import Path
import json

# FastAPIアプリケーション作成
app = FastAPI(
    title="WebSystem API",
    description="統合Webシステム - システム共通基盤API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Vite開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# エラーハンドリングミドルウェア
app.middleware("http")(error_handler_middleware)

# システム共通基盤APIルーター登録
app.include_router(auth.router, prefix="/api/sys")
app.include_router(users.router, prefix="/api/sys")
app.include_router(apps.router, prefix="/api/sys")
app.include_router(notifications.router, prefix="/api/sys")
app.include_router(config.router, prefix="/api/sys")
app.include_router(health.router, prefix="/api/sys")


# アプリケーションAPIを動的にマウント
def mount_app_apis():
    """
    apps.jsonに登録されているアプリのAPIを動的にマウント
    """
    apps_file = Path(__file__).parent / "data" / "apps.json"
    if not apps_file.exists():
        return
    
    with open(apps_file, "r", encoding="utf-8") as f:
        apps_data = json.load(f)
    
    for app_id, app_data in apps_data.items():
        if not app_data.get("enabled", False):
            continue
        
        # アプリのAPIプレフィックス
        api_prefix = app_data.get("apiPrefix", f"/api/apps/{app_id}")
        
        # アプリのmain.pyを動的にインポート
        try:
            app_name = app_data.get("name", app_id)
            # アプリのバックエンドmain.pyからルーターをインポート
            # 例: from apps.todo_app.backend.app.main import router
            app_module_path = f"apps.{app_id.replace('-', '_')}.backend.app.main"
            app_module = __import__(app_module_path, fromlist=["router"])
            app_router = app_module.router
            
            # ルーター登録
            app.include_router(app_router, prefix=api_prefix, tags=[app_name])
            print(f"✓ Mounted app API: {app_name} at {api_prefix}")
        except Exception as e:
            print(f"✗ Failed to mount app API: {app_id} - {e}")


# アプリケーションAPIをマウント
mount_app_apis()


# 静的ファイル配信（本番環境用）
# 開発環境ではViteが担当するため、本番ビルド後に有効化
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


@app.get("/")
async def root():
    """
    ルートエンドポイント
    
    システム情報を返します。
    """
    return {
        "name": "WebSystem",
        "version": "1.0.0",
        "description": "統合Webシステム - システム共通基盤",
        "api_docs": "/docs",
        "health_check": "/api/sys/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
