"""グローバルミドルウェア"""
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    グローバルエラーハンドリングミドルウェア
    
    全てのエンドポイントで発生した未処理例外をキャッチし、
    統一されたJSONエラーレスポンスを返す。
    
    Args:
        request: リクエストオブジェクト
        call_next: 次のミドルウェア/エンドポイント
        
    Returns:
        Response: 正常時はエンドポイントのレスポンス、
                 エラー時は500 JSONエラーレスポンス
    """
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        # エラーログ出力
        logger.error(
            f"Unhandled error in {request.method} {request.url.path}: {str(e)}",
            exc_info=True
        )
        
        # JSONエラーレスポンス
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": str(e)
            }
        )
