"""
単体テスト: NotificationService

テスト対象: project/backend/app/sys/services/notification_service.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.services.notification_service import NotificationService
from app.sys.models.notification import NotificationCreate
from fastapi import HTTPException


class TestNotificationService:
    """NotificationService のテストクラス"""
    
    @pytest.fixture
    def notif_dal_mock(self):
        """NotificationDAL のモック"""
        return Mock()
    
    @pytest.fixture
    def notif_service(self, notif_dal_mock):
        """NotificationService インスタンス"""
        return NotificationService(notif_dal_mock)
    
    @pytest.fixture
    def valid_notif_data(self):
        """有効な通知データ"""
        return {
            "id": "notif-001",
            "userId": "user-001",
            "type": "info",
            "title": "Test Notification",
            "message": "This is a test",
            "metadata": {},
            "read": False,
            "createdAt": "2026-01-01T00:00:00Z",
            "expiresAt": None
        }
    
    # TC-NOTIF-SVC-001: 正常系 - 通知作成成功
    def test_create_notification_success(self, notif_service, notif_dal_mock):
        """通知作成成功"""
        notif_dal_mock.insert.return_value = True
        
        notif_create = NotificationCreate(
            type="info",
            title="Test",
            message="Test message",
            metadata={}
        )
        
        notif = notif_service.create_notification("user-001", notif_create)
        
        assert notif.userId == "user-001"
        assert notif.title == "Test"
        notif_dal_mock.insert.assert_called_once()
    
    # TC-NOTIF-SVC-002: 正常系 - ユーザー通知取得（全件）
    def test_get_user_notifications_all(self, notif_service, notif_dal_mock, valid_notif_data):
        """ユーザー通知取得（全件）"""
        notif_dal_mock.find_by_user.return_value = [valid_notif_data]
        
        notifs = notif_service.get_user_notifications("user-001")
        
        assert len(notifs) == 1
        assert notifs[0].userId == "user-001"
        notif_dal_mock.find_by_user.assert_called_once_with("user-001", unread_only=False)
    
    # TC-NOTIF-SVC-003: 正常系 - 未読通知のみ取得
    def test_get_user_notifications_unread_only(self, notif_service, notif_dal_mock, valid_notif_data):
        """未読通知のみ取得"""
        notif_dal_mock.find_by_user.return_value = [valid_notif_data]
        
        notifs = notif_service.get_user_notifications("user-001", unread_only=True)
        
        notif_dal_mock.find_by_user.assert_called_once_with("user-001", unread_only=True)
    
    # TC-NOTIF-SVC-004: 正常系 - 通知を既読にする
    def test_mark_as_read_success(self, notif_service, notif_dal_mock, valid_notif_data):
        """通知を既読にする成功"""
        notif_dal_mock.find_one.return_value = valid_notif_data
        notif_dal_mock.mark_read.return_value = True
        
        result = notif_service.mark_as_read("notif-001", "user-001")
        
        assert result is True
        notif_dal_mock.mark_read.assert_called_once_with("notif-001")
    
    # TC-NOTIF-SVC-005: 異常系 - 通知が存在しない
    def test_mark_as_read_not_found(self, notif_service, notif_dal_mock):
        """通知が存在しない"""
        notif_dal_mock.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            notif_service.mark_as_read("nonexistent", "user-001")
        
        assert exc.value.status_code == 404
        assert "ERR-SYS-NOTF-001" in str(exc.value.detail)
    
    # TC-NOTIF-SVC-006: 異常系 - 権限エラー（他人の通知）
    def test_mark_as_read_forbidden(self, notif_service, notif_dal_mock, valid_notif_data):
        """権限エラー（他人の通知）"""
        notif_dal_mock.find_one.return_value = valid_notif_data
        
        with pytest.raises(HTTPException) as exc:
            notif_service.mark_as_read("notif-001", "other-user")
        
        assert exc.value.status_code == 403
        assert "ERR-SYS-NOTF-002" in str(exc.value.detail)
    
    # TC-NOTIF-SVC-007: 正常系 - 通知削除成功
    def test_delete_notification_success(self, notif_service, notif_dal_mock, valid_notif_data):
        """通知削除成功"""
        notif_dal_mock.find_one.return_value = valid_notif_data
        notif_dal_mock.delete.return_value = True
        
        result = notif_service.delete_notification("notif-001", "user-001")
        
        assert result is True
        notif_dal_mock.delete.assert_called_once_with("notif-001")
    
    # TC-NOTIF-SVC-008: 異常系 - 削除時に通知が存在しない
    def test_delete_notification_not_found(self, notif_service, notif_dal_mock):
        """削除時に通知が存在しない"""
        notif_dal_mock.find_one.return_value = None
        
        with pytest.raises(HTTPException) as exc:
            notif_service.delete_notification("nonexistent", "user-001")
        
        assert exc.value.status_code == 404
    
    # TC-NOTIF-SVC-009: 異常系 - 削除時に権限エラー
    def test_delete_notification_forbidden(self, notif_service, notif_dal_mock, valid_notif_data):
        """削除時に権限エラー"""
        notif_dal_mock.find_one.return_value = valid_notif_data
        
        with pytest.raises(HTTPException) as exc:
            notif_service.delete_notification("notif-001", "other-user")
        
        assert exc.value.status_code == 403
        assert "ERR-SYS-NOTF-002" in str(exc.value.detail)
    
    # TC-NOTIF-SVC-010: 境界値 - 空の通知一覧
    def test_get_user_notifications_empty(self, notif_service, notif_dal_mock):
        """空の通知一覧"""
        notif_dal_mock.find_by_user.return_value = []
        
        notifs = notif_service.get_user_notifications("user-001")
        
        assert len(notifs) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
