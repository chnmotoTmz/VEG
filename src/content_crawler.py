"""コンテンツ探索モジュール"""

import os
import json
from typing import List, Dict, Any

class ContentCrawler:
    def __init__(self):
        pass

    def crawl(self, input_dir: str) -> List[Dict[str, Any]]:
        """指定されたディレクトリからコンテンツを探索"""
        contents = []
        
        try:
            # ディレクトリ内のvideo_nodes_で始まるディレクトリを探索
            for item in os.listdir(input_dir):
                item_path = os.path.join(input_dir, item)
                if os.path.isdir(item_path) and item.startswith('video_nodes_'):
                    content = self._load_content(item_path)
                    if content:
                        contents.append(content)
        except Exception as e:
            print(f"警告: コンテンツの探索中にエラーが発生しました: {str(e)}")
        
        return contents

    def _load_content(self, content_dir: str) -> Dict[str, Any]:
        """コンテンツディレクトリからデータを読み込み"""
        try:
            # nodes.jsonファイルのパスを構築
            nodes_file = os.path.join(content_dir, 'nodes.json')
            
            if not os.path.exists(nodes_file):
                print(f"警告: {nodes_file} が見つかりません")
                return None
            
            # ファイルを読み込み
            with open(nodes_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            # コンテンツIDを設定
            content_id = os.path.basename(content_dir)
            
            # シーン情報を整形
            scenes = []
            for scene in data.get('scenes', []):
                # トランスクリプトを結合
                transcript = ''
                for t in scene.get('transcripts', []):
                    transcript += t.get('text', '') + ' '
                transcript = transcript.strip()
                
                # シーン情報を作成
                scene_info = {
                    'start_time': float(scene.get('start', 0)),
                    'end_time': float(scene.get('end', 0)),
                    'transcript': transcript,
                    'keywords': scene.get('context_analysis', {}).get('activity', []),
                    'topics': data.get('summary', {}).get('topics', [])
                }
                scenes.append(scene_info)
            
            # シーンを時間順にソート
            scenes.sort(key=lambda x: x['start_time'])
            
            return {
                'content_id': content_id,
                'scenes': scenes,
                'total_duration': float(data.get('metadata', {}).get('duration', 0))
            }
            
        except Exception as e:
            print(f"警告: {content_dir} の読み込み中にエラーが発生しました: {str(e)}")
            return None
