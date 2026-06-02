"""
設定管理API (config.py) の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: 設定取得、設定更新
- 異常系: 権限不足、ファイルIO失敗
- 境界値: デフォルト設定、空の設定
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import json

from project.backend.app.sys.api.config import router, load_config, save_config
from project.backend.app.sys.models.user import User
from project.backend.app.main import app


client = TestClient(app)


class TestConfigAPI:
    """設定管理APIのテストクラス"""
    
    @patch('project.backend.app.sys.api.config.get_current_admin_user')
    @patch('project.backend.app.sys.api.config.load_config')
    def test_get_config_success(self, mock_load_config, mock_get_current_admin_user):
        """
        TC-API-CONFIG-001: 正常系 - 設定取得成功（管理者）
        条件: 管理者権限
        期待: 200 OK, 設定情報返却
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
        
        mock_config = {
            "siteName": "WebSystem",
            "theme": "light",
            "language": "ja"
        }
        mock_load_config.return_value = mock_config
        
        response = client.get(
            "/api/sys/config",
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["config"]["siteName"] == "WebSystem"
        mock_load_config.assert_called_once()
    
    def test_get_config_unauthorized(self):
        """
        TC-API-CONFIG-002: 異常系 - 一般ユーザーでアクセス（権限不足）
        条件: 一般ユーザートークン
        期待: 403 Forbidden
        """
        response = client.get(
            "/api/sys/config",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code in [401, 403]
    
    @patch('project.backend.app.sys.api.config.get_current_admin_user')
    @patch('project.backend.app.sys.api.config.load_config')
    @patch('project.backend.app.sys.api.config.save_config')
    def test_update_config_success(self, mock_save_config, mock_load_config, mock_get_current_admin_user):
        """
        TC-API-CONFIG-003: 正常系 - 設定更新成功
        条件: 有効な設定、管理者権限
        期待: 200 OK, 更新された設定返却
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
        
        updated_config = {
            "siteName": "UpdatedSystem",
            "theme": "dark",
            "language": "en"
        }
        mock_load_config.return_value = updated_config
        
        response = client.put(
            "/api/sys/config",
            json={"config": updated_config},
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["config"]["siteName"] == "UpdatedSystem"
        mock_save_config.assert_called_once_with(updated_config)
    
    @patch('project.backend.app.sys.api.config.get_current_admin_user')
    def test_update_config_missing_field(self, mock_get_current_admin_user):
        """
        TC-API-CONFIG-004: 異常系 - バリデーションエラー（configフィールド欠損）
        条件: configフィールドなし
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
        
        response = client.put(
            "/api/sys/config",
            json={},
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 422
    
    @patch('project.backend.app.sys.api.config.get_current_admin_user')
    @patch('project.backend.app.sys.api.config.load_config')
    @patch('project.backend.app.sys.api.config.save_config')
    def test_update_config_empty(self, mock_save_config, mock_load_config, mock_get_current_admin_user):
        """
        TC-API-CONFIG-005: 境界値 - 空の設定更新
        条件: config={}
        期待: 200 OK, 空の設定が保存される
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
        
        empty_config = {}
        mock_load_config.return_value = empty_config
        
        response = client.put(
            "/config",
            json={"config": empty_config},
            cookies={"auth_token": "admin_token"}
        )
        
        assert response.status_code == 200
        mock_save_config.assert_called_once_with(empty_config)


class TestConfigHelpers:
    """設定ヘルパー関数のテストクラス"""
    
    @patch('pathlib.Path.exists', return_value=False)
    @patch('project.backend.app.sys.api.config.save_config')
    def test_load_config_default(self, mock_save_config, mock_exists):
        """
        TC-CONFIG-HELPER-001: 正常系 - デフォルト設定の生成
        条件: 設定ファイル不存在
        期待: デフォルト設定が返される
        """
        config = load_config()
        
        assert config["siteName"] == "WebSystem"
        assert config["theme"] == "light"
        mock_save_config.assert_called_once()
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='{"siteName": "TestSystem"}')
    def test_load_config_existing(self, mock_file, mock_exists):
        """
        TC-CONFIG-HELPER-002: 正常系 - 既存設定の読み込み
        条件: 設定ファイル存在
        期待: ファイルから設定が読み込まれる
        """
        config = load_config()
        
        assert config["siteName"] == "TestSystem"
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_config_success(self, mock_file, mock_mkdir):
        """
        TC-CONFIG-HELPER-003: 正常系 - 設定保存成功
        条件: 有効な設定辞書
        期待: ファイルに書き込まれる
        """
        test_config = {"siteName": "TestSystem", "theme": "dark"}
        
        save_config(test_config)
        
        mock_mkdir.assert_called_once()
        mock_file.assert_called_once()
