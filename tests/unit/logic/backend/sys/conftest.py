"""
pytest設定ファイル
プロジェクトルートをパスに追加
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加（6段上 = websys/）
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "project" / "backend"))
