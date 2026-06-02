"""
UserDAL の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: ユーザー検索（username, email）、最終ログイン更新
- 異常系: 存在しないユーザー検索
- 境界値: 空データ、重複検索
"""
import pytest
import tempfile
from datetime import datetime, timezone
from unittest.mock import patch

# テスト対象
from project.backend.app.sys.dal.user_dal import UserDAL


class TestUserDAL:
    """UserDAL のテストクラス"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """テスト用一時ディレクトリ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def dal(self, temp_data_dir):
        """テスト用DALインスタンス"""
        return UserDAL(data_dir=temp_data_dir)
    
    def test_find_by_username_existing(self, dal):
        """
        TC-USER-DAL-001: find_by_username() - 存在するユーザー検索
        条件: usernameに一致するユーザーが存在
        期待: ユーザーデータが返される
        """
        user_data = {
            "id": "user-001",
            "username": "testuser",
            "email": "test@example.com",
            "role": "user"
        }
        dal.insert(user_data)
        
        result = dal.find_by_username("testuser")
        
        assert result is not None
        assert result["username"] == "testuser"
        assert result["email"] == "test@example.com"
    
    def test_find_by_username_non_existing(self, dal):
        """
        TC-USER-DAL-002: find_by_username() - 存在しないユーザー検索
        条件: usernameに一致するユーザーが存在しない
        期待: None が返される
        """
        result = dal.find_by_username("nonexistent")
        
        assert result is None
    
    def test_find_by_username_case_sensitive(self, dal):
        """
        TC-USER-DAL-003: find_by_username() - 大文字小文字区別
        条件: usernameが大文字小文字で異なる
        期待: 完全一致のみ検索される
        """
        dal.insert({"id": "user-001", "username": "TestUser", "email": "test@example.com"})
        
        result_upper = dal.find_by_username("TestUser")
        result_lower = dal.find_by_username("testuser")
        
        assert result_upper is not None
        assert result_lower is None
    
    def test_find_by_email_existing(self, dal):
        """
        TC-USER-DAL-004: find_by_email() - 存在するメールアドレス検索
        条件: emailに一致するユーザーが存在
        期待: ユーザーデータが返される
        """
        user_data = {
            "id": "user-002",
            "username": "john",
            "email": "john@example.com",
            "role": "admin"
        }
        dal.insert(user_data)
        
        result = dal.find_by_email("john@example.com")
        
        assert result is not None
        assert result["email"] == "john@example.com"
        assert result["username"] == "john"
    
    def test_find_by_email_non_existing(self, dal):
        """
        TC-USER-DAL-005: find_by_email() - 存在しないメールアドレス検索
        条件: emailに一致するユーザーが存在しない
        期待: None が返される
        """
        result = dal.find_by_email("nonexistent@example.com")
        
        assert result is None
    
    def test_update_last_login_existing_user(self, dal):
        """
        TC-USER-DAL-006: update_last_login() - 存在するユーザーの更新
        条件: 有効なuser_idで最終ログイン時刻を更新
        期待: True が返され、lastLoginとupdatedAtが更新される
        """
        user_id = "user-003"
        user_data = {
            "id": user_id,
            "username": "alice",
            "email": "alice@example.com",
            "lastLogin": "2026-05-28T00:00:00Z",
            "updatedAt": "2026-05-28T00:00:00Z"
        }
        dal.insert(user_data)
        
        with patch('project.backend.app.sys.dal.user_dal.datetime') as mock_datetime:
            fixed_now = datetime(2026, 5, 29, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = fixed_now
            
            result = dal.update_last_login(user_id)
        
        assert result is True
        
        updated_user = dal.find_one({"id": user_id})
        assert updated_user["lastLogin"] == "2026-05-29T12:00:00Z"
        assert updated_user["updatedAt"] == "2026-05-29T12:00:00Z"
    
    def test_update_last_login_non_existing_user(self, dal):
        """
        TC-USER-DAL-007: update_last_login() - 存在しないユーザーの更新
        条件: 存在しないuser_idで更新を試行
        期待: False が返される
        """
        result = dal.update_last_login("non-existent-user")
        
        assert result is False
    
    def test_multiple_users_find_by_username(self, dal):
        """
        TC-USER-DAL-008: find_by_username() - 複数ユーザー存在時の検索
        条件: 複数ユーザーが登録されており、1人を検索
        期待: 指定したユーザーのみが返される
        """
        dal.insert({"id": "user-a", "username": "alice", "email": "alice@example.com"})
        dal.insert({"id": "user-b", "username": "bob", "email": "bob@example.com"})
        dal.insert({"id": "user-c", "username": "charlie", "email": "charlie@example.com"})
        
        result = dal.find_by_username("bob")
        
        assert result is not None
        assert result["username"] == "bob"
        assert result["id"] == "user-b"
    
    def test_find_by_email_case_sensitive(self, dal):
        """
        TC-USER-DAL-009: find_by_email() - 大文字小文字区別
        条件: emailが大文字小文字で異なる
        期待: 完全一致のみ検索される
        """
        dal.insert({"id": "user-001", "username": "test", "email": "Test@Example.com"})
        
        result_upper = dal.find_by_email("Test@Example.com")
        result_lower = dal.find_by_email("test@example.com")
        
        assert result_upper is not None
        assert result_lower is None
    
    def test_collection_name_set(self, dal):
        """
        TC-USER-DAL-010: collection_name 設定確認
        条件: UserDALインスタンスを生成
        期待: collection_name が "users" に設定されている
        """
        assert dal.collection_name == "users"
    
    def test_crud_operations_integration(self, dal):
        """
        TC-USER-DAL-011: 統合テスト - CRUD操作の連携
        条件: ユーザー作成→検索→更新→削除
        期待: 全操作が正常に動作する
        """
        # Create
        user_id = dal.insert({
            "id": "user-integration",
            "username": "integrationuser",
            "email": "integration@example.com",
            "role": "user"
        })
        
        # Read
        user = dal.find_by_username("integrationuser")
        assert user is not None
        
        # Update
        with patch('project.backend.app.sys.dal.user_dal.datetime') as mock_datetime:
            fixed_now = datetime(2026, 5, 29, 15, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = fixed_now
            result = dal.update_last_login(user_id)
        
        assert result is True
        
        # Delete
        deleted = dal.delete(user_id)
        assert deleted is True
        
        # Verify deletion
        user_after_delete = dal.find_by_username("integrationuser")
        assert user_after_delete is None
    
    def test_boundary_empty_database(self, dal):
        """
        TC-USER-DAL-012: 境界値 - 空データベース
        条件: ユーザーが1件も登録されていない
        期待: 全ての検索でNoneが返される
        """
        result_username = dal.find_by_username("anyuser")
        result_email = dal.find_by_email("any@example.com")
        
        assert result_username is None
        assert result_email is None
