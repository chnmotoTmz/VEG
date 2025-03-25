"""デバッグ用実行スクリプト"""

import pdb
import json
import os
import traceback
import sys

def main():
    try:
        # 設定ファイルを読み込む
        print("設定ファイルを読み込みます...")
        with open('test_config.json', 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        
        print("設定内容:", config)
        
        # モジュールのインポート
        print("モジュールをインポートします...")
        from src.main import VideoEditAgent
        
        # ブレークポイントを設定
        pdb.set_trace()
        
        # エージェントを作成して実行
        print("VideoEditAgentを初期化します...")
        agent = VideoEditAgent(config)
        
        print("処理を開始します...")
        agent.process()
        
        print("処理が完了しました")
        return 0
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return 1

if __name__ == '__main__':
    sys.exit(main()) 