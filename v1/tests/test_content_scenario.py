import os
import sys
import json
import logging
from pathlib import Path

# プロジェクトのルートパスをインポートパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from srt_scene_tools.utils import ContentCrawler
from srt_scene_tools.scenario_writer import ScenarioWriter, ScenarioInput

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("test_content_scenario")

def test_content_crawler():
    """ContentCrawlerのテスト - 台詞の抽出とトピック/場所の検出"""
    logger.info("ContentCrawlerテスト開始")
    
    # テストディレクトリ
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        logger.error(f"テストディレクトリが見つかりません: {test_dir}")
        return False
    
    # ContentCrawlerの初期化と実行
    crawler = ContentCrawler()
    contents = crawler.crawl(test_dir)
    
    logger.info(f"読み込んだコンテンツ数: {len(contents)}")
    
    # 検証 - 各コンテンツの基本情報を表示
    success = True
    
    for i, content in enumerate(contents):
        logger.info(f"\nコンテンツ {i+1}:")
        logger.info(f"  タイトル: {getattr(content, 'title', 'タイトルなし')}")
        
        # シーン数の検証
        scenes = getattr(content, 'scenes', [])
        scenes_count = len(scenes)
        logger.info(f"  シーン数: {scenes_count}")
        
        # ビデオ長さの検証
        duration = getattr(content, 'total_duration', 0)
        logger.info(f"  総時間: {duration}秒")
        
        # トピックの検証
        topics = getattr(content, 'topics', [])
        logger.info(f"  トピック数: {len(topics)}")
        logger.info(f"  トピック: {', '.join(topics)}")
        
        # 場所の検証
        location = getattr(content, 'location', '不明')
        logger.info(f"  場所: {location}")
        
        # トランスクリプトの検証
        transcripts = getattr(content, 'transcripts', [])
        logger.info(f"  台詞数: {len(transcripts)}")
        
        for j, transcript in enumerate(transcripts[:3]):  # 最初の3つの台詞のみ表示
            logger.info(f"    台詞 {j+1}: {transcript.get('text', '')}")
        
        # 合格基準
        if scenes_count == 0 and duration > 0:
            logger.warning(f"  検証失敗: シーン数が0ですが、動画の長さが{duration}秒あります")
            success = False
        
        if duration == 0 and scenes_count > 0:
            logger.warning(f"  検証失敗: 動画の長さが0秒ですが、シーン数が{scenes_count}あります")
            success = False
    
    return success

def test_scenario_writer():
    """ScenarioWriterのテスト - 主題の特定とシナリオ生成"""
    logger.info("\nScenarioWriterテスト開始")
    
    # ContentCrawlerでデータを取得
    test_dir = "test_data"
    crawler = ContentCrawler()
    contents = crawler.crawl(test_dir)
    
    if not contents:
        logger.error("コンテンツが取得できませんでした")
        return False
    
    # キーポイントあり/なしの両方をテスト
    test_cases = [
        {
            "name": "キーポイントあり",
            "scenario_input": ScenarioInput(
                title="冬の大山登山記録",
                target_audience="一般視聴者",
                style="ドキュメンタリー",
                main_message="冬山登山の準備と挑戦の記録",
                desired_length=180,
                key_points=["登山の動機と目的", "冬山の装備と準備", "山頂への挑戦"],
                keywords=["大山", "冬山", "登山", "健康維持", "雪山装備", "氷点下"]
            )
        },
        {
            "name": "キーポイントなし",
            "scenario_input": ScenarioInput(
                title="バスの旅",
                target_audience="一般視聴者",
                style="カジュアル",
                main_message="バスの旅の楽しさを伝える",
                desired_length=60,
                key_points=[],
                keywords=["バス", "旅行", "車窓"]
            )
        }
    ]
    
    success = True
    
    for test_case in test_cases:
        name = test_case["name"]
        scenario_input = test_case["scenario_input"]
        
        logger.info(f"\nテストケース: {name}")
        logger.info(f"  タイトル: {scenario_input.title}")
        logger.info(f"  キーポイント: {scenario_input.key_points}")
        
        # ScenarioWriterの実行
        writer = ScenarioWriter()
        try:
            scenario_json = writer.generate(contents, scenario_input)
            scenario = json.loads(scenario_json)
            
            # 主題の検証
            theme = writer.concept_data.get("theme", "不明")
            logger.info(f"  特定された主題: {theme}")
            
            # 台詞の検証
            transcripts = writer.concept_data.get("transcripts", [])
            logger.info(f"  取得された台詞数: {len(transcripts)}")
            
            # シナリオの検証
            sections = scenario.get("sections", [])
            logger.info(f"  生成されたセクション数: {len(sections)}")
            
            # セクションの詳細を表示
            for i, section in enumerate(sections):
                logger.info(f"    セクション {i+1}: {section.get('name')} - {section.get('description')[:30]}...")
            
            # キーポイントとセクション数の関係を検証
            expected_sections = len(scenario_input.key_points) + 2  # イントロとアウトロを加算
            if len(scenario_input.key_points) == 0:
                expected_sections = 2  # イントロとアウトロのみ
                
            if len(sections) != expected_sections:
                logger.warning(f"  検証失敗: セクション数が{len(sections)}ですが、予想は{expected_sections}でした")
                success = False
            
            # 少なくとも一つの台詞が抽出されているかを検証
            if not transcripts:
                logger.warning("  検証失敗: 台詞が抽出されていません")
                success = False
                
        except Exception as e:
            logger.error(f"  エラー発生: {e}")
            success = False
    
    return success

def main():
    """メインテスト関数"""
    logger.info("コンテンツとシナリオテスト開始")
    
    # ContentCrawlerのテスト
    crawler_success = test_content_crawler()
    logger.info(f"ContentCrawlerテスト結果: {'成功' if crawler_success else '失敗'}")
    
    # ScenarioWriterのテスト
    writer_success = test_scenario_writer()
    logger.info(f"ScenarioWriterテスト結果: {'成功' if writer_success else '失敗'}")
    
    # 総合結果
    overall_success = crawler_success and writer_success
    logger.info(f"テスト総合結果: {'成功' if overall_success else '失敗'}")
    
    return 0 if overall_success else 1

if __name__ == "__main__":
    sys.exit(main()) 