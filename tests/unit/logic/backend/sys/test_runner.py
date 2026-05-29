"""
単体テスト メインランナー
詳細設計の変更時に再生成される

実行方法:
  pytest tests/unit/logic/backend/sys/test_runner.py -v
"""
import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_user_model():
    """User モデルの全テストを実行"""
    from test_cases.test_user_model import (
        TestUserModel,
        TestUserCreateModel,
        TestUserUpdateModel,
        TestUserResponseModel
    )
    
    # User モデルテスト
    test_class = TestUserModel()
    test_class.test_user_creation_valid_user()
    test_class.test_user_creation_valid_admin()
    test_class.test_user_boundary_username_min()
    test_class.test_user_boundary_username_max()
    test_class.test_user_boundary_displayname_min()
    test_class.test_user_boundary_displayname_max()
    test_class.test_user_invalid_username_too_short()
    test_class.test_user_invalid_username_too_long()
    test_class.test_user_invalid_role()
    test_class.test_user_invalid_email()
    test_class.test_user_invalid_displayname_empty()
    test_class.test_user_invalid_displayname_too_long()
    test_class.test_user_to_dict()
    test_class.test_user_from_dict()
    test_class.test_user_serialization_roundtrip()
    test_class.test_user_validate_password_success()
    test_class.test_user_validate_password_failure()
    
    # UserCreate モデルテスト
    create_test = TestUserCreateModel()
    create_test.test_usercreate_valid()
    create_test.test_usercreate_invalid_password_too_short()
    
    # UserUpdate モデルテスト
    update_test = TestUserUpdateModel()
    update_test.test_userupdate_partial()
    
    # UserResponse モデルテスト
    response_test = TestUserResponseModel()
    response_test.test_userresponse_no_password()


if __name__ == "__main__":
    # pytest経由での実行を推奨
    pytest.main([__file__, "-v"])
