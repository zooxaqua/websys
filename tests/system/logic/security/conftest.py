"""
結合テスト用conftest（システムテストでも使用）
"""
import sys
from pathlib import Path

# 結合テストのconftestを再利用
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "integration" / "logic" / "backend" / "sys"))

from conftest import *  # noqa: F401, F403
