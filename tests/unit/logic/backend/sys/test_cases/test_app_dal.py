"""
単体テスト: AppDAL

テスト対象: project/backend/app/sys/dal/app_dal.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import json

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.dal.app_dal import AppDAL


class TestAppDAL:
    """AppDAL のテストクラス"""
    
    @pytest.fixture
    def app_dal(self, tmp_path):
        """AppDAL インスタンス"""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return AppDAL(str(data_dir))
    
    @pytest.fixture
    def valid_app_data(self):
        """有効なアプリデータ"""
        return {
            "id": "test-app",
            "name": "Test App",
            "version": "1.0.0",
            "description": "Test",
            "icon": "/apps/test-app/icon.png",
            "entryPoint": "/apps/test-app/index.html",
            "apiPrefix": "/api/apps/test-app",
            "enabled": True,
            "author": "Test",
            "requiredPermissions": [],
            "dependencies": [],
            "manifest": {},
            "lastUpdated": "2026-01-01T00:00:00Z"
        }
    
    # TC-APP-DAL-001: 正常系 - アプリ挿入
    def test_insert_success(self, app_dal, valid_app_data):
        """アプリ挿入成功"""
        app_id = app_dal.insert(valid_app_data)
        
        assert app_id == "test-app"
        # 挿入されたデータを確認
        found = app_dal.find_one({"id": "test-app"})
        assert found is not None
        assert found["name"] == "Test App"
    
    # TC-APP-DAL-002: 正常系 - アプリ検索
    def test_find_one_success(self, app_dal, valid_app_data):
        """アプリ検索成功"""
        app_dal.insert(valid_app_data)
        
        found = app_dal.find_one({"id": "test-app"})
        
        assert found is not None
        assert found["name"] == "Test App"
    
    # TC-APP-DAL-003: 異常系 - 存在しないアプリ
    def test_find_one_not_found(self, app_dal):
        """存在しないアプリ"""
        found = app_dal.find_one({"id": "nonexistent"})
        
        assert found is None
    
    # TC-APP-DAL-004: 正常系 - アプリ更新
    def test_update_success(self, app_dal, valid_app_data):
        """アプリ更新成功"""
        app_dal.insert(valid_app_data)
        
        result = app_dal.update("test-app", {"name": "Updated App"})
        
        assert result is True
        updated = app_dal.find_one({"id": "test-app"})
        assert updated["name"] == "Updated App"
    
    # TC-APP-DAL-005: 正常系 - アプリ削除
    def test_delete_success(self, app_dal, valid_app_data):
        """アプリ削除成功"""
        app_dal.insert(valid_app_data)
        
        result = app_dal.delete("test-app")
        
        assert result is True
        assert app_dal.find_one({"id": "test-app"}) is None
    
    # TC-APP-DAL-006: 正常系 - アプリ一覧取得
    def test_find_all(self, app_dal, valid_app_data):
        """アプリ一覧取得"""
        app_dal.insert(valid_app_data)
        app2 = valid_app_data.copy()
        app2["id"] = "app2"
        app_dal.insert(app2)
        
        apps = app_dal.find({})
        
        assert len(apps) == 2
    
    # TC-APP-DAL-007: 正常系 - 条件検索（enabled=True）
    def test_find_by_enabled(self, app_dal, valid_app_data):
        """有効なアプリのみ取得"""
        app_dal.insert(valid_app_data)
        disabled_app = valid_app_data.copy()
        disabled_app["id"] = "disabled-app"
        disabled_app["enabled"] = False
        app_dal.insert(disabled_app)
        
        enabled_apps = app_dal.find({"enabled": True})
        
        assert len(enabled_apps) == 1
        assert enabled_apps[0]["id"] == "test-app"
    
    # TC-APP-DAL-008: 境界値 - 空のデータ
    def test_find_empty(self, app_dal):
        """空のデータ"""
        apps = app_dal.find({})
        
        assert len(apps) == 0
    
    # TC-APP-DAL-009: 正常系 - カウント
    def test_count(self, app_dal, valid_app_data):
        """カウント"""
        app_dal.insert(valid_app_data)
        
        count = app_dal.count({})
        
        assert count == 1
    
    # TC-APP-DAL-010: 正常系 - 存在確認
    def test_exists(self, app_dal, valid_app_data):
        """存在確認"""
        app_dal.insert(valid_app_data)
        
        assert app_dal.exists({"id": "test-app"}) is True
        assert app_dal.exists({"id": "nonexistent"}) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
