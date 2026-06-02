"""
単体テスト: Notifications API

テスト対象: project/backend/app/sys/api/notifications.py
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

from app.sys.api.notifications import router
from app.sys.models.notification import Notification
from app.sys.models.user import User
from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api/sys")


class TestNotificationsAPI:
    """Notifications API のテストクラス"""
    
    @pytest.fixture
    def client(self):
        """TestClient インスタンス"""
        return TestClient(app)
    
    @pytest.fixture
    def regular_user(self):
        """通常ユーザー"""
        return User(
            id="user-001",
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
    
    @pytest.fixture
    def valid_notification(self):
        """有効な通知"""
        return Notification(
            id="notif-001",
            userId="user-001",
            type="info",
            title="Test Notification",
            message="This is a test",
            metadata={},
            read=False,
            createdAt="2026-01-01T00:00:00Z",
            expiresAt=None
        )
    
    # TC-NOTIF-API-001: 正常系 - 通知一覧取得
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_list_notifications_success(self, mock_get_service, mock_get_user, client, regular_user, valid_notification):
        """通知一覧取得成功"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.get_user_notifications.return_value = [valid_notification]
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/notifications")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "notif-001"
    
    # TC-NOTIF-API-002: 正常系 - 未読通知のみ取得
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_list_notifications_unread_only(self, mock_get_service, mock_get_user, client, regular_user, valid_notification):
        """未読通知のみ取得"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.get_user_notifications.return_value = [valid_notification]
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/sys/notifications?unread_only=true")
        
        assert response.status_code == 200
        mock_service.get_user_notifications.assert_called_once_with("user-001", unread_only=True)
    
    # TC-NOTIF-API-003: 正常系 - 通知作成
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_create_notification_success(self, mock_get_service, mock_get_user, client, regular_user, valid_notification):
        """通知作成成功"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.create_notification.return_value = valid_notification
        mock_get_service.return_value = mock_service
        
        response = client.post("/api/sys/notifications", json={
            "type": "info",
            "title": "Test",
            "message": "Test message",
            "metadata": {}
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Notification"
    
    # TC-NOTIF-API-004: 正常系 - 通知を既読にする
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_mark_as_read_success(self, mock_get_service, mock_get_user, client, regular_user):
        """通知を既読にする成功"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.mark_as_read.return_value = True
        mock_get_service.return_value = mock_service
        
        response = client.put("/api/sys/notifications/notif-001/read")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    # TC-NOTIF-API-005: 異常系 - 既読にする通知が存在しない
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_mark_as_read_not_found(self, mock_get_service, mock_get_user, client, regular_user):
        """既読にする通知が存在しない"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.mark_as_read.side_effect = HTTPException(status_code=404, detail="Not found")
        mock_get_service.return_value = mock_service
        
        response = client.put("/api/sys/notifications/nonexistent/read")
        
        assert response.status_code == 404
    
    # TC-NOTIF-API-006: 正常系 - 通知削除
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_delete_notification_success(self, mock_get_service, mock_get_user, client, regular_user):
        """通知削除成功"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.delete_notification.return_value = True
        mock_get_service.return_value = mock_service
        
        response = client.delete("/api/sys/notifications/notif-001")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    # TC-NOTIF-API-007: 異常系 - 削除する通知が存在しない
    @patch('app.sys.api.notifications.get_current_user')
    @patch('app.sys.api.notifications.get_notification_service')
    def test_delete_notification_not_found(self, mock_get_service, mock_get_user, client, regular_user):
        """削除する通知が存在しない"""
        mock_get_user.return_value = regular_user
        mock_service = Mock()
        mock_service.delete_notification.side_effect = HTTPException(status_code=404, detail="Not found")
        mock_get_service.return_value = mock_service
        
        response = client.delete("/api/sys/notifications/nonexistent")
        
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
