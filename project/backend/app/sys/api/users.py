"""ユーザー管理API"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from pydantic import BaseModel
from ..models.user import User, UserCreate, UserUpdate, UserResponse
from ..services.user_service import UserService
from ..core.dependencies import get_user_service, get_current_user, get_current_admin_user

router = APIRouter(tags=["users"])


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""
    users: list[UserResponse]
    total: int
    limit: int
    offset: int


@router.get("", response_model=UserListResponse)
def list_users(
    role: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """ユーザー一覧を取得（管理者のみ）"""
    users, total = user_service.list_users(role=role, limit=limit, offset=offset)
    
    return UserListResponse(
        users=[UserResponse(**user.model_dump()) for user in users],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """ユーザー詳細を取得（管理者のみ）"""
    user = user_service.get_user(user_id)
    return UserResponse(**user.model_dump())


@router.post("", response_model=UserResponse, status_code=201)
def create_user(
    user_create: UserCreate,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """ユーザーを作成（管理者のみ）"""
    user = user_service.create_user(user_create)
    return UserResponse(**user.model_dump())


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """ユーザーを更新（管理者のみ）"""
    user = user_service.update_user(user_id, user_update)
    return UserResponse(**user.model_dump())


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(get_user_service)
):
    """ユーザーを削除（管理者のみ）"""
    user_service.delete_user(user_id, current_user.id)
    return {"success": True, "message": "ユーザーを削除しました"}
