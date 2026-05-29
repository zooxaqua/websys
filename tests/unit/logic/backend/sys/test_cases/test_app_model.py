"""
App モデルの単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: 有効なデータでインスタンス生成
- 異常系: バリデーションエラー
- 機能: validate_manifest(), to_dict(), from_dict()
"""
import pytest
import json
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError

# テスト対象
from project.backend.app.sys.models.app import App, AppResponse


def load_fixture(name: str) -> dict:
    """フィクスチャデータを読み込む"""
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "inputs" / "fixtures" / "app_fixtures.json"
    with open(fixture_path, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)
    return fixtures[name]


class TestAppModel:
    """App モデルのテストクラス"""
    
    def test_app_creation_valid(self):
        """
        TC-APP-001: 正常系 - 有効なアプリ作成
        条件: 全フィールドが有効な値
        期待: Appインスタンスが正常に生成される
        """
        data = load_fixture('valid_app')
        app = App(**data)
        
        assert app.id == data['id']
        assert app.name == data['name']
        assert app.version == data['version']
        assert app.enabled is True
        assert app.author == data['author']
    
    def test_app_creation_disabled(self):
        """
        TC-APP-002: 正常系 - 無効化アプリ作成
        条件: enabled=False
        期待: Appインスタンスが生成される（enabled=False）
        """
        data = load_fixture('valid_app_disabled')
        app = App(**data)
        
        assert app.enabled is False
    
    def test_app_creation_with_dependencies(self):
        """
        TC-APP-003: 正常系 - 依存関係ありアプリ作成
        条件: dependencies配列あり
        期待: 依存関係が保持される
        """
        data = load_fixture('app_with_dependencies')
        app = App(**data)
        
        assert len(app.dependencies) == 2
        assert 'base-lib' in app.dependencies
        assert 'utils-lib' in app.dependencies
        assert len(app.requiredPermissions) == 3
    
    def test_app_validate_manifest_valid(self):
        """
        TC-APP-004: validate_manifest() - 正常なマニフェスト
        条件: 必須フィールド全て含む
        期待: True
        """
        data = load_fixture('valid_app')
        app = App(**data)
        
        assert app.validate_manifest() is True
    
    def test_app_validate_manifest_invalid_missing_field(self):
        """
        TC-APP-005: validate_manifest() - 必須フィールド欠損
        条件: マニフェストに必須フィールドなし
        期待: False
        """
        data = load_fixture('invalid_manifest_missing_field')
        app = App(**data)
        
        assert app.validate_manifest() is False
    
    def test_app_to_dict(self):
        """
        TC-APP-006: to_dict() - 辞書変換
        条件: 正常なAppインスタンス
        期待: 辞書形式に変換される
        """
        data = load_fixture('valid_app')
        app = App(**data)
        
        result = app.to_dict()
        
        assert isinstance(result, dict)
        assert result['id'] == data['id']
        assert result['name'] == data['name']
        assert result['enabled'] == data['enabled']
    
    def test_app_from_dict(self):
        """
        TC-APP-007: from_dict() - 辞書からインスタンス生成
        条件: 正常な辞書データ
        期待: Appインスタンスが生成される
        """
        data = load_fixture('valid_app')
        app = App.from_dict(data)
        
        assert isinstance(app, App)
        assert app.id == data['id']
        assert app.name == data['name']
    
    def test_app_serialization_roundtrip(self):
        """
        TC-APP-008: シリアライズ・デシリアライズのラウンドトリップ
        条件: App → dict → App
        期待: データが保持される
        """
        data = load_fixture('valid_app')
        app1 = App(**data)
        
        dict_data = app1.to_dict()
        app2 = App.from_dict(dict_data)
        
        assert app1.id == app2.id
        assert app1.name == app2.name
        assert app1.version == app2.version
        assert app1.enabled == app2.enabled
    
    def test_app_invalid_missing_id(self):
        """
        TC-APP-009: 異常系 - id欠損
        条件: idフィールドなし
        期待: ValidationError
        """
        data = load_fixture('valid_app')
        del data['id']
        
        with pytest.raises(ValidationError) as exc_info:
            App(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('id',) for e in errors)
    
    def test_app_invalid_missing_name(self):
        """
        TC-APP-010: 異常系 - name欠損
        条件: nameフィールドなし
        期待: ValidationError
        """
        data = load_fixture('valid_app')
        del data['name']
        
        with pytest.raises(ValidationError) as exc_info:
            App(**data)
        
        errors = exc_info.value.errors()
        assert any(e['loc'] == ('name',) for e in errors)


class TestAppResponseModel:
    """AppResponse モデルのテストクラス"""
    
    def test_appresponse_creation_valid(self):
        """
        TC-APP-RESPONSE-001: 正常系 - AppResponse作成
        条件: 必須フィールドあり
        期待: AppResponseインスタンスが生成される
        """
        data = load_fixture('valid_app')
        # AppResponseに不要なフィールドを削除
        response_data = {
            'id': data['id'],
            'name': data['name'],
            'version': data['version'],
            'description': data['description'],
            'icon': data['icon'],
            'entryPoint': data['entryPoint'],
            'apiPrefix': data['apiPrefix'],
            'enabled': data['enabled'],
            'author': data['author'],
            'lastUpdated': data['lastUpdated']
        }
        
        response = AppResponse(**response_data)
        
        assert response.id == data['id']
        assert response.name == data['name']
        assert response.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
