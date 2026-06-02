"""
単体テスト メインランナー
詳細設計の変更時に再生成される

実行方法:
  PYTHONPATH=project/backend project/backend/venv/bin/python -m pytest tests/unit/logic/backend/sys/test_runner.py -v
"""
import pytest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_all_backend():
    """全てのBackendテストを実行"""
    # test_casesディレクトリ内の全テストを実行
    test_dir = Path(__file__).parent / "test_cases"
    pytest.main([str(test_dir), "-v", "--tb=short"])


if __name__ == "__main__":
    # pytest経由での実行を推奨
    test_all_backend()
