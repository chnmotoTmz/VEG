"""詳細なデバッグスクリプト"""

import json
import os
import sys
import traceback
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("デバッグスクリプトを開始します")
    
    try:
        # 現在のディレクトリを確認
        logger.info(f"現在のディレクトリ: {os.getcwd()}")
        logger.info(f"Pythonのバージョン: {sys.version}")
        
        # 環境変数を確認
        try:
            import dotenv
            dotenv.load_dotenv()
            logger.info("環境変数を読み込みました")
            
            # GEMINIキーの存在チェック（値は表示しない）
            gemini_key = os.getenv('GEMINI_API_KEY')
            logger.info(f"GEMINI_API_KEY: {'設定されています' if gemini_key else '設定されていません'}")
        except Exception as e:
            logger.error(f"環境変数の読み込みに失敗: {str(e)}")
        
        # 設定ファイルを読み込む
        try:
            config_path = 'test_config.json'
            logger.info(f"設定ファイルを読み込み中: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
                logger.info(f"設定を読み込みました: {list(config.keys())}")
                
            # 重要な設定値を確認
            logger.info(f"入力ディレクトリ: {config.get('input_dir', 'なし')}")
            logger.info(f"出力ディレクトリ: {config.get('output_dir', 'なし')}")
            logger.info(f"シナリオファイル: {config.get('scenario_file', config.get('scenario_path', 'なし'))}")
            
            # ディレクトリの存在確認
            input_dir = config.get('input_dir')
            if input_dir and not os.path.exists(input_dir):
                logger.warning(f"入力ディレクトリが存在しません: {input_dir}")
            
            output_dir = config.get('output_dir')
            if output_dir and not os.path.exists(output_dir):
                logger.info(f"出力ディレクトリを作成します: {output_dir}")
                os.makedirs(output_dir, exist_ok=True)
            
            scenario_file = config.get('scenario_file', config.get('scenario_path'))
            if scenario_file and not os.path.exists(scenario_file):
                logger.warning(f"シナリオファイルが存在しません: {scenario_file}")
        except Exception as e:
            logger.error(f"設定ファイルの読み込みに失敗: {str(e)}")
            return
        
        # GeminiClientのインポートとテスト
        try:
            logger.info("GeminiClientをインポートします")
            from src.api_client import GeminiClient
            
            logger.info("GeminiClientをインスタンス化します")
            api_client = GeminiClient()
            
            logger.info("簡単なテキスト分析を実行します")
            result = api_client.text_analysis("こんにちは、テストメッセージです。この時刻を教えてください。")
            logger.info(f"テキスト分析の結果: {result[:100]}...")
        except Exception as e:
            logger.error(f"GeminiClientのテストに失敗: {str(e)}")
            traceback.print_exc()
        
        # 各コンポーネントを個別にインポート
        try:
            logger.info("ContentCrawlerをインポートします")
            from src.content_crawler import ContentCrawler
            content_crawler = ContentCrawler()
            logger.info("ContentCrawlerをインスタンス化しました")
            
            logger.info("ConceptGeneratorをインポートします")
            from src.concept_generator import ConceptGenerator
            concept_generator = ConceptGenerator(api_client=api_client)
            logger.info("ConceptGeneratorをインスタンス化しました")
            
            logger.info("SceneSelectorをインポートします")
            from src.scene_selector import SceneSelector
            scene_selector = SceneSelector(api_client=api_client)
            logger.info("SceneSelectorをインスタンス化しました")
            
            logger.info("EDLGeneratorをインポートします")
            from src.edl_generator import EDLGenerator
            edl_generator = EDLGenerator()
            logger.info("EDLGeneratorをインスタンス化しました")
            
            logger.info("SRTGeneratorをインポートします")
            from src.srt_generator import SRTGenerator
            srt_generator = SRTGenerator()
            logger.info("SRTGeneratorをインスタンス化しました")
        except Exception as e:
            logger.error(f"コンポーネントのインポートに失敗: {str(e)}")
            traceback.print_exc()
            return
        
        # VideoEditAgentをインポート
        try:
            logger.info("VideoEditAgentをインポートします")
            from src.main import VideoEditAgent
            
            logger.info("VideoEditAgentをインスタンス化します")
            agent = VideoEditAgent(config)
            logger.info("VideoEditAgentをインスタンス化しました")
            
            logger.info("処理を開始します")
            agent.process()
            logger.info("処理が完了しました")
        except Exception as e:
            logger.error(f"VideoEditAgentの処理に失敗: {str(e)}")
            traceback.print_exc()
    
    except Exception as e:
        logger.error(f"デバッグスクリプトでエラーが発生: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 