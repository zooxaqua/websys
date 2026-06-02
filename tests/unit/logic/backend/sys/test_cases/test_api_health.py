"""
ヘルスチェックAPI (health.py) の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: ヘルスチェック成功、Ping応答
- 異常系: データディレクトリアクセス失敗
- 境界値: ステータスコード、レスポンス形式
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from project.backend.app.sys.api.health import router
from project.backend.app.main import app


client = TestClient(app)


class TestHealthAPI:
    """ヘルスチェックAPIのテストクラス"""
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_health_check_success(self, mock_is_dir, mock_exists):
        """
        TC-API-HEALTH-001: 正常系 - ヘルスチェック成功
        条件: データディレクトリが存在しアクセス可能
        期待: 200 OK, status="ok", データディレクトリアクセス可
        """
        response = client.get("/api/sys/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["data_dir_accessible"] is True
        assert "version" in response.json()
        assert "python_version" in response.json()
        assert "timestamp" in response.json()
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_health_check_data_dir_not_exists(self, mock_exists):
        """
        TC-API-HEALTH-002: 異常系 - データディレクトリ不存在
        条件: データディレクトリが存在しない
        期待: 200 OK, status="error", データディレクトリアクセス不可
        """
        response = client.get("/api/sys/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "error"
        assert response.json()["data_dir_accessible"] is False
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=False)
    def test_health_check_data_dir_not_directory(self, mock_is_dir, mock_exists):
        """
        TC-API-HEALTH-003: 異常系 - データディレクトリがファイル
        条件: データディレクトリパスがディレクトリでない
        期待: 200 OK, status="error", データディレクトリアクセス不可
        """
        response = client.get("/api/sys/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "error"
        assert response.json()["data_dir_accessible"] is False
    
    def test_ping_success(self):
        """
        TC-API-HEALTH-004: 正常系 - Ping応答成功
        条件: 認証不要のエンドポイント
        期待: 200 OK, message="pong"
        """
        response = client.get("/api/sys/health/ping")
        
        assert response.status_code == 200
        assert response.json()["message"] == "pong"
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_health_check_version_format(self, mock_is_dir, mock_exists):
        """
        TC-API-HEALTH-005: 境界値 - バージョン形式確認
        条件: 正常なヘルスチェック
        期待: versionが"x.x.x"形式、python_versionが"x.x.x"形式
        """
        response = client.get("/api/sys/health")
        
        assert response.status_code == 200
        version = response.json()["version"]
        python_version = response.json()["python_version"]
        
        # バージョン形式確認（x.x.x）
        assert len(version.split(".")) == 3
        assert len(python_version.split(".")) == 3
    
    @patch('pathlib.Path.exists', return_value=True)
    @patch('pathlib.Path.is_dir', return_value=True)
    def test_health_check_timestamp_format(self, mock_is_dir, mock_exists):
        """
        TC-API-HEALTH-006: 境界値 - タイムスタンプ形式確認
        条件: 正常なヘルスチェック
        期待: timestampがISO8601形式（Z末尾）
        """
        response = client.get("/api/sys/health")
        
        assert response.status_code == 200
        timestamp = response.json()["timestamp"]
        
        # ISO8601形式確認（Z末尾）
        assert timestamp.endswith("Z")
        # 日時パース可能か確認
        from datetime import datetime
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
