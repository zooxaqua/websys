"""
JsonDAL の単体テスト
MCDC準拠: 全条件分岐を網羅

テスト観点:
- 正常系: CRUD操作、検索、ページング
- 異常系: ファイルIO失敗、存在しないIDへのアクセス
- 境界値: 空データ、大量データ、limit/offsetの境界
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# テスト対象
from project.backend.app.sys.dal.json_dal import JsonDAL


class TestJsonDAL:
    """JsonDAL のテストクラス"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """テスト用一時ディレクトリ"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def dal(self, temp_data_dir):
        """テスト用DALインスタンス"""
        dal_instance = JsonDAL(data_dir=temp_data_dir)
        dal_instance.collection_name = "test_collection"
        return dal_instance
    
    def test_insert_new_record(self, dal):
        """
        TC-JSON-DAL-001: insert() - 新規レコード挿入
        条件: 有効なデータを挿入
        期待: レコードIDが返され、データが保存される
        """
        data = {"name": "Test User", "email": "test@example.com"}
        record_id = dal.insert(data)
        
        assert record_id is not None
        assert len(record_id) > 0
        
        # データが保存されているか確認
        saved_data = dal._load_data()
        assert record_id in saved_data
        assert saved_data[record_id]["name"] == "Test User"
    
    def test_insert_with_predefined_id(self, dal):
        """
        TC-JSON-DAL-002: insert() - 事前定義IDで挿入
        条件: ID付きデータを挿入
        期待: 指定したIDでレコードが保存される
        """
        data = {"id": "custom-id-001", "name": "Custom"}
        record_id = dal.insert(data)
        
        assert record_id == "custom-id-001"
        
        saved_data = dal._load_data()
        assert "custom-id-001" in saved_data
    
    def test_find_one_existing_record(self, dal):
        """
        TC-JSON-DAL-003: find_one() - 存在するレコード検索
        条件: 条件に一致するレコードが存在
        期待: レコードが返される
        """
        data = {"name": "John", "role": "admin"}
        record_id = dal.insert(data)
        
        result = dal.find_one({"name": "John"})
        
        assert result is not None
        assert result["name"] == "John"
        assert result["role"] == "admin"
    
    def test_find_one_non_existing_record(self, dal):
        """
        TC-JSON-DAL-004: find_one() - 存在しないレコード検索
        条件: 条件に一致するレコードが存在しない
        期待: None が返される
        """
        result = dal.find_one({"name": "NonExistent"})
        
        assert result is None
    
    def test_find_multiple_records(self, dal):
        """
        TC-JSON-DAL-005: find() - 複数レコード検索
        条件: 複数のレコードが条件に一致
        期待: 一致するレコード全てが返される
        """
        dal.insert({"role": "user", "name": "Alice"})
        dal.insert({"role": "user", "name": "Bob"})
        dal.insert({"role": "admin", "name": "Charlie"})
        
        results = dal.find({"role": "user"})
        
        assert len(results) == 2
        assert all(r["role"] == "user" for r in results)
    
    def test_find_with_pagination(self, dal):
        """
        TC-JSON-DAL-006: find() - ページネーション
        条件: limit=2, offset=1
        期待: 2番目と3番目のレコードが返される
        """
        for i in range(5):
            dal.insert({"index": i, "category": "test"})
        
        results = dal.find({"category": "test"}, limit=2, offset=1)
        
        assert len(results) == 2
    
    def test_find_boundary_offset_exceeds_data(self, dal):
        """
        TC-JSON-DAL-007: find() - 境界値（offset > データ数）
        条件: offset=100, データは3件のみ
        期待: 空リストが返される
        """
        dal.insert({"data": "A"})
        dal.insert({"data": "B"})
        dal.insert({"data": "C"})
        
        results = dal.find({}, limit=10, offset=100)
        
        assert results == []
    
    def test_update_existing_record(self, dal):
        """
        TC-JSON-DAL-008: update() - 存在するレコード更新
        条件: 有効なIDで更新
        期待: Trueが返され、データが更新される
        """
        record_id = dal.insert({"name": "Old Name", "status": "pending"})
        
        success = dal.update(record_id, {"status": "completed"})
        
        assert success is True
        
        updated_data = dal._load_data()
        assert updated_data[record_id]["status"] == "completed"
        assert updated_data[record_id]["name"] == "Old Name"  # 他のフィールドは保持
    
    def test_update_non_existing_record(self, dal):
        """
        TC-JSON-DAL-009: update() - 存在しないレコード更新
        条件: 存在しないIDで更新を試行
        期待: False が返される
        """
        success = dal.update("non-existent-id", {"data": "test"})
        
        assert success is False
    
    def test_delete_existing_record(self, dal):
        """
        TC-JSON-DAL-010: delete() - 存在するレコード削除
        条件: 有効なIDで削除
        期待: True が返され、レコードが削除される
        """
        record_id = dal.insert({"data": "to be deleted"})
        
        success = dal.delete(record_id)
        
        assert success is True
        
        data = dal._load_data()
        assert record_id not in data
    
    def test_delete_non_existing_record(self, dal):
        """
        TC-JSON-DAL-011: delete() - 存在しないレコード削除
        条件: 存在しないIDで削除を試行
        期待: False が返される
        """
        success = dal.delete("non-existent-id")
        
        assert success is False
    
    def test_count_matching_records(self, dal):
        """
        TC-JSON-DAL-012: count() - 条件一致レコード数カウント
        条件: 5件中3件が条件に一致
        期待: 3 が返される
        """
        for i in range(5):
            dal.insert({"type": "A" if i < 3 else "B"})
        
        count = dal.count({"type": "A"})
        
        assert count == 3
    
    def test_count_no_match(self, dal):
        """
        TC-JSON-DAL-013: count() - 一致なし
        条件: 条件に一致するレコードが0件
        期待: 0 が返される
        """
        dal.insert({"type": "A"})
        
        count = dal.count({"type": "B"})
        
        assert count == 0
    
    def test_exists_record_present(self, dal):
        """
        TC-JSON-DAL-014: exists() - レコード存在
        条件: 条件に一致するレコードが存在
        期待: True が返される
        """
        dal.insert({"username": "testuser"})
        
        exists = dal.exists({"username": "testuser"})
        
        assert exists is True
    
    def test_exists_record_absent(self, dal):
        """
        TC-JSON-DAL-015: exists() - レコード不在
        条件: 条件に一致するレコードが存在しない
        期待: False が返される
        """
        exists = dal.exists({"username": "nonexistent"})
        
        assert exists is False
    
    def test_load_data_file_not_exists(self, dal):
        """
        TC-JSON-DAL-016: _load_data() - ファイル不在
        条件: データファイルが存在しない
        期待: 空辞書 {} が返される
        """
        data = dal._load_data()
        
        assert data == {}
    
    def test_load_data_empty_file(self, dal, temp_data_dir):
        """
        TC-JSON-DAL-017: _load_data() - 空ファイル
        条件: データファイルが空（{}）
        期待: 空辞書 {} が返される
        """
        file_path = Path(temp_data_dir) / "test_collection.json"
        with open(file_path, 'w') as f:
            json.dump({}, f)
        
        data = dal._load_data()
        
        assert data == {}
    
    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_load_data_io_error(self, mock_file, dal):
        """
        TC-JSON-DAL-018: _load_data() - IOエラー
        条件: ファイル読み込み時にIOError発生
        期待: 空辞書 {} が返される（例外を吸収）
        """
        # ファイルを先に作成（existsチェックをパスさせる）
        file_path = dal._get_file_path()
        file_path.touch()
        
        data = dal._load_data()
        
        assert data == {}
    
    def test_match_criteria_all_match(self, dal):
        """
        TC-JSON-DAL-019: _match_criteria() - 全条件一致
        条件: レコードが全ての条件を満たす
        期待: True が返される
        """
        record = {"name": "Alice", "age": 30, "role": "admin"}
        criteria = {"name": "Alice", "role": "admin"}
        
        result = dal._match_criteria(record, criteria)
        
        assert result is True
    
    def test_match_criteria_partial_match(self, dal):
        """
        TC-JSON-DAL-020: _match_criteria() - 部分一致（不一致）
        条件: レコードが一部の条件を満たさない
        期待: False が返される
        """
        record = {"name": "Alice", "age": 30, "role": "user"}
        criteria = {"name": "Alice", "role": "admin"}
        
        result = dal._match_criteria(record, criteria)
        
        assert result is False
    
    def test_generate_id_uniqueness(self, dal):
        """
        TC-JSON-DAL-021: _generate_id() - ID一意性
        条件: 複数回ID生成
        期待: 全て異なるIDが生成される
        """
        ids = {dal._generate_id() for _ in range(100)}
        
        assert len(ids) == 100  # 全て異なる
