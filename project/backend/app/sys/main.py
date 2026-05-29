"""FastAPI メインアプリケーション"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from .api import auth, users, apps, notifications
from .core.config import settings
from .core.middleware import DisabledAppMiddleware

app = FastAPI(
    title="Webシステム共通基盤",
    version="1.0.0",
    description="システム共通基盤API"
)

# CORS設定（開発環境のみ）
if settings.ENV == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 無効化アプリミドルウェア
app.add_middleware(DisabledAppMiddleware)

# システム共通基盤API
app.include_router(auth.router, prefix="/api/sys/auth", tags=["認証"])
app.include_router(users.router, prefix="/api/sys/users", tags=["ユーザー管理"])
app.include_router(apps.router, prefix="/api/sys/apps", tags=["アプリ管理"])
app.include_router(notifications.router, prefix="/api/sys/notifications", tags=["通知"])

# 静的ファイル配信（フロントエンド）
frontend_dist = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

# ルートエンドポイント
@app.get("/api/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "ok", "message": "Webシステム共通基盤は正常に動作しています"}


# 起動時処理
@app.on_event("startup")
async def startup_event():
    """起動時にアプリをスキャン"""
    from .services.app_service import AppService
    from .dal.app_dal import AppDAL
    
    app_dal = AppDAL(data_dir=settings.DATA_DIR)
    app_service = AppService(dal=app_dal)
    
    # アプリスキャン
    apps = app_service.scan_apps(apps_dir="./apps")
    print(f"[起動] {len(apps)} 個のアプリをスキャンしました")
    
    # 初期ユーザー作成（開発環境のみ）
    if settings.ENV == "development":
        from .dal.user_dal import UserDAL
        from .services.user_service import UserService
        from .models.user import UserCreate
        from datetime import datetime
        
        user_dal = UserDAL(data_dir=settings.DATA_DIR)
        
        # 管理者ユーザーが存在しない場合は作成
        admin_user = user_dal.find_by_username("admin")
        if not admin_user:
            user_service = UserService(dal=user_dal)
            user_service.create_user(UserCreate(
                username="admin",
                password="admin123",
                displayName="管理者",
                role="admin",
                email="admin@example.com",
                metadata={}
            ))
            print("[起動] 初期管理者ユーザー（admin / admin123）を作成しました")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
