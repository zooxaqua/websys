"""
単体テスト: AuthService

テスト対象: project/backend/app/sys/services/auth_service.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.services.auth_service import AuthService
from app.sys.models.user import User
from app.sys.models.session import Session
from fastapi import HTTPException


class TestAuthService:
    """AuthService のテストクラス"""
    
    @pytest.fixture
    def user_dal_mock(self):
        """UserDAL のモック"""
        return Mock()
    
    @pytest.fixture
    def session_dal_mock(self):
        """SessionDAL のモック"""
        return Mock()
    
    @pytest.fixture
    def auth_service(self, user_dal_mock, session_dal_mock):
        """AuthService インスタンス"""
        return AuthService(user_dal_mock, session_dal_mock)
    
    @pytest.fixture
    def valid_user_data(self):
        """有効なユーザーデータ"""
        return {
            "id": "user-001",
            "username": "testuser",
            "passwordHash": "$2b$12$SeledKqfxDPWuX2js6mITuq1VnsI3uHBm03GOT5tnKNWAKdHA9J4e",  # "SecurePass123!"
            "displayName": "Test User",
            "role": "user",
            "email": "test@example.com",
            "metadata": {},
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:00:00Z",
            "lastLogin": None
        }
    
    # TC-AUTH-SVC-001: 正常系 - ユーザー認証成功
    @patch('app.sys.services.auth_service.create_access_token')
    def test_authenticate_success(self, mock_token, auth_service, user_dal_mock, session_dal_mock, valid_user_data):
        """認証成功"""
        user_dal_mock.find_by_username.return_value = valid_user_data
        user_dal_mock.update_last_login.return_value = True
        session_dal_mock.insert.return_value = True
        mock_token.return_value = "valid_token"
        
        user, token = auth_service.authenticate("testuser", "SecurePass123!")
        
        assert user.username == "testuser"
        assert token == "valid_token"
        user_dal_mock.update_last_login.assert_called_once()
        session_dal_mock.insert.assert_called_once()
    
    # TC-AUTH-SVC-002: 異常系 - ユーザーが存在しない
    def test_authenticate_user_not_found(self, auth_service, user_dal_mock):
        """ユーザーが存在しない"""
        user_dal_mock.find_by_username.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            auth_service.authenticate("nonexistent", "AnyPass123!")
        
        assert exc.value.status_code == 401
        assert "ERR-SYS-AUTH-001" in str(exc.value.detail)
    
    # TC-AUTH-SVC-003: 異常系 - パスワード不一致
    def test_authenticate_invalid_password(self, auth_service, user_dal_mock, valid_user_data):
        """パスワード不一致"""
        user_dal_mock.find_by_username.return_value = valid_user_data
        
        with pytest.raises(HTTPException) as exc:
            auth_service.authenticate("testuser", "WrongPassword")
        
        assert exc.value.status_code == 401
        assert "ERR-SYS-AUTH-001" in str(exc.value.detail)
    
    # TC-AUTH-SVC-004: 正常系 - セッション作成
    def test_create_session(self, auth_service, session_dal_mock, valid_user_data):
        """セッション作成"""
        session_dal_mock.insert.return_value = True
        user = User.from_dict(valid_user_data)
        
        session = auth_service.create_session(user, "test_token")
        
        assert session.userId == user.id
        assert session.token == "test_token"
        session_dal_mock.insert.assert_called_once()
    
    # TC-AUTH-SVC-005: 正常系 - ログアウト成功
    def test_logout_success(self, auth_service, session_dal_mock):
        """ログアウト成功"""
        session_dal_mock.find_by_token.return_value = {"sessionId": "session-001"}
        session_dal_mock.delete.return_value = True
        
        result = auth_service.logout("valid_token")
        
        assert result is True
        session_dal_mock.delete.assert_called_once_with("session-001")
    
    # TC-AUTH-SVC-006: 異常系 - ログアウト失敗（セッション存在しない）
    def test_logout_no_session(self, auth_service, session_dal_mock):
        """セッション存在しない"""
        session_dal_mock.find_by_token.return_value = None
        
        result = auth_service.logout("invalid_token")
        
        assert result is False
        session_dal_mock.delete.assert_not_called()
    
    # TC-AUTH-SVC-007: 正常系 - 現在のユーザー取得成功
    @patch('app.sys.services.auth_service.verify_token')
    def test_get_current_user_success(self, mock_verify, auth_service, user_dal_mock, session_dal_mock, valid_user_data):
        """現在のユーザー取得成功"""
        mock_verify.return_value = {"sub": "user-001", "username": "testuser", "role": "user"}
        session_dal_mock.find_by_token.return_value = {"sessionId": "session-001"}
        user_dal_mock.find_one.return_value = valid_user_data
        
        user = auth_service.get_current_user("valid_token")
        
        assert user.id == "user-001"
        assert user.username == "testuser"
    
    # TC-AUTH-SVC-008: 異常系 - 無効なトークン
    @patch('app.sys.services.auth_service.verify_token')
    def test_get_current_user_invalid_token(self, mock_verify, auth_service):
        """無効なトークン"""
        mock_verify.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            auth_service.get_current_user("invalid_token")
        
        assert exc.value.status_code == 401
        assert "ERR-SYS-AUTH-002" in str(exc.value.detail)
    
    # TC-AUTH-SVC-009: 異常系 - セッション存在しない
    @patch('app.sys.services.auth_service.verify_token')
    def test_get_current_user_no_session(self, mock_verify, auth_service, session_dal_mock):
        """セッション存在しない"""
        mock_verify.return_value = {"sub": "user-001"}
        session_dal_mock.find_by_token.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            auth_service.get_current_user("valid_token")
        
        assert exc.value.status_code == 401
        assert "ERR-SYS-AUTH-005" in str(exc.value.detail)
    
    # TC-AUTH-SVC-010: 正常系 - パスワード変更成功
    @patch('app.sys.services.auth_service.hash_password')
    def test_change_password_success(self, mock_hash, auth_service, user_dal_mock, valid_user_data):
        """パスワード変更成功"""
        user_dal_mock.find_one.return_value = valid_user_data
        user_dal_mock.update.return_value = True
        mock_hash.return_value = "new_hashed_password"
        
        result = auth_service.change_password("user-001", "SecurePass123!", "NewSecure456!")
        
        assert result is True
        user_dal_mock.update.assert_called_once()
    
    # TC-AUTH-SVC-011: 異常系 - 現在のパスワード不一致
    def test_change_password_wrong_current(self, auth_service, user_dal_mock, valid_user_data):
        """現在のパスワード不一致"""
        user_dal_mock.find_one.return_value = valid_user_data
        
        with pytest.raises(HTTPException) as exc:
            auth_service.change_password("user-001", "WrongPassword", "NewSecure456!")
        
        assert exc.value.status_code == 400
        assert "ERR-SYS-AUTH-007" in str(exc.value.detail)
    
    # TC-AUTH-SVC-012: 異常系 - 新しいパスワードが短すぎる
    def test_change_password_too_short(self, auth_service, user_dal_mock, valid_user_data):
        """新しいパスワードが短すぎる"""
        user_dal_mock.find_one.return_value = valid_user_data
        
        with pytest.raises(HTTPException) as exc:
            auth_service.change_password("user-001", "SecurePass123!", "short")
        
        assert exc.value.status_code == 400
        assert "ERR-SYS-AUTH-008" in str(exc.value.detail)
    
    # TC-AUTH-SVC-013: 境界値 - パスワード長8文字（最小）
    @patch('app.sys.services.auth_service.hash_password')
    def test_change_password_min_length(self, mock_hash, auth_service, user_dal_mock, valid_user_data):
        """パスワード最小長（8文字）"""
        user_dal_mock.find_one.return_value = valid_user_data
        user_dal_mock.update.return_value = True
        mock_hash.return_value = "new_hashed_password"
        
        result = auth_service.change_password("user-001", "SecurePass123!", "12345678")
        
        assert result is True
    
    # TC-AUTH-SVC-014: 境界値 - パスワード長7文字（最小-1）
    def test_change_password_below_min_length(self, auth_service, user_dal_mock, valid_user_data):
        """パスワード最小長未満（7文字）"""
        user_dal_mock.find_one.return_value = valid_user_data
        
        with pytest.raises(HTTPException) as exc:
            auth_service.change_password("user-001", "SecurePass123!", "1234567")
        
        assert exc.value.status_code == 400
    
    # TC-AUTH-SVC-015: 異常系 - ユーザーが存在しない
    def test_change_password_user_not_found(self, auth_service, user_dal_mock):
        """ユーザーが存在しない"""
        user_dal_mock.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            auth_service.change_password("nonexistent", "OldPass123!", "NewPass456!")
        
        assert exc.value.status_code == 404
        assert "ERR-SYS-USER-001" in str(exc.value.detail)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
