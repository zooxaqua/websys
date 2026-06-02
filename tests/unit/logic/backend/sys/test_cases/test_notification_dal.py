"""
単体テスト: NotificationDAL

テスト対象: project/backend/app/sys/dal/notification_dal.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.dal.notification_dal import NotificationDAL


class TestNotificationDAL:
    """NotificationDAL のテストクラス"""
    
    @pytest.fixture
    def notif_dal(self, tmp_path):
        """NotificationDAL インスタンス"""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        return NotificationDAL(str(data_dir))
    
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
            "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "expiresAt": None
        }
    
    # TC-NOTIF-DAL-001: 正常系 - 通知挿入
    def test_insert_success(self, notif_dal, valid_notif_data):
        """通知挿入成功"""
        notif_id = notif_dal.insert(valid_notif_data)
        
        assert notif_id == "notif-001"
        found = notif_dal.find_one({"id": "notif-001"})
        assert found is not None
        assert found["title"] == "Test Notification"
    
    # TC-NOTIF-DAL-002: 正常系 - ユーザーの通知取得（全件）
    def test_find_by_user_all(self, notif_dal, valid_notif_data):
        """ユーザーの通知取得（全件）"""
        notif_dal.insert(valid_notif_data)
        
        notifs = notif_dal.find_by_user("user-001")
        
        assert len(notifs) == 1
        assert notifs[0]["userId"] == "user-001"
    
    # TC-NOTIF-DAL-003: 正常系 - 未読通知のみ取得
    def test_find_by_user_unread_only(self, notif_dal, valid_notif_data):
        """未読通知のみ取得"""
        notif_dal.insert(valid_notif_data)
        read_notif = valid_notif_data.copy()
        read_notif["id"] = "notif-002"
        read_notif["read"] = True
        notif_dal.insert(read_notif)
        
        unread = notif_dal.find_by_user("user-001", unread_only=True)
        
        assert len(unread) == 1
        assert unread[0]["id"] == "notif-001"
        assert unread[0]["read"] is False
    
    # TC-NOTIF-DAL-004: 正常系 - 通知を既読にする
    def test_mark_read_success(self, notif_dal, valid_notif_data):
        """通知を既読にする成功"""
        notif_dal.insert(valid_notif_data)
        
        result = notif_dal.mark_read("notif-001")
        
        assert result is True
        updated = notif_dal.find_one({"id": "notif-001"})
        assert updated["read"] is True
    
    # TC-NOTIF-DAL-005: 正常系 - 通知削除
    def test_delete_success(self, notif_dal, valid_notif_data):
        """通知削除成功"""
        notif_dal.insert(valid_notif_data)
        
        result = notif_dal.delete("notif-001")
        
        assert result is True
        assert notif_dal.find_one({"id": "notif-001"}) is None
    
    # TC-NOTIF-DAL-006: 正常系 - 期限切れ通知削除
    def test_delete_expired(self, notif_dal, valid_notif_data):
        """期限切れ通知削除"""
        # 期限切れ通知
        expired_notif = valid_notif_data.copy()
        expired_notif["id"] = "expired-notif"
        expired_notif["expiresAt"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        notif_dal.insert(expired_notif)
        
        # 有効な通知
        valid_notif_data["expiresAt"] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
        notif_dal.insert(valid_notif_data)
        
        deleted_count = notif_dal.delete_expired()
        
        assert deleted_count == 1
        assert notif_dal.find_one({"id": "expired-notif"}) is None
        assert notif_dal.find_one({"id": "notif-001"}) is not None
    
    # TC-NOTIF-DAL-007: 境界値 - 空の通知一覧
    def test_find_by_user_empty(self, notif_dal):
        """空の通知一覧"""
        notifs = notif_dal.find_by_user("user-001")
        
        assert len(notifs) == 0
    
    # TC-NOTIF-DAL-008: 正常系 - 複数ユーザーの通知フィルタ
    def test_find_by_user_multiple_users(self, notif_dal, valid_notif_data):
        """複数ユーザーの通知フィルタ"""
        notif_dal.insert(valid_notif_data)
        
        # 別ユーザーの通知
        other_notif = valid_notif_data.copy()
        other_notif["id"] = "notif-002"
        other_notif["userId"] = "user-002"
        notif_dal.insert(other_notif)
        
        user1_notifs = notif_dal.find_by_user("user-001")
        user2_notifs = notif_dal.find_by_user("user-002")
        
        assert len(user1_notifs) == 1
        assert len(user2_notifs) == 1
        assert user1_notifs[0]["userId"] == "user-001"
        assert user2_notifs[0]["userId"] == "user-002"
    
    # TC-NOTIF-DAL-009: 正常系 - カウント
    def test_count(self, notif_dal, valid_notif_data):
        """カウント"""
        notif_dal.insert(valid_notif_data)
        
        count = notif_dal.count({"userId": "user-001"})
        
        assert count == 1
    
    # TC-NOTIF-DAL-010: 正常系 - 存在確認
    def test_exists(self, notif_dal, valid_notif_data):
        """存在確認"""
        notif_dal.insert(valid_notif_data)
        
        assert notif_dal.exists({"id": "notif-001"}) is True
        assert notif_dal.exists({"id": "nonexistent"}) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
