"""メイン処理フロー"""

import argparse
import json
import os
from typing import Dict, Any, List

from .content_crawler import ContentCrawler
from .scenario_writer import ScenarioWriter
from .scene_selector import SceneSelector
from .edl_generator import EDLGenerator
from .srt_generator import SRTGenerator
from .api_client import GeminiClient
import dotenv

dotenv.load_dotenv()

class VideoEditAgent:
    def __init__(self, config: Dict[str, Any]):
        """ビデオ編集エージェントの初期化"""
        self.config = config

        # API クライアントを初期化
        self.api_client = GeminiClient()

        # 各コンポーネントを初期化
        self.content_crawler = ContentCrawler()
        self.scenario_writer = ScenarioWriter(api_client=self.api_client)
        self.scene_selector = SceneSelector(api_client=self.api_client)
        self.edl_generator = EDLGenerator()
        self.srt_generator = SRTGenerator()

    def analyze_contents(self):
        """コンテンツ分析フェーズ"""
        try:
            # コンテンツを探索
            print("映像コンテンツを探索中...")
            contents = self.content_crawler.crawl(self.config['input_dir'])

            # コンセプトを生成
            print("コンセプトを生成中...")
            concept = self.scenario_writer.generate_concept(contents)
            print(f"生成されたコンセプト: {concept['concept']}")

            # コンセプトを保存
            os.makedirs(self.config['output_dir'], exist_ok=True)
            concept_path = os.path.join(self.config['output_dir'], 'concept.json')
            self.scenario_writer.save_concept(concept, concept_path)

            # シナリオテンプレートの作成
            print("シナリオテンプレートを生成中...")
            template = self.scenario_writer.generate_template(concept)
            template_path = os.path.join(self.config['output_dir'], 'scenario_template.json')
            self.scenario_writer.save_template(template, template_path)

            print(f"コンテンツ分析が完了しました")
            return {
                'contents': contents,
                'concept': concept,
                'template': template
            }
        except Exception as e:
            print(f"コンテンツ分析エラー: {e}")
            raise
    
    def select_scenes(self, scenario_path: str):
        """シーン選択フェーズ"""
        try:
            # シナリオを読み込み
            print("シナリオを読み込み中...")
            with open(scenario_path, 'r', encoding='utf-8') as f:
                scenario = json.load(f)
            
            # コンテンツを読み込み
            print("コンテンツを読み込み中...")
            contents_path = os.path.join(self.config['output_dir'], 'contents.json')
            with open(contents_path, 'r', encoding='utf-8') as f:
                contents = json.load(f)
            
            # シーンを選択
            print("シーンを選択中...")
            selected = self.scene_selector.select(contents, scenario)
            print(f"選択されたシーン数: {len(selected['scenes'])}")
            
            # 選択結果を保存
            selected_path = os.path.join(self.config['output_dir'], 'selected.json')
            with open(selected_path, 'w', encoding='utf-8') as f:
                json.dump(selected, f, indent=2, ensure_ascii=False)
            
            print(f"シーン選択が完了しました")
            return selected
        except Exception as e:
            print(f"シーン選択エラー: {e}")
            raise
    
    def generate_outputs(self, selected_path: str):
        """出力生成フェーズ"""
        try:
            # 選択結果を読み込み
            print("選択結果を読み込み中...")
            with open(selected_path, 'r', encoding='utf-8') as f:
                selected = json.load(f)
            
            # EDLファイルを生成
            print("EDLファイルを生成中...")
            edl_path = os.path.join(self.config['output_dir'], 'output.edl')
            self.edl_generator.generate(selected, edl_path)
            
            # SRTファイルを生成
            print("SRTファイルを生成中...")
            srt_path = os.path.join(self.config['output_dir'], 'output.srt')
            self.srt_generator.generate(selected, srt_path)
            
            print(f"出力生成が完了しました")
            return {
                'edl_path': edl_path,
                'srt_path': srt_path
            }
        except Exception as e:
            print(f"出力生成エラー: {e}")
            raise
    
    def run(self):
        """すべてのフェーズを実行"""
        print("ビデオ編集エージェントを開始します...")
        
        # コンテンツ分析フェーズ
        analysis_result = self.analyze_contents()
        
        # シナリオ作成（ユーザーが手動で行う）
        scenario_path = os.path.join(self.config['output_dir'], 'scenario.json')
        print(f"シナリオを {scenario_path} に作成してください")
        input("シナリオが作成されたらEnterキーを押してください...")
        
        # シーン選択フェーズ
        selected = self.select_scenes(scenario_path)
        selected_path = os.path.join(self.config['output_dir'], 'selected.json')
        
        # 出力生成フェーズ
        outputs = self.generate_outputs(selected_path)
        
        print("ビデオ編集エージェントが完了しました")
        print(f"EDLファイル: {outputs['edl_path']}")
        print(f"SRTファイル: {outputs['srt_path']}")
        
        return outputs


def main():
    """コマンドライン実行エントリーポイント"""
    parser = argparse.ArgumentParser(description='ビデオ編集支援ツール')
    parser.add_argument('--config', '-c', required=True, help='設定ファイルのパス')
    args = parser.parse_args()
    
    # 設定を読み込み
    with open(args.config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # エージェントを作成して実行
    agent = VideoEditAgent(config)
    agent.run()


if __name__ == '__main__':
    main() 