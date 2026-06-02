"""
ヘルスチェックAPI

このモジュールはシステムの稼働状況を確認するAPIエンドポイントを提供します。
"""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timezone
from pathlib import Path
import sys

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """ヘルスチェックレスポンス"""
    status: str
    timestamp: str
    version: str
    python_version: str
    data_dir_accessible: bool


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    ヘルスチェック
    
    システムの稼働状況を返します。
    - status: "ok" または "error"
    - timestamp: 現在時刻（ISO8601形式）
    - version: システムバージョン
    - python_version: Pythonバージョン
    - data_dir_accessible: データディレクトリへのアクセス可否
    
    Returns:
        ヘルスチェック情報
    """
    # データディレクトリの存在確認
    data_dir = Path(__file__).parent.parent.parent.parent / "data"
    data_dir_accessible = data_dir.exists() and data_dir.is_dir()
    
    return HealthResponse(
        status="ok" if data_dir_accessible else "error",
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        version="1.0.0",
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        data_dir_accessible=data_dir_accessible
    )


@router.get("/ping")
async def ping() -> dict[str, str]:
    """
    軽量なヘルスチェック（Pingエンドポイント）
    
    ロードバランサーやモニタリングツールからの定期チェックに使用します。
    
    Returns:
        pongレスポンス
    """
    return {"message": "pong"}
