"""テスト実行スクリプト（ログ出力付き）"""

import json
import os
import traceback
import logging
import sys

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("テスト実行を開始します")
    
    try:
        # 設定ファイルを読み込む
        logger.info("設定ファイルを読み込みます: test_config.json")
        with open('test_config.json', 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
        
        logger.info("設定内容: %s", config)
        
        # モジュールのインポート（このタイミングでインポートすることでログにエラーを記録）
        logger.info("モジュールをインポートします")
        try:
            from srt_scene_tools.main import VideoEditAgent
            logger.info("VideoEditAgentをインポートしました")
        except Exception as e:
            logger.error("モジュールのインポートに失敗しました: %s", str(e))
            traceback.print_exc()
            return 1
        
        # エージェントを作成して実行
        logger.info("VideoEditAgentを初期化します")
        agent = VideoEditAgent(config)
        
        logger.info("処理を開始します")
        agent.process()
        
        logger.info("処理が完了しました")
        return 0
    except Exception as e:
        logger.error("エラーが発生しました: %s", str(e))
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical("予期しないエラーが発生しました: %s", str(e))
        traceback.print_exc() 