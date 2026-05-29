"""認証API"""
from fastapi import APIRouter, Depends, Response, HTTPException, status
from pydantic import BaseModel
from ..models.user import UserResponse
from ..services.auth_service import AuthService
from ..core.dependencies import get_auth_service, get_current_user
from ..models.user import User

router = APIRouter()


class LoginRequest(BaseModel):
    """ログインリクエスト"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """ログインレスポンス"""
    success: bool
    user: UserResponse


class ChangePasswordRequest(BaseModel):
    """パスワード変更リクエスト"""
    currentPassword: str
    newPassword: str


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    """ログイン"""
    user, token = auth_service.authenticate(request.username, request.password)
    
    # httpOnly Cookie にJWTを設定
    response.set_cookie(
        key="auth_token",
        value=token,
        httponly=True,
        samesite="strict",
        max_age=86400  # 24時間
    )
    
    return LoginResponse(
        success=True,
        user=UserResponse(**user.model_dump())
    )


@router.post("/logout")
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """ログアウト"""
    # Cookie からトークンを取得して削除（依存関係で取得済み）
    response.delete_cookie(key="auth_token")
    
    return {"success": True, "message": "ログアウトしました"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """現在のユーザー情報を取得"""
    return UserResponse(**current_user.model_dump())


@router.put("/password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """パスワード変更"""
    auth_service.change_password(
        current_user.id,
        request.currentPassword,
        request.newPassword
    )
    
    return {"success": True, "message": "パスワードを変更しました"}
