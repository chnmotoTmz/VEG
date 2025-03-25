import sys
import os
import json
import logging
import argparse
from pathlib import Path

# プロジェクトのルートディレクトリを追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.insert(0, project_root)

from srt_scene_tools.utils import ContentCrawler, Scene
from srt_scene_tools.editing_agent import EditingAgent
from srt_scene_tools.scenario_writer import ScenarioWriter, ScenarioInput

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def format_timecode(seconds):
    """秒数をタイムコード形式（HH:MM:SS.mmm）に変換する"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def main():
    print("テスト実行開始")
    
    # テストデータディレクトリの設定
    content_dir = "test_data"
    scenario_file = "scenario.json"
    
    # ContentCrawlerの初期化と実行
    crawler = ContentCrawler()
    contents = crawler.crawl(content_dir)
    print(f"読み込んだコンテンツ数: {len(contents)}")
    
    # 各コンテンツの基本情報を表示
    for i, content in enumerate(contents):
        print(f"\nコンテンツ {i+1}:")
        print(f"  タイトル: {getattr(content, 'title', 'タイトルなし')}")
        print(f"  シーン数: {len(getattr(content, 'scenes', []))}")
        print(f"  総時間: {getattr(content, 'total_duration', 0)}秒")
        print(f"  トピック: {', '.join(getattr(content, 'topics', []))}")
        print(f"  場所: {getattr(content, 'location', '不明')}")
        
        # シーンの詳細表示
        scenes = getattr(content, 'scenes', [])
        for j, scene in enumerate(scenes[:3]):  # 最初の3シーンのみ表示
            print(f"    シーン {j}:")
            print(f"      開始時間: {scene.get('start', 0)}秒")
            print(f"      終了時間: {scene.get('end', 0)}秒")
            print(f"      トランスクリプト: {scene.get('transcript', '')[:50]}..." if scene.get('transcript') else "      トランスクリプトなし")
    
    # シナリオ読み込み
    try:
        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        # ScenarioInputの作成
        scenario_input = ScenarioInput(
            title=scenario_data.get('title', ''),
            target_audience=scenario_data.get('target_audience', ''),
            style=scenario_data.get('style', ''),
            main_message=scenario_data.get('main_message', ''),
            desired_length=scenario_data.get('desired_length', 0),
            key_points=scenario_data.get('key_points', []),
            keywords=scenario_data.get('keywords', []),
        )
        
        # シナリオ生成
        writer = ScenarioWriter()
        scenario_json = writer.generate(contents, scenario_input)
        print("\nシナリオ生成結果:")
        scenario = json.loads(scenario_json)
        print(f"  タイトル: {scenario.get('title', '')}")
        print(f"  セクション数: {len(scenario.get('sections', []))}")
        
        # シーンマッチング
        query = "登山 冬山 大山"
        agent = EditingAgent()
        matches = agent.match_scenes(contents, query)
        print(f"\nクエリ「{query}」に対するマッチング結果:")
        print(f"  マッチ数: {len(matches)}")
        
        # マッチング結果の詳細表示
        for i, match in enumerate(matches[:5]):  # 最初の5つのマッチのみ表示
            print(f"  マッチ {i+1}:")
            print(f"    類似度: {match.similarity}")
            print(f"    テキスト: {match.text[:50]}..." if match.text else "    テキストなし")
            print(f"    ビデオパス: {match.video_path}")
            if hasattr(match, 'preview_path') and match.preview_path:
                print(f"    プレビューパス: {match.preview_path}")
            else:
                print("    プレビューパスなし")
        
    except Exception as e:
        print(f"エラー発生: {e}")
    
    print("\nテスト実行完了")

if __name__ == "__main__":
    main() 