"""テスト実行スクリプト"""

import json
import os
import traceback
from src.main import VideoEditAgent

def main():
    # 設定ファイルを読み込む
    try:
        with open('test_config.json', 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        
        # エージェントを作成して実行
        agent = VideoEditAgent(config)
        agent.process()
        
        print("処理が完了しました")
        return 0
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    main() 