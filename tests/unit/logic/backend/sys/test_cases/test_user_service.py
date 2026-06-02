"""
単体テスト: UserService

テスト対象: project/backend/app/sys/services/user_service.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.services.user_service import UserService
from app.sys.models.user import UserCreate, UserUpdate
from fastapi import HTTPException


class TestUserService:
    """UserService のテストクラス"""
    
    @pytest.fixture
    def user_dal_mock(self):
        """UserDAL のモック"""
        return Mock()
    
    @pytest.fixture
    def user_service(self, user_dal_mock):
        """UserService インスタンス"""
        return UserService(user_dal_mock)
    
    @pytest.fixture
    def valid_user_data(self):
        """有効なユーザーデータ"""
        return {
            "id": "user-001",
            "username": "testuser",
            "passwordHash": "hashed_password",
            "displayName": "Test User",
            "role": "user",
            "email": "test@example.com",
            "metadata": {},
            "createdAt": "2026-01-01T00:00:00Z",
            "updatedAt": "2026-01-01T00:00:00Z",
            "lastLogin": None
        }
    
    # TC-USER-SVC-001: 正常系 - ユーザー一覧取得
    def test_list_users_success(self, user_service, user_dal_mock, valid_user_data):
        """ユーザー一覧取得成功"""
        user_dal_mock.find.return_value = [valid_user_data]
        user_dal_mock.count.return_value = 1
        
        users, total = user_service.list_users()
        
        assert len(users) == 1
        assert total == 1
        assert users[0].username == "testuser"
    
    # TC-USER-SVC-002: 正常系 - ロールでフィルタ
    def test_list_users_filter_by_role(self, user_service, user_dal_mock, valid_user_data):
        """ロールでフィルタ"""
        user_dal_mock.find.return_value = [valid_user_data]
        user_dal_mock.count.return_value = 1
        
        users, total = user_service.list_users(role="user")
        
        user_dal_mock.find.assert_called_once()
        call_args = user_dal_mock.find.call_args[0][0]
        assert call_args["role"] == "user"
    
    # TC-USER-SVC-003: 正常系 - ユーザー詳細取得
    def test_get_user_success(self, user_service, user_dal_mock, valid_user_data):
        """ユーザー詳細取得成功"""
        user_dal_mock.find_one.return_value = valid_user_data
        
        user = user_service.get_user("user-001")
        
        assert user.id == "user-001"
        assert user.username == "testuser"
    
    # TC-USER-SVC-004: 異常系 - ユーザーが存在しない
    def test_get_user_not_found(self, user_service, user_dal_mock):
        """ユーザーが存在しない"""
        user_dal_mock.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            user_service.get_user("nonexistent")
        
        assert exc.value.status_code == 404
        assert "ERR-SYS-USER-001" in str(exc.value.detail)
    
    # TC-USER-SVC-005: 正常系 - ユーザー作成成功
    def test_create_user_success(self, user_service, user_dal_mock):
        """ユーザー作成成功"""
        user_dal_mock.find_by_username.return_value = None
        user_dal_mock.find_by_email.return_value = None
        user_dal_mock.insert.return_value = True
        
        user_create = UserCreate(
            username="newuser",
            password="NewPass123!",
            email="new@example.com",
            displayName="New User",
            role="user"
        )
        
        user = user_service.create_user(user_create)
        
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        user_dal_mock.insert.assert_called_once()
    
    # TC-USER-SVC-006: 異常系 - ユーザー名重複
    def test_create_user_duplicate_username(self, user_service, user_dal_mock, valid_user_data):
        """ユーザー名重複"""
        user_dal_mock.find_by_username.return_value = valid_user_data
        
        user_create = UserCreate(
            username="testuser",
            password="Pass123!",
            email="new@example.com",
            displayName="New User",
            role="user"
        )
        
        with pytest.raises(HTTPException) as exc:
            user_service.create_user(user_create)
        
        assert exc.value.status_code == 409
        assert "ERR-SYS-USER-002" in str(exc.value.detail)
    
    # TC-USER-SVC-007: 異常系 - メールアドレス重複
    def test_create_user_duplicate_email(self, user_service, user_dal_mock, valid_user_data):
        """メールアドレス重複"""
        user_dal_mock.find_by_username.return_value = None
        user_dal_mock.find_by_email.return_value = valid_user_data
        
        user_create = UserCreate(
            username="newuser",
            password="Pass123!",
            email="test@example.com",
            displayName="New User",
            role="user"
        )
        
        with pytest.raises(HTTPException) as exc:
            user_service.create_user(user_create)
        
        assert exc.value.status_code == 409
        assert "ERR-SYS-USER-003" in str(exc.value.detail)
    
    # TC-USER-SVC-008: 正常系 - ユーザー更新成功
    def test_update_user_success(self, user_service, user_dal_mock, valid_user_data):
        """ユーザー更新成功"""
        user_dal_mock.find_one.return_value = valid_user_data
        user_dal_mock.find_by_email.return_value = None
        user_dal_mock.update.return_value = True
        
        updated_data = valid_user_data.copy()
        updated_data["email"] = "updated@example.com"
        user_dal_mock.find_one.side_effect = [valid_user_data, updated_data]
        
        user_update = UserUpdate(email="updated@example.com")
        
        user = user_service.update_user("user-001", user_update)
        
        assert user.email == "updated@example.com"
        user_dal_mock.update.assert_called_once()
    
    # TC-USER-SVC-009: 異常系 - 更新対象ユーザーが存在しない
    def test_update_user_not_found(self, user_service, user_dal_mock):
        """更新対象ユーザーが存在しない"""
        user_dal_mock.find_one.return_value = None
        
        user_update = UserUpdate(email="new@example.com")
        
        with pytest.raises(HTTPException) as exc:
            user_service.update_user("nonexistent", user_update)
        
        assert exc.value.status_code == 404
    
    # TC-USER-SVC-010: 異常系 - メールアドレス重複（更新時）
    def test_update_user_duplicate_email(self, user_service, user_dal_mock, valid_user_data):
        """メールアドレス重複（更新時）"""
        user_dal_mock.find_one.return_value = valid_user_data
        other_user = valid_user_data.copy()
        other_user["id"] = "other-user"
        user_dal_mock.find_by_email.return_value = other_user
        
        user_update = UserUpdate(email="other@example.com")
        
        with pytest.raises(HTTPException) as exc:
            user_service.update_user("user-001", user_update)
        
        assert exc.value.status_code == 409
        assert "ERR-SYS-USER-003" in str(exc.value.detail)
    
    # TC-USER-SVC-011: 正常系 - ユーザー削除成功
    def test_delete_user_success(self, user_service, user_dal_mock, valid_user_data):
        """ユーザー削除成功"""
        user_dal_mock.find_one.return_value = valid_user_data
        user_dal_mock.delete.return_value = True
        
        result = user_service.delete_user("user-001", "current-user")
        
        assert result is True
        user_dal_mock.delete.assert_called_once_with("user-001")
    
    # TC-USER-SVC-012: 異常系 - 自己削除防止
    def test_delete_user_self_deletion(self, user_service, user_dal_mock):
        """自己削除防止"""
        with pytest.raises(HTTPException) as exc:
            user_service.delete_user("user-001", "user-001")
        
        assert exc.value.status_code == 400
        assert "ERR-SYS-USER-007" in str(exc.value.detail)
        user_dal_mock.delete.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
