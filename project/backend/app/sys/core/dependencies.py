"""FastAPI 依存関係"""
from typing import Optional
from fastapi import Cookie, HTTPException, status, Depends
from ..models.user import User
from ..dal import UserDAL, SessionDAL, AppDAL, NotificationDAL
from ..services import AuthService, UserService, AppService, NotificationService
from ..core.config import settings


# DAL インスタンス
def get_user_dal() -> UserDAL:
    """UserDAL を取得"""
    return UserDAL(data_dir=settings.DATA_DIR)


def get_session_dal() -> SessionDAL:
    """SessionDAL を取得"""
    return SessionDAL(data_dir=settings.DATA_DIR)


def get_app_dal() -> AppDAL:
    """AppDAL を取得"""
    return AppDAL(data_dir=settings.DATA_DIR)


def get_notification_dal() -> NotificationDAL:
    """NotificationDAL を取得"""
    return NotificationDAL(data_dir=settings.DATA_DIR)


# サービス インスタンス
def get_auth_service(
    user_dal: UserDAL = Depends(get_user_dal),
    session_dal: SessionDAL = Depends(get_session_dal)
) -> AuthService:
    """AuthService を取得"""
    return AuthService(user_dal=user_dal, session_dal=session_dal)


def get_user_service(user_dal: UserDAL = Depends(get_user_dal)) -> UserService:
    """UserService を取得"""
    return UserService(dal=user_dal)


def get_app_service(app_dal: AppDAL = Depends(get_app_dal)) -> AppService:
    """AppService を取得"""
    return AppService(dal=app_dal)


def get_notification_service(
    notification_dal: NotificationDAL = Depends(get_notification_dal)
) -> NotificationService:
    """NotificationService を取得"""
    return NotificationService(dal=notification_dal)


# 認証依存関係
def get_current_user(
    auth_token: Optional[str] = Cookie(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """現在のユーザーを取得（認証必須）"""
    if not auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "ERR-SYS-AUTH-004", "message": "認証トークンが見つかりません"}
        )
    
    return auth_service.get_current_user(auth_token)


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """管理者権限チェック"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ERR-SYS-AUTH-006", "message": "管理者権限が必要です"}
        )
    
    return current_user
