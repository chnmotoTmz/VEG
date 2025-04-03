"""繧ｷ繝翫Μ繧ｪ菴懈�先髪謠ｴ繝｢繧ｸ繝･繝ｼ繝ｫ"""

from typing import Dict, Any, List
import json
from .api_client import GeminiClient
import os

class ScenarioWriter:
    def __init__(self, api_client: GeminiClient):
        """繧ｷ繝翫Μ繧ｪ繝ｩ繧､繧ｿ繝ｼ縺ｮ蛻晄悄蛹�"""
        self.api_client = api_client

    def generate_concept(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """繧ｳ繝ｳ繝�繝ｳ繝�縺九ｉ繧ｿ繧､繝医Ν縺ｨ繧ｳ繝ｳ繧ｻ繝励ヨ繧堤函謌�"""
        prompt = f"""莉･荳九�ｮ譏蜒上さ繝ｳ繝�繝ｳ繝�縺九ｉ縲∽ｽ懷刀縺ｮ繧ｿ繧､繝医Ν縺ｨ繧ｳ繝ｳ繧ｻ繝励ヨ繧堤函謌舌＠縺ｦ縺上□縺輔＞�ｼ�

繧ｳ繝ｳ繝�繝ｳ繝�讎りｦ�:
{self._format_contents_summary(contents)}

莉･荳九�ｮ蠖｢蠑上〒JSON蜃ｺ蜉帙＠縺ｦ縺上□縺輔＞�ｼ�
{{
    "title": "菴懷刀繧ｿ繧､繝医Ν",
    "concept": "菴懷刀繧ｳ繝ｳ繧ｻ繝励ヨ�ｼ�200譁�蟄嶺ｻ･蜀��ｼ�",
    "themes": ["繝�繝ｼ繝�1", "繝�繝ｼ繝�2", ...],
    "suggested_duration": "謗ｨ螂ｨ邱乗凾髢難ｼ亥���ｼ�",
    "key_scenes": ["驥崎ｦ√↑繧ｷ繝ｼ繝ｳ1", "驥崎ｦ√↑繧ｷ繝ｼ繝ｳ2", ...]
}}"""

        # 繝励Ο繝ｳ繝励ヨ繧偵Ο繧ｰ繝輔ぃ繧､繝ｫ縺ｫ菫晏ｭ�
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'concept_prompt.txt')
        with open(log_path, 'w', encoding='utf-8-sig') as f:
            f.write(prompt)
        print(f"繝励Ο繝ｳ繝励ヨ繧剃ｿ晏ｭ倥＠縺ｾ縺励◆: {log_path}")

        response = self.api_client.text_analysis(prompt)
        
        try:
            result = json.loads(response)
            return result
        except Exception as e:
            print(f"隴ｦ蜻�: 繧ｳ繝ｳ繧ｻ繝励ヨ逕滓�蝉ｸｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
            return {
                "title": "繧ｿ繧､繝医Ν譛ｪ險ｭ螳�",
                "concept": "繧ｳ繝ｳ繝�繝ｳ繝�縺ｮ閾ｪ蜍募��譫千ｵ先棡",
                "themes": [],
                "suggested_duration": "5",
                "key_scenes": []
            }

    def _format_contents_summary(self, contents: List[Dict[str, Any]]) -> str:
        """繧ｳ繝ｳ繝�繝ｳ繝�縺ｮ讎りｦ√ｒ繝輔か繝ｼ繝槭ャ繝�"""
        summary = []
        for content in contents:
            # 繧ｷ繝ｼ繝ｳ繝ｪ繧ｹ繝医′蟄伜惠縺吶ｋ縺狗｢ｺ隱阪＠縲∫ｩｺ縺ｮ蝣ｴ蜷医�ｯ螳牙�ｨ縺ｫ蜃ｦ逅�
            scenes = content.get('scenes', [])
            
            # 繝医ヴ繝�繧ｯ縺ｮ蜿門ｾ励ｒ螳牙�ｨ縺ｫ陦後≧
            topics = []
            if scenes and len(scenes) > 0:
                topics = scenes[0].get('topics', [])
            
            content_summary = f"""
繧ｳ繝ｳ繝�繝ｳ繝ИD: {content.get('content_id', 'unknown')}
邱丞�咲函譎る俣: {content.get('total_duration', 0)}遘�
繧ｷ繝ｼ繝ｳ謨ｰ: {len(scenes)}
荳ｻ縺ｪ繝医ヴ繝�繧ｯ: {', '.join(topics)}
"""
            summary.append(content_summary)
        return '\n'.join(summary)

    def save_concept(self, concept: Dict[str, Any], output_path: str) -> None:
        """逕滓�舌＆繧後◆繧ｳ繝ｳ繧ｻ繝励ヨ繧剃ｿ晏ｭ�"""
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(concept, f, ensure_ascii=False, indent=2)

    def load_scenario(self, scenario_path: str) -> Dict[str, Any]:
        """繧ｷ繝翫Μ繧ｪJSON繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ繧"""
        with open(scenario_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    def create_scenario_template(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """繧ｳ繝ｳ繧ｻ繝励ヨ縺九ｉ繧ｷ繝翫Μ繧ｪ繝�繝ｳ繝励Ξ繝ｼ繝医ｒ菴懈��"""
        template = {
            "title": concept.get("title", ""),
            "concept": concept.get("concept", ""),
            "themes": concept.get("themes", []),
            "total_duration": 300,  # 5蛻�
            "sections": [
                {
                    "section_id": "intro",
                    "type": "intro",
                    "title": "繧､繝ｳ繝医Ο繝繧ｯ繧ｷ繝ｧ繝ｳ",
                    "description": "菴懷刀縺ｮ蟆主�･驛ｨ蛻�",
                    "key_messages": [
                        "菴懷刀縺ｮ逶ｮ逧�縺ｨ讎りｦ�",
                        "隕冶�ｴ閠�縺ｸ縺ｮ譛溷ｾ�",
                        "荳ｻ隕√↑隕九←縺薙ｍ"
                    ],
                    "duration": 30,
                    "content_ids": [],
                    "effects": [
                        {
                            "type": "fade_in",
                            "duration": 2.0,
                            "description": "繧ｿ繧､繝医Ν繝輔ぉ繝ｼ繝峨う繝ｳ"
                        },
                        {
                            "type": "text_overlay",
                            "duration": 5.0,
                            "description": "荳ｻ隕√ユ繝ｼ繝槭�ｮ陦ｨ遉ｺ"
                        }
                    ],
                    "scene_requirements": {
                        "min_duration": 5.0,
                        "max_duration": 15.0,
                        "required_elements": [
                            "繧ｿ繧､繝医Ν繧ｷ繝ｼ繝ｳ",
                            "蟆主�･繧ｷ繝ｼ繝ｳ",
                            "繝�繝ｼ繝樊署遉ｺ"
                        ]
                    }
                },
                {
                    "section_id": "main_1",
                    "type": "main",
                    "title": "貅門ｙ縺ｨ蜃ｺ逋ｺ",
                    "description": "逋ｻ螻ｱ縺ｮ貅門ｙ縺ｨ蜃ｺ逋ｺ繧ｷ繝ｼ繝ｳ",
                    "key_messages": [
                        "貅門ｙ縺ｮ迥ｶ豕�",
                        "蜃ｺ逋ｺ譎ゅ�ｮ豌玲戟縺｡",
                        "繧｢繧ｯ繧ｻ繧ｹ譁ｹ豕�"
                    ],
                    "duration": 60,
                    "content_ids": [],
                    "effects": [
                        {
                            "type": "transition",
                            "duration": 1.0,
                            "description": "繧ｷ繝ｼ繝ｳ蛻�繧頑崛縺�"
                        }
                    ],
                    "scene_requirements": {
                        "min_duration": 10.0,
                        "max_duration": 20.0,
                        "required_elements": [
                            "貅門ｙ繧ｷ繝ｼ繝ｳ",
                            "莠､騾壹い繧ｯ繧ｻ繧ｹ",
                            "蜃ｺ逋ｺ繧ｷ繝ｼ繝ｳ"
                        ]
                    }
                },
                {
                    "section_id": "main_2",
                    "type": "main",
                    "title": "逋ｻ螻ｱ驕薙〒縺ｮ菴馴ｨ�",
                    "description": "逋ｻ螻ｱ驕薙〒縺ｮ讒倥�縺ｪ菴馴ｨ�",
                    "key_messages": [
                        "驕謎ｸｭ縺ｮ讒伜ｭ�",
                        "蝗ｰ髮｣縺ｪ迥ｶ豕�",
                        "閾ｪ辟ｶ縺ｮ鄒弱＠縺�"
                    ],
                    "duration": 60,
                    "content_ids": [],
                    "effects": [
                        {
                            "type": "transition",
                            "duration": 1.0,
                            "description": "繧ｷ繝ｼ繝ｳ蛻�繧頑崛縺�"
                        }
                    ],
                    "scene_requirements": {
                        "min_duration": 15.0,
                        "max_duration": 30.0,
                        "required_elements": [
                            "逋ｻ螻ｱ驕薙�ｮ讒伜ｭ�",
                            "閾ｪ辟ｶ縺ｮ鬚ｨ譎ｯ",
                            "蝗ｰ髮｣縺ｪ迥ｶ豕�"
                        ]
                    }
                },
                {
                    "section_id": "main_3",
                    "type": "main",
                    "title": "鬆ゆｸ翫→荳句ｱｱ",
                    "description": "鬆ゆｸ翫〒縺ｮ驕疲�先─縺ｨ荳句ｱｱ",
                    "key_messages": [
                        "鬆ゆｸ翫〒縺ｮ諢溷虚",
                        "荳句ｱｱ縺ｮ讒伜ｭ�",
                        "謖ｯ繧願ｿ斐ｊ"
                    ],
                    "duration": 60,
                    "content_ids": [],
                    "effects": [
                        {
                            "type": "transition",
                            "duration": 1.0,
                            "description": "繧ｷ繝ｼ繝ｳ蛻�繧頑崛縺�"
                        }
                    ],
                    "scene_requirements": {
                        "min_duration": 15.0,
                        "max_duration": 30.0,
                        "required_elements": [
                            "鬆ゆｸ翫す繝ｼ繝ｳ",
                            "荳句ｱｱ繧ｷ繝ｼ繝ｳ",
                            "謖ｯ繧願ｿ斐ｊ"
                        ]
                    }
                },
                {
                    "section_id": "outro",
                    "type": "outro",
                    "title": "繧ｨ繝ｳ繝�繧｣繝ｳ繧ｰ",
                    "description": "菴懷刀縺ｮ縺ｾ縺ｨ繧√→謖ｯ繧願ｿ斐ｊ",
                    "key_messages": [
                        "菴馴ｨ薙�ｮ邱乗峡",
                        "蟄ｦ繧薙□縺薙→",
                        "莉雁ｾ後�ｮ螻墓悍"
                    ],
                    "duration": 30,
                    "content_ids": [],
                    "effects": [
                        {
                            "type": "fade_out",
                            "duration": 3.0,
                            "description": "繧ｨ繝ｳ繝�繧｣繝ｳ繧ｰ繝輔ぉ繝ｼ繝峨い繧ｦ繝�"
                        }
                    ],
                    "scene_requirements": {
                        "min_duration": 5.0,
                        "max_duration": 15.0,
                        "required_elements": [
                            "縺ｾ縺ｨ繧�",
                            "謖ｯ繧願ｿ斐ｊ",
                            "繧ｨ繝ｳ繝�繧｣繝ｳ繧ｰ"
                        ]
                    }
                }
            ]
        }
        return template 