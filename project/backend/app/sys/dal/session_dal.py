"""セッションDAL"""
from datetime import datetime
from pathlib import Path
from typing import Optional
import json
from .json_dal import JsonDAL
from ..core.config import settings


class SessionDAL(JsonDAL):
    """セッション専用DAL"""
    
    collection_name = "sessions"
    
    def __init__(self, data_dir: Optional[str] = None):
        super().__init__(data_dir)
        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def find_by_token(self, token: str) -> Optional[dict]:
        """トークンでセッションを検索"""
        return self.find_one({"token": token})
    
    def cleanup_expired(self) -> int:
        """期限切れセッションを削除"""
        all_data = self._load_data()
        deleted_count = 0
        
        for session_id, session in list(all_data.items()):
            expires_at = session.get("expiresAt")
            if expires_at:
                from datetime import timezone
                if datetime.fromisoformat(expires_at.replace("Z", "+00:00")) < datetime.now(timezone.utc):
                    self.delete(session_id)
                    deleted_count += 1
        
        return deleted_count
    
    def _save_session_file(self, session: dict) -> None:
        """セッション情報を個別ファイルに保存"""
        session_id = session["sessionId"]
        file_path = self.sessions_dir / f"{session_id}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
    
    def _delete_session_file(self, session_id: str) -> None:
        """セッションファイルを削除"""
        file_path = self.sessions_dir / f"{session_id}.json"
        if file_path.exists():
            file_path.unlink()
    
    def insert(self, data: dict) -> str:
        """セッションを挿入（ファイルにも保存）"""
        # sessionIdをidとして扱う
        if "sessionId" in data and "id" not in data:
            data["id"] = data["sessionId"]
        session_id = super().insert(data)
        self._save_session_file(data)
        return session_id
    
    def delete(self, id: str) -> bool:
        """セッションを削除（ファイルも削除）"""
        result = super().delete(id)
        if result:
            self._delete_session_file(id)
        return result
