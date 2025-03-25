"""アプリケーション実行スクリプト"""

import json
import traceback
from src.main import VideoEditAgent

def main():
    try:
        print("設定ファイルを読み込み中...")
        with open('test_config.json', 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        
        print(f"設定内容: {config}")
        
        print("VideoEditAgentを初期化中...")
        agent = VideoEditAgent(config)
        
        print("処理を開始...")
        agent.process()
        
        print("処理が正常に完了しました。")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 