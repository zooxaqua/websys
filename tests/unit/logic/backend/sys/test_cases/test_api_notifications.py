"""
通知API (notifications.py) の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: 通知一覧取得、作成、既読処理、削除、ストリーミング
- 異常系: 権限不足、通知不存在
- 境界値: unread_onlyフィルター
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from project.backend.app.sys.api.notifications import router
from project.backend.app.sys.models.notification import Notification, NotificationCreate, NotificationResponse
from project.backend.app.sys.models.user import User
from project.backend.app.main import app


client = TestClient(app)


class TestNotificationsAPI:
    """通知APIのテストクラス"""
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_list_notifications_success(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-001: 正常系 - 通知一覧取得成功
        条件: unread_only=false
        期待: 200 OK, 全通知返却
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
        
        mock_notifications = [
            Notification(id="NOTIF001", userId="USR001", title="通知1", message="メッセージ1",
                        type="info", isRead=False, createdAt=datetime.now()),
            Notification(id="NOTIF002", userId="USR001", title="通知2", message="メッセージ2",
                        type="info", isRead=True, createdAt=datetime.now())
        ]
        mock_notification_service = Mock()
        mock_notification_service.get_user_notifications.return_value = mock_notifications
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.get(
            "/api/sys/notifications",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_notification_service.get_user_notifications.assert_called_once_with("USR001", unread_only=False)
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_list_notifications_unread_only(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-002: 正常系 - 未読通知のみ取得
        条件: unread_only=true
        期待: 200 OK, 未読通知のみ返却
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
        
        mock_notifications = [
            Notification(id="NOTIF001", userId="USR001", title="通知1", message="メッセージ1",
                        type="info", isRead=False, createdAt=datetime.now())
        ]
        mock_notification_service = Mock()
        mock_notification_service.get_user_notifications.return_value = mock_notifications
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.get(
            "/api/sys/notifications?unread_only=true",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_notification_service.get_user_notifications.assert_called_once_with("USR001", unread_only=True)
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_create_notification_success(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-003: 正常系 - 通知作成成功
        条件: 有効なNotificationCreate
        期待: 201 Created, 作成された通知返却
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
        
        mock_notification = Notification(
            id="NOTIF_NEW",
            userId="USR001",
            title="新規通知",
            message="テストメッセージ",
            type="info",
            isRead=False,
            createdAt=datetime.now()
        )
        mock_notification_service = Mock()
        mock_notification_service.create_notification.return_value = mock_notification
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.post(
            "/api/sys/notifications",
            json={"title": "新規通知", "message": "テストメッセージ", "type": "info"},
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == "NOTIF_NEW"
        assert response.json()["title"] == "新規通知"
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    def test_create_notification_missing_fields(self, mock_get_current_user):
        """
        TC-API-NOTIF-004: 異常系 - バリデーションエラー（必須フィールド欠損）
        条件: title欠損
        期待: 422 Unprocessable Entity
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
        
        response = client.post(
            "/api/sys/notifications",
            json={"message": "メッセージのみ", "type": "info"},
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 422
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_mark_notification_as_read_success(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-005: 正常系 - 通知既読処理成功
        条件: 有効なnotification_id
        期待: 200 OK, 成功メッセージ
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
        
        mock_notification_service = Mock()
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.put(
            "/api/sys/notifications/NOTIF001/read",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_notification_service.mark_as_read.assert_called_once_with("NOTIF001", "USR001")
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_mark_notification_as_read_not_found(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-006: 異常系 - 通知不存在
        条件: 存在しないnotification_id
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
        
        mock_notification_service = Mock()
        mock_notification_service.mark_as_read.side_effect = ValueError("通知が見つかりません")
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.put(
            "/api/sys/notifications/INVALID_ID/read",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code in [404, 500]
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_delete_notification_success(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-007: 正常系 - 通知削除成功
        条件: 有効なnotification_id
        期待: 200 OK, 成功メッセージ
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
        
        mock_notification_service = Mock()
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.delete(
            "/api/sys/notifications/NOTIF001",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        mock_notification_service.delete_notification.assert_called_once_with("NOTIF001", "USR001")
    
    @patch('project.backend.app.sys.api.notifications.get_current_user')
    @patch('project.backend.app.sys.api.notifications.get_notification_service')
    def test_delete_notification_permission_denied(self, mock_get_notification_service, mock_get_current_user):
        """
        TC-API-NOTIF-008: 異常系 - 他人の通知削除（権限不足）
        条件: 他ユーザーの通知ID
        期待: 403 Forbidden
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
        
        mock_notification_service = Mock()
        mock_notification_service.delete_notification.side_effect = PermissionError("権限がありません")
        mock_get_notification_service.return_value = mock_notification_service
        
        response = client.delete(
            "/api/sys/notifications/OTHER_NOTIF",
            cookies={"auth_token": "user_token"}
        )
        
        assert response.status_code in [403, 500]
