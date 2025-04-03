"""繧ｷ繝ｼ繝ｳ驕ｸ謚槭Δ繧ｸ繝･繝ｼ繝ｫ"""

from typing import List, Dict, Any
import json
import time
from .api_client import GeminiClient
import os

class SceneSelector:
    def __init__(self, api_client: GeminiClient):
        """繧ｷ繝ｼ繝ｳ驕ｸ謚槫勣縺ｮ蛻晄悄蛹�"""
        self.api_client = api_client
        self.max_retries = 3
        self.retry_delay = 1.0  # 遘�

    def select(self, contents: List[Dict[str, Any]], scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """繧ｷ繝翫Μ繧ｪ縺ｫ蝓ｺ縺･縺�縺ｦ繧ｷ繝ｼ繝ｳ繧帝∈謚�"""
        try:
            # 繧ｷ繝ｼ繝ｳ繧帝∈謚�
            selected_scenes = self._select_scenes_with_ai(contents, scenario)
            return selected_scenes
        except Exception as e:
            print(f"隴ｦ蜻�: 繧ｷ繝ｼ繝ｳ驕ｸ謚樔ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
            return []

    def _select_scenes_with_ai(self, contents: List[Dict[str, Any]], 
                              scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """逕滓�植I繧剃ｽｿ逕ｨ縺励※繧ｷ繝ｼ繝ｳ繧帝∈謚�"""
        # 繧ｳ繝ｳ繝�繝ｳ繝�縺ｮ讎りｦ√ｒ貅門ｙ
        content_summary = self._format_contents_summary(contents)
        
        # 繝励Ο繝ｳ繝励ヨ繝�繝ｳ繝励Ξ繝ｼ繝�
        prompt = f"""莉･荳九�ｮ繧ｷ繝翫Μ繧ｪ縺ｨ繧ｳ繝ｳ繝�繝ｳ繝�縺ｫ蝓ｺ縺･縺�縺ｦ縲∵怙驕ｩ縺ｪ繧ｷ繝ｼ繝ｳ繧帝∈謚槭＠縺ｦ縺上□縺輔＞�ｼ�

繧ｷ繝翫Μ繧ｪ:
{json.dumps(scenario, ensure_ascii=False, indent=2)}

蛻ｩ逕ｨ蜿ｯ閭ｽ縺ｪ繧ｳ繝ｳ繝�繝ｳ繝�:
{content_summary}

莉･荳九�ｮ蠖｢蠑上〒蜃ｺ蜉帙＠縺ｦ縺上□縺輔＞�ｼ�
{{
    "selected_scenes": [
        {{
            "content_id": "繧ｳ繝ｳ繝�繝ｳ繝ИD",
            "scene_index": 繧ｷ繝ｼ繝ｳ逡ｪ蜿ｷ,
            "start_time": 髢句ｧ区凾髢難ｼ育ｧ抵ｼ�,
            "end_time": 邨ゆｺ�譎る俣�ｼ育ｧ抵ｼ�,
            "reason": "驕ｸ謚樒炊逕ｱ",
            "section_id": "蟇ｾ蠢懊☆繧九そ繧ｯ繧ｷ繝ｧ繝ｳID"
        }},
        ...
    ]
}}"""

        # 繝励Ο繝ｳ繝励ヨ繧偵Ο繧ｰ繝輔ぃ繧､繝ｫ縺ｫ菫晏ｭ�
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'scene_selection_prompt.txt')
        with open(log_path, 'w', encoding='utf-8-sig') as f:
            f.write(prompt)
        print(f"繧ｷ繝ｼ繝ｳ驕ｸ謚槭�励Ο繝ｳ繝励ヨ繧剃ｿ晏ｭ倥＠縺ｾ縺励◆: {log_path}")

        # 逕滓�植I縺ｫ繝ｪ繧ｯ繧ｨ繧ｹ繝�
        response = self.api_client.text_analysis(prompt)
        
        try:
            # 繝ｬ繧ｹ繝昴Φ繧ｹ繧偵ヱ繝ｼ繧ｹ
            result = json.loads(response)
            
            # 驕ｸ謚槭＆繧後◆繧ｷ繝ｼ繝ｳ繧貞叙蠕�
            selected_scenes = []
            for scene_info in result.get("selected_scenes", []):
                content_id = scene_info.get("content_id")
                scene_index = scene_info.get("scene_index")
                
                # 蟇ｾ蠢懊☆繧九さ繝ｳ繝�繝ｳ繝�縺ｨ繧ｷ繝ｼ繝ｳ繧呈爾縺�
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
            print(f"隴ｦ蜻�: 繧ｷ繝ｼ繝ｳ驕ｸ謚樒ｵ先棡縺ｮ蜃ｦ逅�荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
            return []

    def _format_contents_summary(self, contents: List[Dict[str, Any]]) -> str:
        """繧ｳ繝ｳ繝�繝ｳ繝�縺ｮ讎りｦ√ｒ繝輔か繝ｼ繝槭ャ繝�"""
        summary = []
        for content in contents:
            content_summary = f"""
繧ｳ繝ｳ繝�繝ｳ繝ИD: {content['content_id']}
邱丞�咲函譎る俣: {content['total_duration']}遘�
繧ｷ繝ｼ繝ｳ謨ｰ: {len(content.get('scenes', []))}

繧ｷ繝ｼ繝ｳ荳隕ｧ:
"""
            for i, scene in enumerate(content.get('scenes', [])):
                scene_summary = f"""
繧ｷ繝ｼ繝ｳ {i}:
- 髢句ｧ区凾髢�: {scene.get('start_time', 0)}遘�
- 邨ゆｺ�譎る俣: {scene.get('end_time', 0)}遘�
- 繝医ヴ繝�繧ｯ: {', '.join(scene.get('topics', []))}
- 繝医Λ繝ｳ繧ｹ繧ｯ繝ｪ繝励ヨ: {scene.get('transcript', '')[:100]}...
"""
                content_summary += scene_summary
            
            summary.append(content_summary)
        return '\n'.join(summary)
