"""
User モデルの単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: 有効なデータでインスタンス生成
- 異常系: バリデーションエラー（必須項目欠損、型不正、制約違反）
- 境界値: 文字列長の上限・下限
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError
from unittest.mock import patch

# テスト対象
from project.backend.app.sys.models.user import User, UserCreate, UserUpdate, UserResponse


def load_fixture(name: str) -> dict:
    """フィクスチャデータを読み込む"""
    # tests/unit/logic/backend/sys/test_cases/ から tests/unit/inputs/ へ
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "inputs" / "fixtures" / "user_fixtures.json"
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    return fixtures[name]


def load_expected_error(name: str) -> dict:
    """期待されるエラー情報を読み込む"""
    # tests/unit/logic/backend/sys/test_cases/ から tests/unit/inputs/ へ
    error_path = Path(__file__).parent.parent.parent.parent.parent / "inputs" / "expected" / "user_validation_errors.json"
    with open(error_path, 'r', encoding='utf-8') as f:
        errors = json.load(f)
    return errors[name]


class TestUserModel:
    """User モデルのテストクラス"""
    
    def test_user_creation_valid_user(self):
        """
        TC-USER-001: 正常系 - 一般ユーザー作成成功
        条件: 全フィールドが有効な値
        期待: Userインスタンスが正常に生成される
        """
        data = load_fixture('valid_user')
        user = User(**data)
        
        assert user.id == data['id']
        assert user.username == data['username']
        assert user.passwordHash == data['passwordHash']
        assert user.displayName == data['displayName']
        assert user.role == data['role']
        assert user.email == data['email']
        assert user.metadata == data['metadata']
        assert user.lastLogin is None
    
    def test_user_creation_valid_admin(self):
        """
        TC-USER-002: 正常系 - 管理者ユーザー作成成功
        条件: role="admin"、lastLoginあり
        期待: Userインスタンスが正常に生成される
        """
        data = load_fixture('valid_admin')
        user = User(**data)
        
        assert user.role == "admin"
        assert user.lastLogin is not None
    
    def test_user_boundary_username_min(self):
        """
        TC-USER-003: 境界値 - username 最小長（3文字）
        条件: username="abc"（3文字）
        期待: 正常に生成される
        """
        data = load_fixture('boundary_username_min')
        user = User(**data)
        
        assert len(user.username) == 3
        assert user.username == "abc"
    
    def test_user_boundary_username_max(self):
        """
        TC-USER-004: 境界値 - username 最大長（50文字）
        条件: username=50文字
        期待: 正常に生成される
        """
        data = load_fixture('boundary_username_max')
        user = User(**data)
        
        assert len(user.username) == 50
    
    def test_user_boundary_displayname_min(self):
        """
        TC-USER-005: 境界値 - displayName 最小長（1文字）
        条件: displayName="A"（1文字）
        期待: 正常に生成される
        """
        data = load_fixture('boundary_displayname_min')
        user = User(**data)
        
        assert len(user.displayName) == 1
        assert user.displayName == "A"
    
    def test_user_boundary_displayname_max(self):
        """
        TC-USER-006: 境界値 - displayName 最大長（100文字）
        条件: displayName=100文字
        期待: 正常に生成される
        """
        data = load_fixture('boundary_displayname_max')
        user = User(**data)
        
        assert len(user.displayName) == 100
    
    def test_user_invalid_username_too_short(self):
        """
        TC-USER-007: 異常系 - username 最小長違反（2文字）
        条件: username="ab"（2文字）
        期待: ValidationError が発生
        """
        data = load_fixture('invalid_username_too_short')
        expected = load_expected_error('username_too_short')
        
        with pytest.raises(ValidationError) as exc_info:
            User(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('username',) for e in errors)
        assert any('at least 3 characters' in str(e['msg']).lower() or 'min_length' in str(e['type']) for e in errors)
    
    def test_user_invalid_username_too_long(self):
        """
        TC-USER-008: 異常系 - username 最大長違反（51文字）
        条件: username=51文字
        期待: ValidationError が発生
        """
        data = load_fixture('invalid_username_too_long')
        expected = load_expected_error('username_too_long')
        
        with pytest.raises(ValidationError) as exc_info:
            User(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('username',) for e in errors)
        assert any('at most 50 characters' in str(e['msg']).lower() or 'max_length' in str(e['type']) for e in errors)
    
    def test_user_invalid_role(self):
        """
        TC-USER-009: 異常系 - role パターン違反
        条件: role="superadmin"（許可されていない値）
        期待: ValidationError が発生
        """
        data = load_fixture('invalid_role')
        expected = load_expected_error('invalid_role')
        
        with pytest.raises(ValidationError) as exc_info:
            User(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('role',) for e in errors)
        assert any('pattern' in str(e['type']).lower() or 'string_pattern_mismatch' in str(e['type']) for e in errors)
    
    def test_user_invalid_email(self):
        """
        TC-USER-010: 異常系 - email フォーマット違反
        条件: email="not-an-email"（@なし）
        期待: ValidationError が発生
        """
        data = load_fixture('invalid_email')
        expected = load_expected_error('invalid_email')
        
        with pytest.raises(ValidationError) as exc_info:
            User(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('email',) for e in errors)
    
    def test_user_invalid_displayname_empty(self):
        """
        TC-USER-011: 異常系 - displayName 最小長違反（空文字）
        条件: displayName=""
        期待: ValidationError が発生
        """
        data = load_fixture('invalid_displayname_empty')
        expected = load_expected_error('displayname_empty')
        
        with pytest.raises(ValidationError) as exc_info:
            User(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('displayName',) for e in errors)
        assert any('at least 1 character' in str(e['msg']).lower() or 'min_length' in str(e['type']) for e in errors)
    
    def test_user_invalid_displayname_too_long(self):
        """
        TC-USER-012: 異常系 - displayName 最大長違反（101文字）
        条件: displayName=101文字
        期待: ValidationError が発生
        """
        data = load_fixture('invalid_displayname_too_long')
        expected = load_expected_error('displayname_too_long')
        
        with pytest.raises(ValidationError) as exc_info:
            User(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('displayName',) for e in errors)
        assert any('at most 100 characters' in str(e['msg']).lower() or 'max_length' in str(e['type']) for e in errors)
    
    def test_user_to_dict(self):
        """
        TC-USER-013: 正常系 - to_dict() メソッド
        条件: 有効なUserインスタンス
        期待: 辞書形式に変換される
        """
        data = load_fixture('valid_user')
        user = User(**data)
        result = user.to_dict()
        
        assert isinstance(result, dict)
        assert result['id'] == data['id']
        assert result['username'] == data['username']
    
    def test_user_from_dict(self):
        """
        TC-USER-014: 正常系 - from_dict() クラスメソッド
        条件: 有効な辞書データ
        期待: Userインスタンスが生成される
        """
        data = load_fixture('valid_user')
        user = User.from_dict(data)
        
        assert isinstance(user, User)
        assert user.id == data['id']
        assert user.username == data['username']
    
    def test_user_serialization_roundtrip(self):
        """
        TC-USER-015: 正常系 - シリアライズ・デシリアライズのラウンドトリップ
        条件: User → dict → User
        期待: 元のデータと一致する
        """
        original_data = load_fixture('valid_user')
        user1 = User(**original_data)
        
        # シリアライズ
        serialized = user1.to_dict()
        
        # デシリアライズ
        user2 = User.from_dict(serialized)
        
        # 検証
        assert user1.id == user2.id
        assert user1.username == user2.username
        assert user1.email == user2.email
        assert user1.role == user2.role
    
    @patch('project.backend.app.sys.core.security.verify_password')
    def test_user_validate_password_success(self, mock_verify):
        """
        TC-USER-016: 正常系 - パスワード検証成功
        条件: 正しいパスワードを検証
        期待: True が返される
        """
        mock_verify.return_value = True
        
        data = load_fixture('valid_user')
        user = User(**data)
        
        result = user.validate_password("correct_password")
        
        assert result is True
        mock_verify.assert_called_once_with("correct_password", user.passwordHash)
    
    @patch('project.backend.app.sys.core.security.verify_password')
    def test_user_validate_password_failure(self, mock_verify):
        """
        TC-USER-017: 異常系 - パスワード検証失敗
        条件: 誤ったパスワードを検証
        期待: False が返される
        """
        mock_verify.return_value = False
        
        data = load_fixture('valid_user')
        user = User(**data)
        
        result = user.validate_password("wrong_password")
        
        assert result is False
        mock_verify.assert_called_once_with("wrong_password", user.passwordHash)


class TestUserCreateModel:
    """UserCreate モデルのテストクラス"""
    
    def test_usercreate_valid(self):
        """
        TC-USERCREATE-001: 正常系 - 有効な作成リクエスト
        条件: 全フィールドが有効
        期待: UserCreateインスタンスが生成される
        """
        data = {
            "username": "newuser",
            "password": "password123",
            "displayName": "New User",
            "role": "user",
            "email": "newuser@example.com",
            "metadata": {}
        }
        user_create = UserCreate(**data)
        
        assert user_create.username == data['username']
        assert user_create.password == data['password']
    
    def test_usercreate_invalid_password_too_short(self):
        """
        TC-USERCREATE-002: 異常系 - パスワード最小長違反
        条件: password="pass123"（7文字）
        期待: ValidationError が発生
        """
        data = {
            "username": "newuser",
            "password": "pass123",  # 7文字（8文字未満）
            "displayName": "New User",
            "role": "user",
            "email": "newuser@example.com"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            user_create = UserCreate(**data)
        
        # エラー内容の検証
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('password',) for e in errors)
        assert any('at least 8 characters' in str(e['msg']).lower() or 'string_too_short' in str(e['type']) for e in errors)


class TestUserUpdateModel:
    """UserUpdate モデルのテストクラス"""
    
    def test_userupdate_partial(self):
        """
        TC-USERUPDATE-001: 正常系 - 部分更新
        条件: displayNameのみ更新
        期待: UserUpdateインスタンスが生成される
        """
        data = {
            "displayName": "Updated Name"
        }
        user_update = UserUpdate(**data)
        
        assert user_update.displayName == "Updated Name"
        assert user_update.role is None
        assert user_update.email is None


class TestUserResponseModel:
    """UserResponse モデルのテストクラス"""
    
    def test_userresponse_no_password(self):
        """
        TC-USERRESPONSE-001: 正常系 - パスワードハッシュを含まない
        条件: UserResponseインスタンス生成
        期待: passwordHashフィールドが存在しない
        """
        data = {
            "id": "user-001",
            "username": "testuser",
            "displayName": "Test User",
            "role": "user",
            "email": "test@example.com",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "metadata": {}
        }
        response = UserResponse(**data)
        
        # passwordHash フィールドが存在しないことを確認
        assert not hasattr(response, 'passwordHash')
        assert response.username == data['username']
