"""アプリ管理API"""
from fastapi import APIRouter, Depends
from typing import Optional
from pydantic import BaseModel
from ..models.app import AppResponse
from ..models.user import User
from ..services.app_service import AppService
from ..core.dependencies import get_app_service, get_current_user, get_current_admin_user

router = APIRouter(tags=["apps"])


class AppUpdateRequest(BaseModel):
    """アプリ更新リクエスト"""
    enabled: Optional[bool] = None
    isEnabled: Optional[bool] = None  # テストで使用される可能性があるため両方対応


@router.get("", response_model=list[AppResponse])
def list_apps(
    enabled: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリ一覧を取得"""
    apps = app_service.list_apps(enabled=enabled)
    return [AppResponse(**app.model_dump()) for app in apps]


@router.get("/{app_id}", response_model=AppResponse)
def get_app(
    app_id: str,
    current_user: User = Depends(get_current_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリ詳細を取得"""
    app = app_service.get_app(app_id)
    return AppResponse(**app.model_dump())


@router.patch("/{app_id}", response_model=AppResponse)
def update_app(
    app_id: str,
    update_request: AppUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリを更新（有効化・無効化）（管理者のみ）"""
    # enabled または isEnabled のいずれかを受け取る
    enabled = update_request.enabled if update_request.enabled is not None else update_request.isEnabled
    
    if enabled is None:
        return AppResponse(**app_service.get_app(app_id).model_dump())
    
    if enabled:
        app_service.enable_app(app_id)
    else:
        app_service.disable_app(app_id)
    
    app = app_service.get_app(app_id)
    return AppResponse(**app.model_dump())


@router.post("/scan")
def scan_apps(
    current_user: User = Depends(get_current_admin_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリをスキャンして登録（管理者のみ）"""
    apps = app_service.scan_apps()
    return {
        "success": True,
        "message": f"{len(apps)} 個のアプリをスキャンしました",
        "apps": [AppResponse(**app.model_dump()) for app in apps]
    }


@router.put("/{app_id}/enable")
def enable_app(
    app_id: str,
    current_user: User = Depends(get_current_admin_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリを有効化（管理者のみ）"""
    app_service.enable_app(app_id)
    return {"success": True, "message": "アプリを有効化しました"}


@router.put("/{app_id}/disable")
def disable_app(
    app_id: str,
    current_user: User = Depends(get_current_admin_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリを無効化（管理者のみ）"""
    app_service.disable_app(app_id)
    return {"success": True, "message": "アプリを無効化しました"}


@router.post("/{app_id}/reload", response_model=AppResponse)
def reload_app(
    app_id: str,
    current_user: User = Depends(get_current_admin_user),
    app_service: AppService = Depends(get_app_service)
):
    """アプリをリロード（管理者のみ）"""
    app = app_service.reload_app(app_id)
    return AppResponse(**app.model_dump())
