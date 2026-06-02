"""
単体テスト: Auth API

テスト対象: project/backend/app/sys/api/auth.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.api.auth import router, LoginRequest, ChangePasswordRequest
from app.sys.models.user import User
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/sys")


class TestAuthAPI:
    """Auth API のテストクラス"""
    
    @pytest.fixture
    def client(self):
        """TestClient インスタンス"""
        return TestClient(app)
    
    @pytest.fixture
    def valid_user(self):
        """有効なユーザー"""
        return User(
            id="user-001",
            username="testuser",
            passwordHash="hashed_password",
            displayName="Test User",
            role="user",
            email="test@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
    
    # TC-AUTH-API-001: 正常系 - ログイン成功
    @patch('app.sys.api.auth.get_auth_service')
    def test_login_success(self, mock_get_service, client, valid_user):
        """ログイン成功"""
        mock_service = Mock()
        mock_service.authenticate.return_value = (valid_user, "valid_token")
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/auth/login", json={
            "username": "testuser",
            "password": "SecurePass123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["username"] == "testuser"
        # Cookie が設定されることを確認
        assert "auth_token" in response.cookies
    
    # TC-AUTH-API-002: 異常系 - ログイン失敗（認証エラー）
    @patch('app.sys.api.auth.get_auth_service')
    def test_login_failure(self, mock_get_service, client):
        """ログイン失敗（認証エラー）"""
        mock_service = Mock()
        mock_service.authenticate.side_effect = HTTPException(
            status_code=401,
            detail={"code": "ERR-SYS-AUTH-001", "message": "認証失敗"}
        )
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/auth/login", json={
            "username": "testuser",
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
    
    # TC-AUTH-API-003: 異常系 - バリデーションエラー（パスワード未入力）
    def test_login_validation_error(self, client):
        """バリデーションエラー（パスワード未入力）"""
        response = client.post("/api/sys/auth/login", json={
            "username": "testuser"
        })
        
        assert response.status_code == 422  # Validation Error
    
    # TC-AUTH-API-004: 正常系 - ログアウト成功
    @patch('app.sys.api.auth.get_current_user')
    @patch('app.sys.api.auth.get_auth_service')
    def test_logout_success(self, mock_get_service, mock_get_user, client, valid_user):
        """ログアウト成功"""
        mock_get_user.return_value = valid_user
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/auth/logout")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    # TC-AUTH-API-005: 正常系 - 現在のユーザー情報取得
    @patch('app.sys.api.auth.get_current_user')
    def test_get_me_success(self, mock_get_user, client, valid_user):
        """現在のユーザー情報取得成功"""
        mock_get_user.return_value = valid_user
        
        response = client.get("/api/sys/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "passwordHash" not in data  # パスワードハッシュは含まれない
    
    # TC-AUTH-API-006: 異常系 - 未認証でアクセス
    @patch('app.sys.api.auth.get_current_user')
    def test_get_me_unauthorized(self, mock_get_user, client):
        """未認証でアクセス"""
        mock_get_user.side_effect = HTTPException(status_code=401, detail="Unauthorized")
        
        response = client.get("/api/sys/auth/me")
        
        assert response.status_code == 401
    
    # TC-AUTH-API-007: 正常系 - パスワード変更成功
    @patch('app.sys.api.auth.get_current_user')
    @patch('app.sys.api.auth.get_auth_service')
    def test_change_password_success(self, mock_get_service, mock_get_user, client, valid_user):
        """パスワード変更成功"""
        mock_get_user.return_value = valid_user
        mock_service = Mock()
        mock_service.change_password.return_value = True
        mock_get_service.return_value = mock_service
        
        response = client.put("/api/sys/auth/password", json={
            "currentPassword": "OldPass123!",
            "newPassword": "NewPass456!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    # TC-AUTH-API-008: 異常系 - パスワード変更失敗（現在のパスワード不一致）
    @patch('app.sys.api.auth.get_current_user')
    @patch('app.sys.api.auth.get_auth_service')
    def test_change_password_wrong_current(self, mock_get_service, mock_get_user, client, valid_user):
        """パスワード変更失敗（現在のパスワード不一致）"""
        mock_get_user.return_value = valid_user
        mock_service = Mock()
        mock_service.change_password.side_effect = HTTPException(
            status_code=400,
            detail={"code": "ERR-SYS-AUTH-007", "message": "現在のパスワードが正しくありません"}
        )
        mock_get_service.return_value = mock_service
        
        response = client.put("/api/sys/auth/password", json={
            "currentPassword": "WrongPassword",
            "newPassword": "NewPass456!"
        })
        
        assert response.status_code == 400
    
    # TC-AUTH-API-009: 境界値 - ログインリクエストの最小データ
    @patch('app.sys.api.auth.get_auth_service')
    def test_login_minimal_data(self, mock_get_service, client, valid_user):
        """ログインリクエストの最小データ"""
        mock_service = Mock()
        mock_service.authenticate.return_value = (valid_user, "valid_token")
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/auth/login", json={
            "username": "a",
            "password": "p"
        })
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
