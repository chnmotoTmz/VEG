"""
非常にシンプルなテストスクリプト
"""
import os
import json
import logging

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    scenario_path = "test_data/test_scenario.json"
    content_dir = "test_data"
    output_srt = "test_outputs/test_result.srt"
    output_edl = "test_outputs/test_result.edl"
    
    logger.info(f"シナリオファイル: {scenario_path}")
    logger.info(f"コンテンツディレクトリ: {content_dir}")
    
    try:
        # シナリオファイルの読み込み
        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        logger.info(f"シナリオタイトル: {scenario_data.get('title', 'Unknown')}")
        
        # テストデータディレクトリの内容を確認
        file_count = 0
        json_files = []
        
        # ディレクトリの内容を列挙
        for root, dirs, files in os.walk(content_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_count += 1
                if file.endswith('.json'):
                    json_files.append(file_path)
                    
        logger.info(f"コンテンツディレクトリ内のファイル数: {file_count}")
        logger.info(f"JSONファイル: {json_files}")
        
        # JSONファイルの内容を確認
        for json_path in json_files:
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                logger.info(f"JSONファイル '{json_path}' の内容:")
                logger.info(f"  タイトル: {data.get('title', 'Unknown')}")
                logger.info(f"  シーン数: {len(data.get('scenes', []))}")
                
            except Exception as e:
                logger.error(f"JSONファイル '{json_path}' の読み込みエラー: {e}")
        
        # ダミーファイルの出力
        os.makedirs(os.path.dirname(output_srt), exist_ok=True)
        os.makedirs(os.path.dirname(output_edl), exist_ok=True)
        
        with open(output_srt, 'w', encoding='utf-8') as f:
            f.write("1\n00:00:00,000 --> 00:00:10,000\nテストシーン\n\n")
            
        with open(output_edl, 'w', encoding='utf-8') as f:
            f.write("TITLE: Test EDL\nFCM: NON-DROP FRAME\n\n")
            f.write("001  AX       AA/V  C        00:00:00,000 00:00:10,000 00:00:00,000 00:00:10,000\n")
            f.write("* FROM CLIP NAME: TEST\n\n")
            
        logger.info(f"SRTファイルを作成しました: {output_srt}")
        logger.info(f"EDLファイルを作成しました: {output_edl}")
        logger.info("テスト完了")
        
    except Exception as e:
        logger.error(f"エラー: {e}", exc_info=True)
        return False
        
    return True

if __name__ == "__main__":
    success = main()
    print(f"テスト結果: {'成功' if success else '失敗'}") 