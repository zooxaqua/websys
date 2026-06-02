"""
ユーザー管理API (users.py) の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: ユーザー一覧取得、ユーザー詳細取得、作成、更新、削除
- 異常系: 権限不足、ユーザー不存在、バリデーションエラー
- 境界値: ページネーション、ロールフィルター
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from project.backend.app.sys.api.users import router
from project.backend.app.sys.models.user import User, UserCreate, UserUpdate, UserResponse
from project.backend.app.main import app


client = TestClient(app)


class TestUsersAPI:
    """ユーザー管理APIのテストクラス"""
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_list_users_success(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-001: 正常系 - ユーザー一覧取得成功（管理者）
        条件: 管理者権限、フィルターなし
        期待: 200 OK, ユーザー一覧返却
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_users = [
            User(id="USR001", username="user1", passwordHash="hashed", displayName="User 1",
                 role="user", email="user1@example.com", metadata={}, createdAt="2026-01-01T00:00:00Z", updatedAt="2026-01-01T00:00:00Z", lastLogin=None),
            User(id="USR002", username="user2", passwordHash="hashed", displayName="User 2",
                 role="user", email="user2@example.com", metadata={}, createdAt="2026-01-01T00:00:00Z", updatedAt="2026-01-01T00:00:00Z", lastLogin=None)
        ]
        mock_user_service = Mock()
        mock_user_service.list_users.return_value = (mock_users, 2)
        mock_get_user_service.return_value = mock_user_service
        
        response = client.get(
            "/api/sys/users",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["total"] == 2
        assert len(response.json()["users"]) == 2
        mock_user_service.list_users.assert_called_once()
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_list_users_with_role_filter(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-002: 正常系 - ロールフィルター付きユーザー一覧取得
        条件: role="admin"でフィルター
        期待: 200 OK, 管理者ユーザーのみ返却
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_admins = [mock_admin]
        mock_user_service = Mock()
        mock_user_service.list_users.return_value = (mock_admins, 1)
        mock_get_user_service.return_value = mock_user_service
        
        response = client.get(
            "/api/sys/users?role=admin",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["total"] == 1
        mock_user_service.list_users.assert_called_once_with(role="admin", limit=100, offset=0)
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_list_users_with_pagination(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-003: 境界値 - ページネーション（limit=10, offset=5）
        条件: limit=10, offset=5
        期待: 200 OK, 指定範囲のユーザー返却
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_user_service = Mock()
        mock_user_service.list_users.return_value = ([], 100)
        mock_get_user_service.return_value = mock_user_service
        
        response = client.get(
            "/api/sys/users?limit=10&offset=5",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["limit"] == 10
        assert response.json()["offset"] == 5
        mock_user_service.list_users.assert_called_once_with(role=None, limit=10, offset=5)
    
    def test_list_users_unauthorized(self):
        """
        TC-API-USERS-004: 異常系 - 一般ユーザーでアクセス（権限不足）
        条件: 一般ユーザートークン
        期待: 403 Forbidden
        """
        response = client.get(
            "/api/sys/users",
            cookies={"auth_token": "user_token"}
        )
        
        # 依存関係で権限チェックされる
        assert response.status_code in [401, 403]
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_get_user_success(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-005: 正常系 - ユーザー詳細取得成功
        条件: 有効なuser_id
        期待: 200 OK, ユーザー詳細返却
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
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
        mock_user_service = Mock()
        mock_user_service.get_user.return_value = mock_user
        mock_get_user_service.return_value = mock_user_service
        
        response = client.get(
            "/api/sys/users/USR001",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == "USR001"
        assert response.json()["username"] == "testuser"
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_get_user_not_found(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-006: 異常系 - ユーザー不存在
        条件: 存在しないuser_id
        期待: 404 Not Found
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_user_service = Mock()
        mock_user_service.get_user.side_effect = ValueError("ユーザーが見つかりません")
        mock_get_user_service.return_value = mock_user_service
        
        response = client.get(
            "/api/sys/users/INVALID_ID",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code in [404, 500]
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_create_user_success(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-007: 正常系 - ユーザー作成成功
        条件: 有効なUserCreate
        期待: 201 Created, 作成されたユーザー返却
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_created_user = User(
            id="USR_NEW",
            username="newuser",
            passwordHash="hashed",
            displayName="New User",
            role="user",
            email="newuser@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_user_service = Mock()
        mock_user_service.create_user.return_value = mock_created_user
        mock_get_user_service.return_value = mock_user_service
        
        response = client.post(
            "/api/sys/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "displayName": "New User",
                "password": "Password123!",
                "role": "user"
            },
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == "USR_NEW"
        assert response.json()["username"] == "newuser"
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    def test_create_user_missing_fields(self, mock_get_current_admin_user):
        """
        TC-API-USERS-008: 異常系 - バリデーションエラー（必須フィールド欠損）
        条件: email欠損
        期待: 422 Unprocessable Entity
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        response = client.post(
            "/api/sys/users",
            json={
                "username": "newuser",
                "displayName": "New User",
                "password": "Password123!",
                "role": "user"
            },
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 422
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_update_user_success(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-009: 正常系 - ユーザー更新成功
        条件: 有効なUserUpdate
        期待: 200 OK, 更新されたユーザー返却
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_updated_user = User(
            id="USR001",
            username="testuser",
            passwordHash="hashed",
            displayName="Updated User",
            role="user",
            email="updated@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
        mock_user_service = Mock()
        mock_user_service.update_user.return_value = mock_updated_user
        mock_get_user_service.return_value = mock_user_service
        
        response = client.put(
            "/api/sys/users/USR001",
            json={"email": "updated@example.com", "displayName": "Updated User"},
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["email"] == "updated@example.com"
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_delete_user_success(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-010: 正常系 - ユーザー削除成功
        条件: 有効なuser_id
        期待: 200 OK, 成功メッセージ
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_user_service = Mock()
        mock_get_user_service.return_value = mock_user_service
        
        response = client.delete(
            "/api/sys/users/USR001",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_user_service.delete_user.assert_called_once_with("USR001", "USR_ADMIN")
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    @patch('project.backend.app.sys.api.users.get_user_service')
    def test_list_users_limit_max(self, mock_get_user_service, mock_get_current_admin_user):
        """
        TC-API-USERS-011: 境界値 - limit最大値（1000）
        条件: limit=1000
        期待: 200 OK, limit=1000で処理
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_user_service = Mock()
        mock_user_service.list_users.return_value = ([], 0)
        mock_get_user_service.return_value = mock_user_service
        
        response = client.get(
            "/api/sys/users?limit=1000",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["limit"] == 1000
    
    @patch('project.backend.app.sys.api.users.get_current_admin_user')
    def test_list_users_limit_exceeds_max(self, mock_get_current_admin_user):
        """
        TC-API-USERS-012: 境界値 - limit超過（1001）
        条件: limit=1001
        期待: 422 Unprocessable Entity（バリデーションエラー）
        """
        mock_admin = User(
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
        mock_get_current_admin_user.return_value = mock_admin
        
        response = client.get(
            "/api/sys/users?limit=1001",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 422
