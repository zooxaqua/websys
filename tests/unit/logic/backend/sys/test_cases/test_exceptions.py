"""
単体テスト: Core Exceptions

テスト対象: project/backend/app/sys/core/exceptions.py
MCDC 対応: 各条件が独立して判定結果を変える組み合わせを網羅
"""
import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "project" / "backend"))

from app.sys.core.exceptions import (
    WebSystemException,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    UserNotFoundException,
    UserAlreadyExistsException
)


class TestExceptions:
    """例外クラスのテストクラス"""
    
    # TC-EXC-001: 正常系 - WebSystemException
    def test_websystem_exception(self):
        """WebSystemException"""
        exc = WebSystemException(message="Test error", error_code="TEST-001")
        assert str(exc) == "Test error"
        assert exc.code == "TEST-001"
        assert exc.status_code == 500
    
    # TC-EXC-002: 正常系 - AuthenticationException
    def test_authentication_exception(self):
        """AuthenticationException"""
        exc = AuthenticationException(code="ERR-SYS-AUTH-001", message="Auth failed")
        assert "Auth failed" in str(exc)
        assert exc.status_code == 401
    
    # TC-EXC-003: 正常系 - AuthorizationException
    def test_authorization_exception(self):
        """AuthorizationException"""
        exc = AuthorizationException(message="Permission denied")
        assert "Permission denied" in str(exc)
        assert exc.status_code == 403
    
    # TC-EXC-004: 正常系 - ValidationException
    def test_validation_exception(self):
        """ValidationException"""
        exc = ValidationException(code="ERR-SYS-VAL-001", message="Invalid input")
        assert "Invalid input" in str(exc)
        assert exc.status_code == 400
    
    # TC-EXC-005: 正常系 - UserNotFoundException
    def test_user_not_found_exception(self):
        """UserNotFoundException"""
        exc = UserNotFoundException(user_id="user-001")
        assert "ユーザーが見つかりません" in str(exc)
        assert exc.details["userId"] == "user-001"
        assert exc.status_code == 404
    
    # TC-EXC-006: 正常系 - UserAlreadyExistsException
    def test_user_already_exists_exception(self):
        """UserAlreadyExistsException"""
        exc = UserAlreadyExistsException(field="username", value="testuser")
        assert "ユーザー名が既に存在します" in str(exc)
        assert exc.details["value"] == "testuser"
        assert exc.status_code == 409


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
