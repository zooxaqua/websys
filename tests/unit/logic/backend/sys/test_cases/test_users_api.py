"""
単体テスト: Users API

テスト対象: project/backend/app/sys/api/users.py
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

from app.sys.api.users import router
from app.sys.models.user import User, UserCreate, UserUpdate
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/sys")


class TestUsersAPI:
    """Users API のテストクラス"""
    
    @pytest.fixture
    def client(self):
        """TestClient インスタンス"""
        return TestClient(app)
    
    @pytest.fixture
    def admin_user(self):
        """管理者ユーザー"""
        return User(
            id="admin-001",
            username="admin",
            passwordHash="hashed_password",
            displayName="Admin",
            role="admin",
            email="admin@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
    
    @pytest.fixture
    def regular_user(self):
        """通常ユーザー"""
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
    
    # TC-USERS-API-001: 正常系 - ユーザー一覧取得
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_list_users_success(self, mock_get_service, mock_get_admin, client, admin_user, regular_user):
        """ユーザー一覧取得成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.list_users.return_value = ([regular_user], 1)
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/users")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["users"]) == 1
        assert data["users"][0]["username"] == "testuser"
    
    # TC-USERS-API-002: 正常系 - ロールでフィルタ
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_list_users_filter_by_role(self, mock_get_service, mock_get_admin, client, admin_user):
        """ロールでフィルタ"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.list_users.return_value = ([admin_user], 1)
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/users?role=admin")
        
        assert response.status_code == 200
        mock_service.list_users.assert_called_once()
    
    # TC-USERS-API-003: 正常系 - ユーザー詳細取得
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_get_user_success(self, mock_get_service, mock_get_admin, client, admin_user, regular_user):
        """ユーザー詳細取得成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.get_user.return_value = regular_user
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/users/user-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    # TC-USERS-API-004: 異常系 - ユーザーが存在しない
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_get_user_not_found(self, mock_get_service, mock_get_admin, client, admin_user):
        """ユーザーが存在しない"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.get_user.side_effect = HTTPException(status_code=404, detail="User not found")
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/users/nonexistent")
        
        assert response.status_code == 404
    
    # TC-USERS-API-005: 正常系 - ユーザー作成
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_create_user_success(self, mock_get_service, mock_get_admin, client, admin_user, regular_user):
        """ユーザー作成成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.create_user.return_value = regular_user
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/users", json={
            "username": "newuser",
            "password": "NewPass123!",
            "email": "new@example.com",
            "displayName": "New User",
            "role": "user"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
    
    # TC-USERS-API-006: 異常系 - ユーザー作成失敗（重複）
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_create_user_duplicate(self, mock_get_service, mock_get_admin, client, admin_user):
        """ユーザー作成失敗（重複）"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.create_user.side_effect = HTTPException(status_code=409, detail="User already exists")
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/users", json={
            "username": "testuser",
            "password": "Pass123!",
            "email": "test@example.com",
            "displayName": "Test",
            "role": "user"
        })
        
        assert response.status_code == 409
    
    # TC-USERS-API-007: 正常系 - ユーザー更新
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_update_user_success(self, mock_get_service, mock_get_admin, client, admin_user, regular_user):
        """ユーザー更新成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        updated_user = regular_user.model_copy(update={"email": "updated@example.com"})
        mock_service.update_user.return_value = updated_user
        mock_get_service.return_value = mock_service
        
        response = client.put("/api/sys/users/user-001", json={
            "email": "updated@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
    
    # TC-USERS-API-008: 正常系 - ユーザー削除
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_delete_user_success(self, mock_get_service, mock_get_admin, client, admin_user):
        """ユーザー削除成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.delete_user.return_value = True
        mock_get_service.return_value = mock_service
        
        response = client.delete("/api/sys/users/user-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    # TC-USERS-API-009: 異常系 - 管理者権限なし
    @patch('app.sys.api.users.get_current_admin_user')
    def test_list_users_forbidden(self, mock_get_admin, client):
        """管理者権限なし"""
        mock_get_admin.side_effect = HTTPException(status_code=403, detail="Forbidden")
        
        response = client.get("/api/sys/users")
        
        assert response.status_code == 403
    
    # TC-USERS-API-010: 境界値 - ページネーション
    @patch('app.sys.api.users.get_current_admin_user')
    @patch('app.sys.api.users.get_user_service')
    def test_list_users_pagination(self, mock_get_service, mock_get_admin, client, admin_user, regular_user):
        """ページネーション"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.list_users.return_value = ([regular_user], 100)
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/users?limit=10&offset=0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
