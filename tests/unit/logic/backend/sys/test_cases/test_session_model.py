"""
Session モデルの単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: 有効なセッション、is_valid()の動作
- 異常系: 期限切れセッション、必須項目欠損
- 境界値: expiresAtの境界
"""
import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from pydantic import ValidationError
from unittest.mock import patch

# テスト対象
from project.backend.app.sys.models.session import Session


def load_fixture(name: str) -> dict:
    """フィクスチャデータを読み込む"""
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "inputs" / "fixtures" / "session_fixtures.json"
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    return fixtures[name]


class TestSessionModel:
    """Session モデルのテストクラス"""
    
    def test_session_creation_valid(self):
        """
        TC-SESSION-001: 正常系 - 有効なセッション作成成功
        条件: 全フィールドが有効な値
        期待: Sessionインスタンスが正常に生成される
        """
        data = load_fixture('valid_session')
        session = Session(**data)
        
        assert session.sessionId == data['sessionId']
        assert session.userId == data['userId']
        assert session.token == data['token']
        assert session.metadata == data['metadata']
    
    def test_session_is_valid_future(self):
        """
        TC-SESSION-002: is_valid() - 有効期限内（未来）
        条件: expiresAt > 現在時刻
        期待: is_valid() が True を返す
        """
        data = load_fixture('session_boundary_future')
        session = Session(**data)
        
        # 未来の有効期限を持つため有効
        assert session.is_valid() is True
    
    def test_session_is_valid_expired(self):
        """
        TC-SESSION-003: is_valid() - 有効期限切れ（過去）
        条件: expiresAt < 現在時刻
        期待: is_valid() が False を返す
        """
        data = load_fixture('expired_session')
        session = Session(**data)
        
        # 過去の有効期限を持つため無効
        assert session.is_valid() is False
    
    @patch('project.backend.app.sys.models.session.datetime')
    def test_session_is_valid_boundary_exact_now(self, mock_datetime):
        """
        TC-SESSION-004: is_valid() - 境界値（expiresAt == 現在時刻）
        条件: expiresAt == datetime.utcnow()
        期待: is_valid() が False を返す（厳密な未満比較）
        """
        # 固定時刻を設定
        fixed_now = datetime(2026, 5, 29, 10, 0, 0)
        mock_datetime.utcnow.return_value = fixed_now
        
        session = Session(
            sessionId="sess_boundary",
            userId="user_test",
            token="token_boundary",
            createdAt=datetime(2026, 5, 29, 9, 0, 0),
            expiresAt=fixed_now  # ちょうど現在時刻
        )
        
        # utcnow() < expiresAt は False（等しいため）
        assert session.is_valid() is False
    
    @patch('project.backend.app.sys.models.session.datetime')
    def test_session_is_valid_boundary_one_second_before_expiry(self, mock_datetime):
        """
        TC-SESSION-005: is_valid() - 境界値（expiresAt - 1秒）
        条件: expiresAt が現在時刻より1秒後
        期待: is_valid() が True を返す
        """
        fixed_now = datetime(2026, 5, 29, 10, 0, 0)
        mock_datetime.utcnow.return_value = fixed_now
        
        session = Session(
            sessionId="sess_boundary_before",
            userId="user_test",
            token="token_boundary_before",
            createdAt=datetime(2026, 5, 29, 9, 0, 0),
            expiresAt=fixed_now + timedelta(seconds=1)  # 1秒後
        )
        
        assert session.is_valid() is True
    
    def test_session_to_dict(self):
        """
        TC-SESSION-006: to_dict() - 辞書形式変換
        条件: 有効なSessionインスタンス
        期待: 正しい辞書形式で出力される
        """
        data = load_fixture('valid_session')
        session = Session(**data)
        result = session.to_dict()
        
        assert isinstance(result, dict)
        assert result['sessionId'] == data['sessionId']
        assert result['userId'] == data['userId']
        assert result['token'] == data['token']
    
    def test_session_from_dict(self):
        """
        TC-SESSION-007: from_dict() - 辞書からインスタンス生成
        条件: 有効な辞書データ
        期待: Sessionインスタンスが正常に生成される
        """
        data = load_fixture('valid_session')
        session = Session.from_dict(data)
        
        assert isinstance(session, Session)
        assert session.sessionId == data['sessionId']
    
    def test_session_no_metadata(self):
        """
        TC-SESSION-008: metadata省略時のデフォルト値
        条件: metadataフィールドを省略
        期待: 空辞書 {} がデフォルト値として設定される
        """
        data = load_fixture('session_no_metadata')
        session = Session(**data)
        
        assert session.metadata == {}
    
    def test_session_missing_sessionId(self):
        """
        TC-SESSION-009: 異常系 - sessionId必須項目欠損
        条件: sessionIdフィールドが欠損
        期待: ValidationError が発生
        """
        data = load_fixture('valid_session')
        del data['sessionId']
        
        with pytest.raises(ValidationError) as exc_info:
            Session(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('sessionId',) and e['type'] == 'missing' for e in errors)
    
    def test_session_missing_userId(self):
        """
        TC-SESSION-010: 異常系 - userId必須項目欠損
        条件: userIdフィールドが欠損
        期待: ValidationError が発生
        """
        data = load_fixture('valid_session')
        del data['userId']
        
        with pytest.raises(ValidationError) as exc_info:
            Session(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('userId',) and e['type'] == 'missing' for e in errors)
    
    def test_session_invalid_createdAt_type(self):
        """
        TC-SESSION-011: 異常系 - createdAt型不正
        条件: createdAtが文字列（不正なフォーマット）
        期待: ValidationError が発生
        """
        data = load_fixture('valid_session')
        data['createdAt'] = 'invalid-date-format'
        
        with pytest.raises(ValidationError) as exc_info:
            Session(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('createdAt',) for e in errors)
    
    def test_session_invalid_expiresAt_type(self):
        """
        TC-SESSION-012: 異常系 - expiresAt型不正
        条件: expiresAtが不正な型（数値）
        期待: ValidationError が発生
        """
        data = load_fixture('valid_session')
        data['expiresAt'] = 12345
        
        with pytest.raises(ValidationError) as exc_info:
            Session(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('expiresAt',) for e in errors)
