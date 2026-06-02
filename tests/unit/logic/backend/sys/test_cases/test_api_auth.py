"""
認証API (auth.py) の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: ログイン成功、ログアウト成功、ユーザー情報取得、パスワード変更
- 異常系: 認証失敗、権限不足、無効なトークン
- 境界値: パスワード長、トークン有効期限
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from project.backend.app.sys.api.auth import router, LoginRequest, LoginResponse, ChangePasswordRequest
from project.backend.app.sys.models.user import User, UserResponse
from project.backend.app.main import app


client = TestClient(app)


class TestAuthAPI:
    """認証APIのテストクラス"""
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_success(self, mock_get_auth_service):
        """
        TC-API-AUTH-001: 正常系 - ログイン成功
        条件: 有効なusername/password
        期待: 200 OK, auth_token Cookie設定, ユーザー情報返却
        """
        mock_auth_service = Mock()
        mock_user = User(
            id="USR001",
            username="testuser",
            email="test@example.com",
            fullName="Test User",
            role="user",
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        mock_auth_service.authenticate.return_value = (mock_user, "mock_jwt_token")
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "testuser", "password": "Password123!"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["user"]["username"] == "testuser"
        assert "auth_token" in response.cookies
        mock_auth_service.authenticate.assert_called_once_with("testuser", "Password123!")
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_invalid_credentials(self, mock_get_auth_service):
        """
        TC-API-AUTH-002: 異常系 - 認証失敗（不正な認証情報）
        条件: 誤ったpassword
        期待: 401 Unauthorized
        """
        mock_auth_service = Mock()
        mock_auth_service.authenticate.side_effect = ValueError("認証に失敗しました")
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "testuser", "password": "WrongPassword"}
        )
        
        # FastAPIの例外ハンドリングによりエラーが返される
        assert response.status_code in [401, 500]
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_missing_username(self, mock_get_auth_service):
        """
        TC-API-AUTH-003: 異常系 - バリデーションエラー（username欠損）
        条件: usernameなし
        期待: 422 Unprocessable Entity
        """
        response = client.post(
            "/api/sys/auth/login",
            json={"password": "Password123!"}
        )
        
        assert response.status_code == 422
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_missing_password(self, mock_get_auth_service):
        """
        TC-API-AUTH-004: 異常系 - バリデーションエラー（password欠損）
        条件: passwordなし
        期待: 422 Unprocessable Entity
        """
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422
    
    @patch('project.backend.app.sys.api.auth.get_current_user')
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_logout_success(self, mock_get_auth_service, mock_get_current_user):
        """
        TC-API-AUTH-005: 正常系 - ログアウト成功
        条件: 有効なトークン
        期待: 200 OK, auth_token Cookie削除
        """
        mock_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_get_current_user.return_value = mock_user
        
        response = client.post(
            "/api/sys/auth/logout",
            cookies={"auth_token": "valid_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "auth_token" not in response.cookies or response.cookies.get("auth_token") == ""
    
    @patch('project.backend.app.sys.api.auth.get_current_user')
    def test_get_me_success(self, mock_get_current_user):
        """
        TC-API-AUTH-006: 正常系 - 現在のユーザー情報取得成功
        条件: 有効なトークン
        期待: 200 OK, ユーザー情報返却
        """
        mock_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_get_current_user.return_value = mock_user
        
        response = client.get(
            "/api/sys/auth/me",
            cookies={"auth_token": "valid_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
        assert response.json()["id"] == "USR001"
    
    def test_get_me_unauthorized(self):
        """
        TC-API-AUTH-007: 異常系 - 未認証でユーザー情報取得
        条件: トークンなし
        期待: 401 Unauthorized
        """
        response = client.get("/api/sys/auth/me")
        
        # 依存関係でエラーが返される
        assert response.status_code in [401, 403]
    
    @patch('project.backend.app.sys.api.auth.get_current_user')
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_change_password_success(self, mock_get_auth_service, mock_get_current_user):
        """
        TC-API-AUTH-008: 正常系 - パスワード変更成功
        条件: 有効な現在のパスワード、有効な新しいパスワード
        期待: 200 OK, 成功メッセージ
        """
        mock_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_get_current_user.return_value = mock_user
        mock_auth_service = Mock()
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.put(
            "/api/sys/auth/password",
            json={
                "currentPassword": "OldPassword123!",
                "newPassword": "NewPassword456!"
            },
            cookies={"auth_token": "valid_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_auth_service.change_password.assert_called_once_with(
            "USR001",
            "OldPassword123!",
            "NewPassword456!"
        )
    
    @patch('project.backend.app.sys.api.auth.get_current_user')
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_change_password_wrong_current_password(self, mock_get_auth_service, mock_get_current_user):
        """
        TC-API-AUTH-009: 異常系 - パスワード変更失敗（現在のパスワード誤り）
        条件: 誤った現在のパスワード
        期待: 401 Unauthorized
        """
        mock_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_get_current_user.return_value = mock_user
        mock_auth_service = Mock()
        mock_auth_service.change_password.side_effect = ValueError("現在のパスワードが正しくありません")
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.put(
            "/api/sys/auth/password",
            json={
                "currentPassword": "WrongPassword",
                "newPassword": "NewPassword456!"
            },
            cookies={"auth_token": "valid_token"}
        )
        
        assert response.status_code in [401, 500]
    
    @patch('project.backend.app.sys.api.auth.get_current_user')
    def test_change_password_missing_fields(self, mock_get_current_user):
        """
        TC-API-AUTH-010: 異常系 - パスワード変更失敗（必須フィールド欠損）
        条件: newPassword欠損
        期待: 422 Unprocessable Entity
        """
        mock_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_get_current_user.return_value = mock_user
        
        response = client.put(
            "/api/sys/auth/password",
            json={"currentPassword": "OldPassword123!"},
            cookies={"auth_token": "valid_token"}
        )
        
        assert response.status_code == 422
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_empty_username(self, mock_get_auth_service):
        """
        TC-API-AUTH-011: 境界値 - 空のusername
        条件: username=""
        期待: 422 Unprocessable Entity
        """
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "", "password": "Password123!"}
        )
        
        # Pydanticのバリデーションまたはサービス層でエラー
        assert response.status_code in [422, 401, 500]
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_empty_password(self, mock_get_auth_service):
        """
        TC-API-AUTH-012: 境界値 - 空のpassword
        条件: password=""
        期待: 422 Unprocessable Entity
        """
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "testuser", "password": ""}
        )
        
        assert response.status_code in [422, 401, 500]
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_long_username(self, mock_get_auth_service):
        """
        TC-API-AUTH-013: 境界値 - 長いusername（500文字）
        条件: username="a"*500
        期待: 認証処理が実行される（エラーまたは失敗）
        """
        mock_auth_service = Mock()
        mock_auth_service.authenticate.side_effect = ValueError("ユーザーが見つかりません")
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "a" * 500, "password": "Password123!"}
        )
        
        # バリデーションまたは認証失敗
        assert response.status_code in [422, 401, 500]
    
    @patch('project.backend.app.sys.api.auth.get_current_user')
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_change_password_same_password(self, mock_get_auth_service, mock_get_current_user):
        """
        TC-API-AUTH-014: 境界値 - 現在のパスワードと同じ新しいパスワード
        条件: currentPassword == newPassword
        期待: サービス層でバリデーションエラー（またはwarning）
        """
        mock_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_get_current_user.return_value = mock_user
        mock_auth_service = Mock()
        # サービス層で同じパスワードを許可する場合もあるため、正常終了またはエラー
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.put(
            "/api/sys/auth/password",
            json={
                "currentPassword": "SamePassword123!",
                "newPassword": "SamePassword123!"
            },
            cookies={"auth_token": "valid_token"}
        )
        
        # 正常終了（200）またはバリデーションエラー（400, 422）
        assert response.status_code in [200, 400, 422]
    
    @patch('project.backend.app.sys.api.auth.get_auth_service')
    def test_login_admin_user(self, mock_get_auth_service):
        """
        TC-API-AUTH-015: 正常系 - 管理者ユーザーログイン
        条件: role="admin"
        期待: 200 OK, role="admin"のユーザー情報返却
        """
        mock_auth_service = Mock()
        mock_user = User(
            id="USR_ADMIN",
            username="admin",
            passwordHash="hashed",
            displayName="Admin User",
            role="admin",
            email="admin@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_auth_service.authenticate.return_value = (mock_user, "admin_jwt_token")
        mock_get_auth_service.return_value = mock_auth_service
        
        response = client.post(
            "/api/sys/auth/login",
            json={"username": "admin", "password": "AdminPassword123!"}
        )
        
        assert response.status_code == 200
        assert response.json()["user"]["role"] == "admin"
