"""
Notification モデルの単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: 有効なデータでインスタンス生成
- 異常系: バリデーションエラー（type, title, message制約）
- 境界値: title/messageの長さ上限・下限
- 機能: is_expired(), to_dict(), from_dict()
"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import ValidationError
from unittest.mock import patch

# テスト対象
from project.backend.app.sys.models.notification import Notification, NotificationCreate, NotificationResponse


def load_fixture(name: str) -> dict:
    """フィクスチャデータを読み込む"""
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "inputs" / "fixtures" / "notification_fixtures.json"
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    return fixtures[name]


class TestNotificationModel:
    """Notification モデルのテストクラス"""
    
    def test_notification_creation_info(self):
        """
        TC-NOTIF-001: 正常系 - info通知作成
        条件: type=info, 有効なデータ
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('valid_info_notification')
        notif = Notification(**data)
        
        assert notif.type == 'info'
        assert notif.title == data['title']
        assert notif.read is False
    
    def test_notification_creation_warning(self):
        """
        TC-NOTIF-002: 正常系 - warning通知作成
        条件: type=warning
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('valid_warning_notification')
        notif = Notification(**data)
        
        assert notif.type == 'warning'
        assert notif.metadata['priority'] == 'high'
    
    def test_notification_creation_error(self):
        """
        TC-NOTIF-003: 正常系 - error通知作成
        条件: type=error, read=True
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('valid_error_notification')
        notif = Notification(**data)
        
        assert notif.type == 'error'
        assert notif.read is True
    
    def test_notification_creation_success(self):
        """
        TC-NOTIF-004: 正常系 - success通知作成
        条件: type=success, expiresAtあり
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('valid_success_notification')
        notif = Notification(**data)
        
        assert notif.type == 'success'
        assert notif.expiresAt is not None
    
    def test_notification_boundary_title_min(self):
        """
        TC-NOTIF-005: 境界値 - title最小長（1文字）
        条件: title=1文字
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('boundary_title_min')
        notif = Notification(**data)
        
        assert len(notif.title) == 1
    
    def test_notification_boundary_title_max(self):
        """
        TC-NOTIF-006: 境界値 - title最大長（200文字）
        条件: title=200文字
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('boundary_title_max')
        notif = Notification(**data)
        
        assert len(notif.title) == 200
    
    def test_notification_boundary_message_min(self):
        """
        TC-NOTIF-007: 境界値 - message最小長（1文字）
        条件: message=1文字
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('boundary_message_min')
        notif = Notification(**data)
        
        assert len(notif.message) == 1
    
    def test_notification_invalid_type(self):
        """
        TC-NOTIF-008: 異常系 - 無効なtype
        条件: type='invalid'
        期待: ValidationError
        """
        data = load_fixture('valid_info_notification')
        data['type'] = 'invalid'
        
        with pytest.raises(ValidationError) as exc_info:
            Notification(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('type',) for e in errors)
    
    def test_notification_invalid_title_empty(self):
        """
        TC-NOTIF-009: 異常系 - title空文字
        条件: title=''
        期待: ValidationError
        """
        data = load_fixture('valid_info_notification')
        data['title'] = ''
        
        with pytest.raises(ValidationError) as exc_info:
            Notification(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('title',) for e in errors)
    
    def test_notification_invalid_title_too_long(self):
        """
        TC-NOTIF-010: 異常系 - title長すぎる（201文字）
        条件: title=201文字
        期待: ValidationError
        """
        data = load_fixture('valid_info_notification')
        data['title'] = 'A' * 201
        
        with pytest.raises(ValidationError) as exc_info:
            Notification(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('title',) for e in errors)
    
    def test_notification_invalid_message_empty(self):
        """
        TC-NOTIF-011: 異常系 - message空文字
        条件: message=''
        期待: ValidationError
        """
        data = load_fixture('valid_info_notification')
        data['message'] = ''
        
        with pytest.raises(ValidationError) as exc_info:
            Notification(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('message',) for e in errors)
    
    def test_notification_invalid_message_too_long(self):
        """
        TC-NOTIF-012: 異常系 - message長すぎる（1001文字）
        条件: message=1001文字
        期待: ValidationError
        """
        data = load_fixture('valid_info_notification')
        data['message'] = 'A' * 1001
        
        with pytest.raises(ValidationError) as exc_info:
            Notification(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('message',) for e in errors)
    
    @patch('project.backend.app.sys.models.notification.datetime')
    def test_notification_is_expired_true(self, mock_datetime):
        """
        TC-NOTIF-013: is_expired() - 期限切れ
        条件: 現在時刻 > expiresAt
        期待: True
        """
        mock_datetime.utcnow.return_value = datetime(2026, 5, 29, 12, 0, 0)
        
        data = load_fixture('expired_notification')
        notif = Notification(**data)
        
        assert notif.is_expired() is True
    
    @patch('project.backend.app.sys.models.notification.datetime')
    def test_notification_is_expired_false_not_expired(self, mock_datetime):
        """
        TC-NOTIF-014: is_expired() - 有効期限内
        条件: 現在時刻 < expiresAt
        期待: False
        """
        mock_datetime.utcnow.return_value = datetime(2026, 5, 29, 12, 0, 0)
        
        data = load_fixture('valid_warning_notification')
        notif = Notification(**data)
        
        assert notif.is_expired() is False
    
    @patch('project.backend.app.sys.models.notification.datetime')
    def test_notification_is_expired_false_no_expiry(self, mock_datetime):
        """
        TC-NOTIF-015: is_expired() - 有効期限なし
        条件: expiresAt=None
        期待: False
        """
        mock_datetime.utcnow.return_value = datetime(2026, 5, 29, 12, 0, 0)
        
        data = load_fixture('valid_info_notification')
        notif = Notification(**data)
        
        assert notif.is_expired() is False
    
    def test_notification_to_dict(self):
        """
        TC-NOTIF-016: to_dict() - 辞書変換
        条件: 正常なNotificationインスタンス
        期待: 辞書形式に変換される
        """
        data = load_fixture('valid_info_notification')
        notif = Notification(**data)
        
        result = notif.to_dict()
        
        assert isinstance(result, dict)
        assert result['id'] == data['id']
        assert result['type'] == data['type']
    
    def test_notification_from_dict(self):
        """
        TC-NOTIF-017: from_dict() - 辞書からインスタンス生成
        条件: 正常な辞書データ
        期待: Notificationインスタンスが生成される
        """
        data = load_fixture('valid_info_notification')
        notif = Notification.from_dict(data)
        
        assert isinstance(notif, Notification)
        assert notif.id == data['id']
    
    def test_notification_serialization_roundtrip(self):
        """
        TC-NOTIF-018: シリアライズ・デシリアライズのラウンドトリップ
        条件: Notification → dict → Notification
        期待: データが保持される
        """
        data = load_fixture('valid_info_notification')
        notif1 = Notification(**data)
        
        dict_data = notif1.to_dict()
        notif2 = Notification.from_dict(dict_data)
        
        assert notif1.id == notif2.id
        assert notif1.type == notif2.type
        assert notif1.title == notif2.title


class TestNotificationCreateModel:
    """NotificationCreate モデルのテストクラス"""
    
    def test_notification_create_valid(self):
        """
        TC-NOTIF-CREATE-001: 正常系 - NotificationCreate作成
        条件: 必須フィールドあり
        期待: NotificationCreateインスタンスが生成される
        """
        data = {
            'type': 'info',
            'title': 'Test notification',
            'message': 'Test message',
            'metadata': {},
            'expiresAt': None
        }
        
        notif_create = NotificationCreate(**data)
        
        assert notif_create.type == 'info'
        assert notif_create.title == 'Test notification'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
