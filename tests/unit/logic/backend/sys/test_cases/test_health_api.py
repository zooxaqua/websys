"""
単体テスト: Health API

テスト対象: project/backend/app/sys/api/health.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.api.health import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/sys")


class TestHealthAPI:
    """Health API のテストクラス"""
    
    @pytest.fixture
    def client(self):
        """TestClient インスタンス"""
        return TestClient(app)
    
    # TC-HEALTH-001: 正常系 - ヘルスチェック成功
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_health_check_success(self, mock_is_dir, mock_exists, client):
        """ヘルスチェック成功"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
        assert "version" in data
        assert data["data_dir_accessible"] is True
    
    # TC-HEALTH-002: 異常系 - データディレクトリアクセス不可
    @patch('pathlib.Path.exists')
    def test_health_check_data_dir_not_accessible(self, mock_exists, client):
        """データディレクトリアクセス不可"""
        mock_exists.return_value = False
        
        response = client.get("/api/sys/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert data["data_dir_accessible"] is False
    
    # TC-HEALTH-003: 境界値 - レスポンス形式確認
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_health_check_response_format(self, mock_is_dir, mock_exists, client):
        """レスポンス形式確認"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        response = client.get("/health")
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "python_version" in data
        assert "data_dir_accessible" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
