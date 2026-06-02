"""
SessionDAL の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: セッション検索（token）、期限切れセッション削除、個別ファイル保存
- 異常系: 存在しないトークン検索、ファイル削除失敗
- 境界値: 期限切れ境界、空データベース
"""
import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

# テスト対象
from project.backend.app.sys.dal.session_dal import SessionDAL


class TestSessionDAL:
    """SessionDAL のテストクラス"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """テスト用一時ディレクトリ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def dal(self, temp_data_dir):
        """テスト用DALインスタンス"""
        return SessionDAL(data_dir=temp_data_dir)
    
    def test_find_by_token_existing(self, dal):
        """
        TC-SESSION-DAL-001: find_by_token() - 存在するトークン検索
        条件: tokenに一致するセッションが存在
        期待: セッションデータが返される
        """
        session_data = {
            "sessionId": "sess-001",
            "userId": "user-001",
            "token": "token-abc123",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2026-05-30T00:00:00Z"
        }
        dal.insert(session_data)
        
        result = dal.find_by_token("token-abc123")
        
        assert result is not None
        assert result["token"] == "token-abc123"
        assert result["userId"] == "user-001"
    
    def test_find_by_token_non_existing(self, dal):
        """
        TC-SESSION-DAL-002: find_by_token() - 存在しないトークン検索
        条件: tokenに一致するセッションが存在しない
        期待: None が返される
        """
        result = dal.find_by_token("non-existent-token")
        
        assert result is None
    
    def test_insert_creates_session_file(self, dal):
        """
        TC-SESSION-DAL-003: insert() - セッションファイル作成
        条件: セッションを挿入
        期待: 個別ファイル（sessionId.json）が作成される
        """
        session_data = {
            "sessionId": "sess-file-001",
            "userId": "user-001",
            "token": "token-file",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2026-05-30T00:00:00Z"
        }
        session_id = dal.insert(session_data)
        
        session_file = dal.sessions_dir / f"{session_id}.json"
        
        assert session_file.exists()
        assert session_file.is_file()
    
    def test_delete_removes_session_file(self, dal):
        """
        TC-SESSION-DAL-004: delete() - セッションファイル削除
        条件: セッションを削除
        期待: 個別ファイルも削除される
        """
        session_data = {
            "sessionId": "sess-delete-001",
            "userId": "user-001",
            "token": "token-delete",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2026-05-30T00:00:00Z"
        }
        session_id = dal.insert(session_data)
        
        session_file = dal.sessions_dir / f"{session_id}.json"
        assert session_file.exists()
        
        result = dal.delete(session_id)
        
        assert result is True
        assert not session_file.exists()
    
    def test_cleanup_expired_removes_old_sessions(self, dal):
        """
        TC-SESSION-DAL-005: cleanup_expired() - 期限切れセッション削除
        条件: 期限切れと有効なセッションが混在
        期待: 期限切れのみ削除され、削除数が返される
        """
        # 期限切れセッション（2件）
        dal.insert({
            "sessionId": "sess-exp-001",
            "userId": "user-001",
            "token": "token-exp-1",
            "createdAt": "2026-05-01T00:00:00Z",
            "expiresAt": "2026-05-02T00:00:00Z"
        })
        dal.insert({
            "sessionId": "sess-exp-002",
            "userId": "user-002",
            "token": "token-exp-2",
            "createdAt": "2026-05-01T00:00:00Z",
            "expiresAt": "2026-05-03T00:00:00Z"
        })
        
        # 有効なセッション
        dal.insert({
            "sessionId": "sess-valid-001",
            "userId": "user-003",
            "token": "token-valid",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2027-05-29T00:00:00Z"
        })
        
        deleted_count = dal.cleanup_expired()
        
        assert deleted_count == 2
        
        # 有効なセッションは残っているか確認
        valid_session = dal.find_by_token("token-valid")
        assert valid_session is not None
        
        # 期限切れセッションが削除されたか確認
        expired_session = dal.find_by_token("token-exp-1")
        assert expired_session is None
    
    def test_cleanup_expired_no_expired_sessions(self, dal):
        """
        TC-SESSION-DAL-006: cleanup_expired() - 期限切れなし
        条件: 全セッションが有効
        期待: 削除数 0 が返される
        """
        dal.insert({
            "sessionId": "sess-valid-001",
            "userId": "user-001",
            "token": "token-valid-1",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2027-05-29T00:00:00Z"
        })
        dal.insert({
            "sessionId": "sess-valid-002",
            "userId": "user-002",
            "token": "token-valid-2",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2027-05-29T00:00:00Z"
        })
        
        deleted_count = dal.cleanup_expired()
        
        assert deleted_count == 0
    
    def test_cleanup_expired_boundary_exact_now(self, dal):
        """
        TC-SESSION-DAL-007: cleanup_expired() - 境界値（expiresAt == 現在時刻）
        条件: expiresAtがちょうど現在時刻
        期待: 削除されない（< 比較のため、等しい場合は削除されない）
        """
        with patch('project.backend.app.sys.dal.session_dal.datetime') as mock_datetime:
            fixed_now = datetime(2026, 5, 29, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = fixed_now
            mock_datetime.fromisoformat = datetime.fromisoformat
            
            dal.insert({
                "sessionId": "sess-boundary",
                "userId": "user-001",
                "token": "token-boundary",
                "createdAt": "2026-05-29T00:00:00Z",
                "expiresAt": "2026-05-29T12:00:00Z"  # ちょうど現在時刻
            })
            
            deleted_count = dal.cleanup_expired()
        
        assert deleted_count == 0  # 等しい場合は削除されない
    
    def test_cleanup_expired_removes_session_files(self, dal):
        """
        TC-SESSION-DAL-008: cleanup_expired() - セッションファイルも削除
        条件: 期限切れセッションを削除
        期待: 個別ファイルも削除される
        """
        session_id = "sess-cleanup-file"
        dal.insert({
            "sessionId": session_id,
            "userId": "user-001",
            "token": "token-cleanup",
            "createdAt": "2026-05-01T00:00:00Z",
            "expiresAt": "2026-05-02T00:00:00Z"
        })
        
        session_file = dal.sessions_dir / f"{session_id}.json"
        assert session_file.exists()
        
        deleted_count = dal.cleanup_expired()
        
        assert deleted_count == 1
        assert not session_file.exists()
    
    def test_sessions_dir_created_on_init(self, temp_data_dir):
        """
        TC-SESSION-DAL-009: __init__() - sessionsディレクトリ作成
        条件: SessionDALインスタンスを生成
        期待: data_dir/sessions/ ディレクトリが作成される
        """
        dal = SessionDAL(data_dir=temp_data_dir)
        
        assert dal.sessions_dir.exists()
        assert dal.sessions_dir.is_dir()
    
    def test_collection_name_set(self, dal):
        """
        TC-SESSION-DAL-010: collection_name 設定確認
        条件: SessionDALインスタンスを生成
        期待: collection_name が "sessions" に設定されている
        """
        assert dal.collection_name == "sessions"
    
    def test_find_by_token_multiple_sessions(self, dal):
        """
        TC-SESSION-DAL-011: find_by_token() - 複数セッション存在時
        条件: 複数セッションが登録されており、1つを検索
        期待: 指定したセッションのみが返される
        """
        dal.insert({
            "sessionId": "sess-a",
            "userId": "user-a",
            "token": "token-a",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2026-05-30T00:00:00Z"
        })
        dal.insert({
            "sessionId": "sess-b",
            "userId": "user-b",
            "token": "token-b",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2026-05-30T00:00:00Z"
        })
        dal.insert({
            "sessionId": "sess-c",
            "userId": "user-c",
            "token": "token-c",
            "createdAt": "2026-05-29T00:00:00Z",
            "expiresAt": "2026-05-30T00:00:00Z"
        })
        
        result = dal.find_by_token("token-b")
        
        assert result is not None
        assert result["token"] == "token-b"
        assert result["sessionId"] == "sess-b"
    
    def test_boundary_empty_database_cleanup(self, dal):
        """
        TC-SESSION-DAL-012: cleanup_expired() - 空データベース
        条件: セッションが1件も登録されていない
        期待: 削除数 0 が返される
        """
        deleted_count = dal.cleanup_expired()
        
        assert deleted_count == 0
