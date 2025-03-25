"""メイン処理フロー"""

import argparse
import json
import os
from typing import Dict, Any

from .content_crawler import ContentCrawler
from .concept_generator import ConceptGenerator
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
        self.concept_generator = ConceptGenerator(api_client=self.api_client)
        self.scene_selector = SceneSelector(api_client=self.api_client)
        self.edl_generator = EDLGenerator()
        self.srt_generator = SRTGenerator()

    def process(self):
        """メイン処理フローを実行"""
        try:
            # コンテンツを探索
            print("映像コンテンツを探索中...")
            contents = self.content_crawler.crawl(self.config['input_dir'])
            
            # コンセプトを生成
            print("コンセプトを生成中...")
            concept = self.concept_generator.generate(contents)
            print(f"生成されたコンセプト: {concept}")
            
            # シナリオプロンプトを生成
            print("シナリオプロンプトを生成中...")
            scenario_prompt = self.concept_generator.generate_scenario_prompt(concept)
            
            # シナリオプロンプトを保存
            os.makedirs(self.config['output_dir'], exist_ok=True)
            with open(os.path.join(self.config['output_dir'], 'scenario_prompt.txt'), 
                     'w', encoding='utf-8-sig') as f:
                f.write(scenario_prompt)
            
            # シナリオを読み込む
            scenario_path = self.config.get('scenario_path', self.config.get('scenario_file'))
            with open(scenario_path, 'r', encoding='utf-8-sig') as f:
                scenario = json.load(f)
            
            # シーンを選択
            print("シーンを選択中...")
            selected_scenes = self.scene_selector.select(contents, scenario)
            
            # EDLファイルを生成
            print("EDLファイルを生成中...")
            edl_output_path = os.path.join(self.config['output_dir'], 'output.edl')
            self.edl_generator.generate(selected_scenes, edl_output_path)
            
            # SRTファイルを生成
            print("SRTファイルを生成中...")
            srt_output_path = os.path.join(self.config['output_dir'], 'output.srt')
            self.srt_generator.generate(selected_scenes, srt_output_path)
            
            print("処理が完了しました。")
            
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")
            raise
