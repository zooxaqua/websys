"""
設定管理API

このモジュールはシステム設定の取得・更新を担当するAPIエンドポイントを提供します。
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.sys.core.dependencies import get_current_admin_user
from app.sys.models.user import User
import json
from pathlib import Path
from typing import Any

router = APIRouter(tags=["config"])

# 設定ファイルパス
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "data" / "config.json"


class ConfigResponse(BaseModel):
    """設定レスポンス"""
    config: dict[str, Any]


class ConfigUpdateRequest(BaseModel):
    """設定更新リクエスト"""
    config: dict[str, Any]


def load_config() -> dict[str, Any]:
    """
    設定ファイルを読み込み
    
    Returns:
        設定辞書
    """
    if not CONFIG_FILE.exists():
        # デフォルト設定
        default_config = {
            "siteName": "WebSystem",
            "siteDescription": "統合Webシステム",
            "theme": "light",
            "language": "ja",
            "sessionTimeout": 24,
            "maxLoginAttempts": 5,
            "passwordMinLength": 8,
            "enableNotifications": True,
            "enableAppStore": True,
            "maintenanceMode": False
        }
        save_config(default_config)
        return default_config
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict[str, Any]) -> None:
    """
    設定ファイルに保存
    
    Args:
        config: 設定辞書
    """
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


@router.get("", response_model=ConfigResponse)
async def get_config(
    current_user: User = Depends(get_current_admin_user)
) -> ConfigResponse:
    """
    システム設定を取得（管理者のみ）
    
    Args:
        current_user: 現在のユーザー（管理者）
        
    Returns:
        設定情報
    """
    config = load_config()
    return ConfigResponse(config=config)


@router.put("", response_model=ConfigResponse)
async def update_config(
    request: ConfigUpdateRequest,
    current_user: User = Depends(get_current_admin_user)
) -> ConfigResponse:
    """
    システム設定を更新（管理者のみ）
    
    Args:
        request: 設定更新リクエスト
        current_user: 現在のユーザー（管理者）
        
    Returns:
        更新後の設定情報
    """
    # 既存設定を読み込み
    current_config = load_config()
    
    # 更新（マージ）
    current_config.update(request.config)
    
    # 保存
    save_config(current_config)
    
    return ConfigResponse(config=current_config)


@router.get("/public", response_model=ConfigResponse)
async def get_public_config() -> ConfigResponse:
    """
    公開設定を取得（認証不要）
    
    パスワードポリシーなど、ログイン前に必要な情報を返します。
    
    Returns:
        公開設定情報
    """
    config = load_config()
    
    # 公開する設定のみ抽出
    public_config = {
        "siteName": config.get("siteName", "WebSystem"),
        "siteDescription": config.get("siteDescription", ""),
        "theme": config.get("theme", "light"),
        "language": config.get("language", "ja"),
        "passwordMinLength": config.get("passwordMinLength", 8),
        "maintenanceMode": config.get("maintenanceMode", False)
    }
    
    return ConfigResponse(config=public_config)
