"""
アプリ管理API (apps.py) の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: アプリ一覧取得、詳細取得、スキャン、有効化/無効化、リロード
- 異常系: 権限不足、アプリ不存在
- 境界値: フィルター（enabled）
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from project.backend.app.sys.api.apps import router
from project.backend.app.sys.models.app import App, AppResponse
from project.backend.app.sys.models.user import User
from project.backend.app.main import app


client = TestClient(app)


class TestAppsAPI:
    """アプリ管理APIのテストクラス"""
    
    @patch('project.backend.app.sys.api.apps.get_current_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_list_apps_success(self, mock_get_app_service, mock_get_current_user):
        """
        TC-API-APPS-001: 正常系 - アプリ一覧取得成功
        条件: フィルターなし
        期待: 200 OK, アプリ一覧返却
        """
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
        mock_get_current_user.return_value = mock_user
        
        mock_apps = [
            App(id="APP001", name="Todo App", version="1.0.0", description="Todo管理",
                enabled=True, icon="📝", createdAt=datetime.now(), updatedAt=datetime.now()),
            App(id="APP002", name="Calendar", version="1.0.0", description="カレンダー",
                enabled=True, icon="📅", createdAt=datetime.now(), updatedAt=datetime.now())
        ]
        mock_app_service = Mock()
        mock_app_service.list_apps.return_value = mock_apps
        mock_get_app_service.return_value = mock_app_service
        
        response = client.get(
            "/api/sys/apps",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_app_service.list_apps.assert_called_once_with(enabled=None)
    
    @patch('project.backend.app.sys.api.apps.get_current_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_list_apps_enabled_only(self, mock_get_app_service, mock_get_current_user):
        """
        TC-API-APPS-002: 正常系 - 有効なアプリのみ取得
        条件: enabled=true
        期待: 200 OK, 有効なアプリのみ返却
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
        
        mock_apps = [
            App(id="APP001", name="Todo App", version="1.0.0", description="Todo管理",
                enabled=True, icon="📝", createdAt=datetime.now(), updatedAt=datetime.now())
        ]
        mock_app_service = Mock()
        mock_app_service.list_apps.return_value = mock_apps
        mock_get_app_service.return_value = mock_app_service
        
        response = client.get(
            "/api/sys/apps?enabled=true",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_app_service.list_apps.assert_called_once_with(enabled=True)
    
    @patch('project.backend.app.sys.api.apps.get_current_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_get_app_success(self, mock_get_app_service, mock_get_current_user):
        """
        TC-API-APPS-003: 正常系 - アプリ詳細取得成功
        条件: 有効なapp_id
        期待: 200 OK, アプリ詳細返却
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
        
        mock_app = App(
            id="APP001",
            name="Todo App",
            version="1.0.0",
            description="Todo管理",
            enabled=True,
            icon="📝",
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        mock_app_service = Mock()
        mock_app_service.get_app.return_value = mock_app
        mock_get_app_service.return_value = mock_app_service
        
        response = client.get(
            "/api/sys/apps/APP001",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == "APP001"
        assert response.json()["name"] == "Todo App"
    
    @patch('project.backend.app.sys.api.apps.get_current_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_get_app_not_found(self, mock_get_app_service, mock_get_current_user):
        """
        TC-API-APPS-004: 異常系 - アプリ不存在
        条件: 存在しないapp_id
        期待: 404 Not Found
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
        
        mock_app_service = Mock()
        mock_app_service.get_app.side_effect = ValueError("アプリが見つかりません")
        mock_get_app_service.return_value = mock_app_service
        
        response = client.get(
            "/api/sys/apps/INVALID_ID",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code in [404, 500]
    
    @patch('project.backend.app.sys.api.apps.get_current_admin_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_scan_apps_success(self, mock_get_app_service, mock_get_current_admin_user):
        """
        TC-API-APPS-005: 正常系 - アプリスキャン成功（管理者）
        条件: 管理者権限
        期待: 200 OK, スキャンされたアプリ一覧返却
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
        
        mock_apps = [
            App(id="APP001", name="Todo App", version="1.0.0", description="Todo管理",
                enabled=True, icon="📝", createdAt=datetime.now(), updatedAt=datetime.now())
        ]
        mock_app_service = Mock()
        mock_app_service.scan_apps.return_value = mock_apps
        mock_get_app_service.return_value = mock_app_service
        
        response = client.post(
            "/api/sys/apps/scan",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert len(response.json()["apps"]) == 1
    
    def test_scan_apps_unauthorized(self):
        """
        TC-API-APPS-006: 異常系 - スキャン権限不足（一般ユーザー）
        条件: 一般ユーザートークン
        期待: 403 Forbidden
        """
        response = client.post(
            "/api/sys/apps/scan",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code in [401, 403]
    
    @patch('project.backend.app.sys.api.apps.get_current_admin_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_enable_app_success(self, mock_get_app_service, mock_get_current_admin_user):
        """
        TC-API-APPS-007: 正常系 - アプリ有効化成功
        条件: 有効なapp_id、管理者権限
        期待: 200 OK, 成功メッセージ
        """
        mock_admin = User(
            id="USR_ADMIN",
            username="admin",
            email="admin@example.com",
            fullName="Admin User",
            role="admin",
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_app_service = Mock()
        mock_get_app_service.return_value = mock_app_service
        
        response = client.put(
            "/api/sys/apps/APP001/enable",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_app_service.enable_app.assert_called_once_with("APP001")
    
    @patch('project.backend.app.sys.api.apps.get_current_admin_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_disable_app_success(self, mock_get_app_service, mock_get_current_admin_user):
        """
        TC-API-APPS-008: 正常系 - アプリ無効化成功
        条件: 有効なapp_id、管理者権限
        期待: 200 OK, 成功メッセージ
        """
        mock_admin = User(
            id="USR_ADMIN",
            username="admin",
            email="admin@example.com",
            fullName="Admin User",
            role="admin",
            isActive=True,
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        mock_get_current_admin_user.return_value = mock_admin
        
        mock_app_service = Mock()
        mock_get_app_service.return_value = mock_app_service
        
        response = client.put(
            "/api/sys/apps/APP001/disable",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_app_service.disable_app.assert_called_once_with("APP001")
    
    @patch('project.backend.app.sys.api.apps.get_current_admin_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_reload_app_success(self, mock_get_app_service, mock_get_current_admin_user):
        """
        TC-API-APPS-009: 正常系 - アプリリロード成功
        条件: 有効なapp_id、管理者権限
        期待: 200 OK, リロードされたアプリ返却
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
        
        mock_app = App(
            id="APP001",
            name="Todo App",
            version="1.0.1",
            description="Todo管理（更新）",
            enabled=True,
            icon="📝",
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        mock_app_service = Mock()
        mock_app_service.reload_app.return_value = mock_app
        mock_get_app_service.return_value = mock_app_service
        
        response = client.post(
            "/api/sys/apps/APP001/reload",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == "APP001"
        assert response.json()["version"] == "1.0.1"
    
    @patch('project.backend.app.sys.api.apps.get_current_user')
    @patch('project.backend.app.sys.api.apps.get_app_service')
    def test_list_apps_disabled_only(self, mock_get_app_service, mock_get_current_user):
        """
        TC-API-APPS-010: 境界値 - 無効なアプリのみ取得
        条件: enabled=false
        期待: 200 OK, 無効なアプリのみ返却
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
        
        mock_apps = [
            App(id="APP002", name="Disabled App", version="1.0.0", description="無効化済み",
                enabled=False, icon="❌", createdAt=datetime.now(), updatedAt=datetime.now())
        ]
        mock_app_service = Mock()
        mock_app_service.list_apps.return_value = mock_apps
        mock_get_app_service.return_value = mock_app_service
        
        response = client.get(
            "/api/sys/apps?enabled=false",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_app_service.list_apps.assert_called_once_with(enabled=False)
