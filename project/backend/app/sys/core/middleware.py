"""ミドルウェア"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from ..services.app_service import AppService
from ..dal.app_dal import AppDAL
from ..core.config import settings


class DisabledAppMiddleware(BaseHTTPMiddleware):
    """無効化されたアプリへのアクセスをブロック"""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # アプリAPIへのアクセスをチェック
        if path.startswith("/api/") and not path.startswith("/api/sys/"):
            # アプリIDを抽出（例: /api/todo-app/... → todo-app）
            parts = path.split("/")
            if len(parts) >= 3:
                app_id = parts[2]
                
                # アプリ状態をチェック
                app_dal = AppDAL(data_dir=settings.DATA_DIR)
                app_data = app_dal.find_one({"id": app_id})
                
                if app_data and not app_data.get("enabled", True):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={"code": "ERR-SYS-APPS-007", "message": "このアプリは無効化されています"}
                    )
        
        response = await call_next(request)
        return response
