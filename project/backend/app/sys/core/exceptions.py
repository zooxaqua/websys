"""
カスタム例外クラス

このモジュールはシステム共通基盤で使用するカスタム例外クラスを定義します。
エラーコード体系に基づき、統一的なエラーハンドリングを実現します。
"""

from typing import Any


class BaseAPIException(Exception):
    """
    API例外の基底クラス
    
    すべてのカスタム例外はこのクラスを継承します。
    """
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: dict[str, Any] | None = None
    ):
        """
        BaseAPIExceptionの初期化
        
        Args:
            code: エラーコード（ERR-SYS-XXX-XXX形式）
            message: エラーメッセージ
            status_code: HTTPステータスコード
            details: エラー詳細情報
        """
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict[str, Any]:
        """
        例外を辞書形式に変換
        
        Returns:
            エラー情報を含む辞書
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details
            }
        }


class WebSystemException(BaseAPIException):
    """
    Webシステム全体で使用する汎用例外クラス
    
    BaseAPIExceptionを継承し、デフォルトで500エラーを返します。
    カスタムエラーメッセージとエラーコードをサポートします。
    """
    def __init__(
        self, 
        status_code: int = 500,
        message: str = "Internal Server Error",
        error_code: str = "WS_ERROR"
    ):
        """
        WebSystemExceptionの初期化
        
        Args:
            status_code: HTTPステータスコード（デフォルト: 500）
            message: エラーメッセージ（デフォルト: "Internal Server Error"）
            error_code: エラーコード（デフォルト: "WS_ERROR"）
        """
        super().__init__(
            code=error_code,
            message=message,
            status_code=status_code
        )


# 認証エラー（ERR-SYS-AUTH-XXX）
class AuthenticationException(BaseAPIException):
    """認証エラー"""
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(code, message, status_code=401, details=details)


class AuthorizationException(BaseAPIException):
    """認可エラー（権限不足）"""
    def __init__(self, code: str = "ERR-SYS-AUTH-006", message: str = "管理者権限が必要です", details: dict[str, Any] | None = None):
        super().__init__(code, message, status_code=403, details=details)


# ユーザー管理エラー（ERR-SYS-USER-XXX）
class UserNotFoundException(BaseAPIException):
    """ユーザーが見つからないエラー"""
    def __init__(self, user_id: str | None = None):
        details = {"userId": user_id} if user_id else {}
        super().__init__(
            code="ERR-SYS-USER-001",
            message="ユーザーが見つかりません",
            status_code=404,
            details=details
        )


class UserAlreadyExistsException(BaseAPIException):
    """ユーザーが既に存在するエラー"""
    def __init__(self, field: str, value: str):
        super().__init__(
            code="ERR-SYS-USER-002" if field == "username" else "ERR-SYS-USER-003",
            message=f"{'ユーザー名' if field == 'username' else 'メールアドレス'}が既に存在します",
            status_code=409,
            details={"field": field, "value": value}
        )


class ValidationException(BaseAPIException):
    """バリデーションエラー"""
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(code, message, status_code=400, details=details)


# アプリ管理エラー（ERR-SYS-APPS-XXX）
class AppNotFoundException(BaseAPIException):
    """アプリが見つからないエラー"""
    def __init__(self, app_id: str | None = None):
        details = {"appId": app_id} if app_id else {}
        super().__init__(
            code="ERR-SYS-APPS-001",
            message="アプリが見つかりません",
            status_code=404,
            details=details
        )


class AppManifestException(BaseAPIException):
    """アプリマニフェストエラー"""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            code="ERR-SYS-APPS-002",
            message=message,
            status_code=400,
            details=details
        )


# 通知エラー（ERR-SYS-NOTF-XXX）
class NotificationNotFoundException(BaseAPIException):
    """通知が見つからないエラー"""
    def __init__(self, notification_id: str | None = None):
        details = {"notificationId": notification_id} if notification_id else {}
        super().__init__(
            code="ERR-SYS-NOTF-001",
            message="通知が見つかりません",
            status_code=404,
            details=details
        )


class NotificationAccessDeniedException(BaseAPIException):
    """通知アクセス権限エラー"""
    def __init__(self):
        super().__init__(
            code="ERR-SYS-NOTF-002",
            message="この通知にアクセスする権限がありません",
            status_code=403
        )


# サーバーエラー（ERR-SYS-SRVR-XXX）
class InternalServerException(BaseAPIException):
    """内部サーバーエラー"""
    def __init__(self, message: str = "予期しないエラーが発生しました", details: dict[str, Any] | None = None):
        super().__init__(
            code="ERR-SYS-SRVR-001",
            message=message,
            status_code=500,
            details=details
        )
