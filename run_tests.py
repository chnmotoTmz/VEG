#!/usr/bin/env python3
"""テスト実行スクリプト"""

import unittest
import sys
import os

# テストディレクトリを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """すべてのテストを実行"""
    # テストディレクトリからすべてのテストを検出
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # テスト実行
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # 終了コードの設定（失敗があれば1、なければ0）
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 