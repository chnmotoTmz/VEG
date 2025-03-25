"""シーン選択モジュール"""

from typing import List, Dict, Any
import json
import time
from .api_client import GeminiClient

class SceneSelector:
    def __init__(self, api_client: GeminiClient):
        """シーン選択器の初期化"""
        self.api_client = api_client
        self.max_retries = 3
        self.retry_delay = 1.0  # 秒

    def select(self, contents: List[Dict[str, Any]], scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """シナリオに基づいてシーンを選択"""
        try:
            # シーンを選択
            selected_scenes = self._select_scenes_with_ai(contents, scenario)
            return selected_scenes
        except Exception as e:
            print(f"警告: シーン選択中にエラーが発生しました: {str(e)}")
            return []

    def _select_scenes_with_ai(self, contents: List[Dict[str, Any]], 
                              scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成AIを使用してシーンを選択"""
        # コンテンツの概要を準備
        content_summary = self._format_contents_summary(contents)
        
        # プロンプトテンプレート
        prompt = f"""以下のシナリオとコンテンツに基づいて、最適なシーンを選択してください：

シナリオ:
{json.dumps(scenario, ensure_ascii=False, indent=2)}

利用可能なコンテンツ:
{content_summary}

以下の形式で出力してください：
{{
    "selected_scenes": [
        {{
            "content_id": "コンテンツID",
            "scene_index": シーン番号,
            "start_time": 開始時間（秒）,
            "end_time": 終了時間（秒）,
            "reason": "選択理由",
            "section_id": "対応するセクションID"
        }},
        ...
    ]
}}"""

        # 生成AIにリクエスト
        response = self.api_client.text_analysis(prompt)
        
        try:
            # レスポンスをパース
            result = json.loads(response)
            
            # 選択されたシーンを取得
            selected_scenes = []
            for scene_info in result.get("selected_scenes", []):
                content_id = scene_info.get("content_id")
                scene_index = scene_info.get("scene_index")
                
                # 対応するコンテンツとシーンを探す
                for content in contents:
                    if content["content_id"] == content_id:
                        if scene_index >= 0 and scene_index < len(content.get('scenes', [])):
                            scene = content["scenes"][scene_index]
                            selected_scenes.append({
                                "content_id": content_id,
                                "scene_index": scene_index,
                                "start_time": scene_info.get("start_time", scene.get("start_time", 0)),
                                "end_time": scene_info.get("end_time", scene.get("end_time", 0)),
                                "reason": scene_info.get("reason", ""),
                                "section_id": scene_info.get("section_id", ""),
                                "transcript": scene.get("transcript", ""),
                                "topics": scene.get("topics", []),
                                "effects": scene.get("effects", [])
                            })
                        break
            
            return selected_scenes
            
        except Exception as e:
            print(f"警告: シーン選択結果の処理中にエラーが発生しました: {str(e)}")
            return []

    def _format_contents_summary(self, contents: List[Dict[str, Any]]) -> str:
        """コンテンツの概要をフォーマット"""
        summary = []
        for content in contents:
            content_summary = f"""
コンテンツID: {content['content_id']}
総再生時間: {content['total_duration']}秒
シーン数: {len(content.get('scenes', []))}

シーン一覧:
"""
            for i, scene in enumerate(content.get('scenes', [])):
                scene_summary = f"""
シーン {i}:
- 開始時間: {scene.get('start_time', 0)}秒
- 終了時間: {scene.get('end_time', 0)}秒
- トピック: {', '.join(scene.get('topics', []))}
- トランスクリプト: {scene.get('transcript', '')[:100]}...
"""
                content_summary += scene_summary
            
            summary.append(content_summary)
        return '\n'.join(summary)
