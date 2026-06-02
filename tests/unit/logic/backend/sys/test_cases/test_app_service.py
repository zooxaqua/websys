"""
単体テスト: AppService

テスト対象: project/backend/app/sys/services/app_service.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.services.app_service import AppService
from fastapi import HTTPException


class TestAppService:
    """AppService のテストクラス"""
    
    @pytest.fixture
    def app_dal_mock(self):
        """AppDAL のモック"""
        return Mock()
    
    @pytest.fixture
    def app_service(self, app_dal_mock):
        """AppService インスタンス"""
        return AppService(app_dal_mock)
    
    @pytest.fixture
    def valid_app_data(self):
        """有効なアプリデータ"""
        return {
            "id": "test-app",
            "name": "Test App",
            "version": "1.0.0",
            "description": "Test application",
            "icon": "/apps/test-app/icon.png",
            "entryPoint": "/apps/test-app/frontend/index.html",
            "apiPrefix": "/api/apps/test-app",
            "enabled": True,
            "author": "Test Author",
            "requiredPermissions": ["read"],
            "dependencies": [],
            "manifest": {},
            "lastUpdated": "2026-01-01T00:00:00Z"
        }
    
    # TC-APP-SVC-001: 正常系 - アプリ一覧取得
    def test_list_apps_all(self, app_service, app_dal_mock, valid_app_data):
        """アプリ一覧取得（全件）"""
        app_dal_mock.find.return_value = [valid_app_data]
        
        apps = app_service.list_apps()
        
        assert len(apps) == 1
        assert apps[0].id == "test-app"
        app_dal_mock.find.assert_called_once_with({})
    
    # TC-APP-SVC-002: 正常系 - 有効なアプリのみ取得
    def test_list_apps_enabled_only(self, app_service, app_dal_mock, valid_app_data):
        """有効なアプリのみ取得"""
        app_dal_mock.find.return_value = [valid_app_data]
        
        apps = app_service.list_apps(enabled=True)
        
        app_dal_mock.find.assert_called_once_with({"enabled": True})
    
    # TC-APP-SVC-003: 正常系 - アプリ詳細取得
    def test_get_app_success(self, app_service, app_dal_mock, valid_app_data):
        """アプリ詳細取得成功"""
        app_dal_mock.find_one.return_value = valid_app_data
        
        app = app_service.get_app("test-app")
        
        assert app.id == "test-app"
        assert app.name == "Test App"
    
    # TC-APP-SVC-004: 異常系 - アプリが存在しない
    def test_get_app_not_found(self, app_service, app_dal_mock):
        """アプリが存在しない"""
        app_dal_mock.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            app_service.get_app("nonexistent")
        
        assert exc.value.status_code == 404
        assert "ERR-SYS-APPS-001" in str(exc.value.detail)
    
    # TC-APP-SVC-005: 正常系 - アプリ有効化
    def test_enable_app_success(self, app_service, app_dal_mock, valid_app_data):
        """アプリ有効化成功"""
        disabled_app = valid_app_data.copy()
        disabled_app["enabled"] = False
        app_dal_mock.find_one.return_value = disabled_app
        app_dal_mock.update.return_value = True
        
        result = app_service.enable_app("test-app")
        
        assert result is True
        app_dal_mock.update.assert_called_once()
    
    # TC-APP-SVC-006: 境界値 - 空のアプリ一覧
    def test_list_apps_empty(self, app_service, app_dal_mock):
        """空のアプリ一覧"""
        app_dal_mock.find.return_value = []
        
        apps = app_service.list_apps()
        
        assert len(apps) == 0
    
    # TC-APP-SVC-007: MCDC - enabled=True の場合のフィルタ
    def test_list_apps_enabled_true(self, app_service, app_dal_mock, valid_app_data):
        """enabled=True でフィルタ"""
        app_dal_mock.find.return_value = [valid_app_data]
        
        apps = app_service.list_apps(enabled=True)
        
        # enabled=True でfindが呼ばれることを確認
        call_args = app_dal_mock.find.call_args[0][0]
        assert call_args == {"enabled": True}
    
    # TC-APP-SVC-008: MCDC - enabled=False の場合のフィルタ
    def test_list_apps_enabled_false(self, app_service, app_dal_mock, valid_app_data):
        """enabled=False でフィルタ"""
        disabled_app = valid_app_data.copy()
        disabled_app["enabled"] = False
        app_dal_mock.find.return_value = [disabled_app]
        
        apps = app_service.list_apps(enabled=False)
        
        # enabled=False でfindが呼ばれることを確認
        call_args = app_dal_mock.find.call_args[0][0]
        assert call_args == {"enabled": False}
    
    # TC-APP-SVC-009: MCDC - enabled=None の場合（フィルタなし）
    def test_list_apps_enabled_none(self, app_service, app_dal_mock, valid_app_data):
        """enabled=None（フィルタなし）"""
        app_dal_mock.find.return_value = [valid_app_data]
        
        apps = app_service.list_apps(enabled=None)
        
        # 空の条件でfindが呼ばれることを確認
        call_args = app_dal_mock.find.call_args[0][0]
        assert call_args == {}
    
    # TC-APP-SVC-010: 正常系 - 複数アプリ取得
    def test_list_apps_multiple(self, app_service, app_dal_mock, valid_app_data):
        """複数アプリ取得"""
        app2 = valid_app_data.copy()
        app2["id"] = "app2"
        app2["name"] = "App 2"
        app_dal_mock.find.return_value = [valid_app_data, app2]
        
        apps = app_service.list_apps()
        
        assert len(apps) == 2
        assert apps[0].id == "test-app"
        assert apps[1].id == "app2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
