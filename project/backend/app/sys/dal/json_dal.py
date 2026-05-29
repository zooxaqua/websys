"""JSON DB 実装"""
import json
import os
import uuid
from pathlib import Path
from threading import Lock
from typing import Any, Optional
from .base import BaseDAL
from ..core.config import settings


class JsonDAL(BaseDAL):
    """JSON ファイルベースの DAL 実装"""
    
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self.cache: dict = {}
        self.lock = Lock()
        self._ensure_data_dir()
    
    def _ensure_data_dir(self) -> None:
        """データディレクトリを作成"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self) -> Path:
        """データファイルのパスを取得"""
        return self.data_dir / f"{self.collection_name}.json"
    
    def _load_data(self) -> dict:
        """データをロード（キャッシュあれば使用）"""
        file_path = self._get_file_path()
        
        if not file_path.exists():
            return {}
        
        with self.lock:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.cache = data
                return data
            except (json.JSONDecodeError, IOError):
                return {}
    
    def _save_data(self, data: dict) -> None:
        """データを保存"""
        file_path = self._get_file_path()
        
        with self.lock:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.cache = data
    
    def _generate_id(self) -> str:
        """ユニークIDを生成"""
        return str(uuid.uuid4())
    
    def _match_criteria(self, record: dict, criteria: dict) -> bool:
        """レコードが条件に一致するか"""
        for key, value in criteria.items():
            if key not in record or record[key] != value:
                return False
        return True
    
    def find(self, criteria: dict, limit: int = 100, offset: int = 0) -> list[dict]:
        """条件に一致するレコードを検索"""
        data = self._load_data()
        
        results = []
        for record_id, record in data.items():
            if self._match_criteria(record, criteria):
                results.append(record)
        
        # ページング
        return results[offset:offset + limit]
    
    def find_one(self, criteria: dict) -> Optional[dict]:
        """条件に一致する単一レコードを検索"""
        data = self._load_data()
        
        for record_id, record in data.items():
            if self._match_criteria(record, criteria):
                return record
        
        return None
    
    def insert(self, data: dict) -> str:
        """レコードを挿入"""
        all_data = self._load_data()
        
        # IDが指定されていなければ生成
        record_id = data.get("id", self._generate_id())
        data["id"] = record_id
        
        all_data[record_id] = data
        self._save_data(all_data)
        
        return record_id
    
    def update(self, id: str, data: dict) -> bool:
        """レコードを更新"""
        all_data = self._load_data()
        
        if id not in all_data:
            return False
        
        # 既存データとマージ
        all_data[id].update(data)
        all_data[id]["id"] = id  # IDは変更不可
        
        self._save_data(all_data)
        return True
    
    def delete(self, id: str) -> bool:
        """レコードを削除"""
        all_data = self._load_data()
        
        if id not in all_data:
            return False
        
        del all_data[id]
        self._save_data(all_data)
        return True
    
    def count(self, criteria: dict) -> int:
        """条件に一致するレコード数をカウント"""
        data = self._load_data()
        
        count = 0
        for record_id, record in data.items():
            if self._match_criteria(record, criteria):
                count += 1
        
        return count
    
    def exists(self, criteria: dict) -> bool:
        """条件に一致するレコードが存在するか"""
        return self.find_one(criteria) is not None
