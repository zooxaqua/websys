"""
単体テスト: Config API

テスト対象: project/backend/app/sys/api/config.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from fastapi.testclient import TestClient
import json

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.api.config import router, load_config
from app.sys.models.user import User
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/sys")


class TestConfigAPI:
    """Config API のテストクラス"""
    
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
    
    # TC-CONFIG-001: 正常系 - デフォルト設定読み込み
    @patch('app.sys.api.config.CONFIG_FILE')
    def test_load_config_default(self, mock_config_file):
        """デフォルト設定読み込み"""
        mock_config_file.exists.return_value = False
        
        config = load_config()
        
        assert config["siteName"] == "WebSystem"
        assert config["sessionTimeout"] == 24
    
    # TC-CONFIG-002: 正常系 - 設定ファイル読み込み
    @patch('app.sys.api.config.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open, read_data='{"siteName":"Custom"}')
    def test_load_config_from_file(self, mock_file, mock_config_file):
        """設定ファイルから読み込み"""
        mock_config_file.exists.return_value = True
        
        config = load_config()
        
        assert config["siteName"] == "Custom"
    
    # TC-CONFIG-003: 境界値 - 空の設定
    @patch('app.sys.api.config.CONFIG_FILE')
    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_load_config_empty(self, mock_file, mock_config_file):
        """空の設定"""
        mock_config_file.exists.return_value = True
        
        config = load_config()
        
        assert isinstance(config, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
