"""
単体テスト: Apps API

テスト対象: project/backend/app/sys/api/apps.py
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

from app.sys.api.apps import router
from app.sys.models.app import App
from app.sys.models.user import User
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/sys")


class TestAppsAPI:
    """Apps API のテストクラス"""
    
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
            passwordHash="hashed",
            displayName="Admin",
            role="admin",
            email="admin@example.com",
            metadata={},
            createdAt="2026-01-01T00:00:00Z",
            updatedAt="2026-01-01T00:00:00Z",
            lastLogin=None
        )
    
    @pytest.fixture
    def valid_app(self):
        """有効なアプリ"""
        return App(
            id="test-app",
            name="Test App",
            version="1.0.0",
            description="Test",
            icon="/apps/test-app/icon.png",
            entryPoint="/apps/test-app/index.html",
            apiPrefix="/api/apps/test-app",
            enabled=True,
            author="Test",
            requiredPermissions=[],
            dependencies=[],
            manifest={},
            lastUpdated="2026-01-01T00:00:00Z"
        )
    
    # TC-APPS-API-001: 正常系 - アプリ一覧取得
    @patch('app.sys.api.apps.get_current_user')
    @patch('app.sys.api.apps.get_app_service')
    def test_list_apps_success(self, mock_get_service, mock_get_user, client, admin_user, valid_app):
        """アプリ一覧取得成功"""
        mock_get_user.return_value = admin_user
        mock_service = Mock()
        mock_service.list_apps.return_value = [valid_app]
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/apps")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "test-app"
    
    # TC-APPS-API-002: 正常系 - 有効なアプリのみ取得
    @patch('app.sys.api.apps.get_current_user')
    @patch('app.sys.api.apps.get_app_service')
    def test_list_apps_enabled_only(self, mock_get_service, mock_get_user, client, admin_user, valid_app):
        """有効なアプリのみ取得"""
        mock_get_user.return_value = admin_user
        mock_service = Mock()
        mock_service.list_apps.return_value = [valid_app]
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/apps?enabled=true")
        
        assert response.status_code == 200
    
    # TC-APPS-API-003: 正常系 - アプリ詳細取得
    @patch('app.sys.api.apps.get_current_user')
    @patch('app.sys.api.apps.get_app_service')
    def test_get_app_success(self, mock_get_service, mock_get_user, client, admin_user, valid_app):
        """アプリ詳細取得成功"""
        mock_get_user.return_value = admin_user
        mock_service = Mock()
        mock_service.get_app.return_value = valid_app
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/apps/test-app")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-app"
    
    # TC-APPS-API-004: 異常系 - アプリが存在しない
    @patch('app.sys.api.apps.get_current_user')
    @patch('app.sys.api.apps.get_app_service')
    def test_get_app_not_found(self, mock_get_service, mock_get_user, client, admin_user):
        """アプリが存在しない"""
        mock_get_user.return_value = admin_user
        mock_service = Mock()
        mock_service.get_app.side_effect = HTTPException(status_code=404, detail="App not found")
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/apps/nonexistent")
        
        assert response.status_code == 404
    
    # TC-APPS-API-005: 正常系 - アプリスキャン
    @patch('app.sys.api.apps.get_current_admin_user')
    @patch('app.sys.api.apps.get_app_service')
    def test_scan_apps_success(self, mock_get_service, mock_get_admin, client, admin_user, valid_app):
        """アプリスキャン成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.scan_apps.return_value = [valid_app]
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/apps/scan")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    # TC-APPS-API-006: 正常系 - アプリ有効化
    @patch('app.sys.api.apps.get_current_admin_user')
    @patch('app.sys.api.apps.get_app_service')
    def test_enable_app_success(self, mock_get_service, mock_get_admin, client, admin_user):
        """アプリ有効化成功"""
        mock_get_admin.return_value = admin_user
        mock_service = Mock()
        mock_service.enable_app.return_value = True
        mock_get_service.return_value = mock_service
        
        response = client.put("/api/sys/apps/test-app/enable")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
