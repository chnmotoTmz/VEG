"""繧ｳ繝ｳ繝�繝ｳ繝�謗｢邏｢繝｢繧ｸ繝･繝ｼ繝ｫ"""

import os
import json
from typing import List, Dict, Any

class ContentCrawler:
    def __init__(self):
        pass

    def crawl(self, input_dir: str) -> List[Dict[str, Any]]:
        """謖�螳壹＆繧後◆繝�繧｣繝ｬ繧ｯ繝医Μ縺九ｉ繧ｳ繝ｳ繝�繝ｳ繝�繧呈爾邏｢"""
        contents = []
        
        try:
            # 繝�繧｣繝ｬ繧ｯ繝医Μ蜀�縺ｮvideo_nodes_縺ｧ蟋九∪繧九ョ繧｣繝ｬ繧ｯ繝医Μ繧呈爾邏｢
            for item in os.listdir(input_dir):
                item_path = os.path.join(input_dir, item)
                if os.path.isdir(item_path) and item.startswith('video_nodes_'):
                    content = self._load_content(item_path)
                    if content:
                        contents.append(content)
        except Exception as e:
            print(f"隴ｦ蜻�: 繧ｳ繝ｳ繝�繝ｳ繝�縺ｮ謗｢邏｢荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
        
        return contents

    def _load_content(self, content_dir: str) -> Dict[str, Any]:
        """繧ｳ繝ｳ繝�繝ｳ繝�繝�繧｣繝ｬ繧ｯ繝医Μ縺九ｉ繝�繝ｼ繧ｿ繧定ｪｭ縺ｿ霎ｼ縺ｿ"""
        try:
            # nodes.json繝輔ぃ繧､繝ｫ縺ｮ繝代せ繧呈ｧ狗ｯ�
            nodes_file = os.path.join(content_dir, 'nodes.json')
            
            if not os.path.exists(nodes_file):
                print(f"隴ｦ蜻�: {nodes_file} 縺瑚ｦ九▽縺九ｊ縺ｾ縺帙ｓ")
                return None
            
            # 繝輔ぃ繧､繝ｫ繧定ｪｭ縺ｿ霎ｼ縺ｿ
            with open(nodes_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
            
            # 繧ｳ繝ｳ繝�繝ｳ繝ИD繧定ｨｭ螳�
            content_id = os.path.basename(content_dir)
            
            # 繧ｷ繝ｼ繝ｳ諠�蝣ｱ繧呈紛蠖｢
            scenes = []
            for scene in data.get('scenes', []):
                # 繝医Λ繝ｳ繧ｹ繧ｯ繝ｪ繝励ヨ繧堤ｵ仙粋
                transcript = ''
                for t in scene.get('transcripts', []):
                    transcript += t.get('text', '') + ' '
                transcript = transcript.strip()
                
                # 繧ｷ繝ｼ繝ｳ諠�蝣ｱ繧剃ｽ懈��
                scene_info = {
                    'start_time': float(scene.get('start', 0)),
                    'end_time': float(scene.get('end', 0)),
                    'transcript': transcript,
                    'keywords': scene.get('context_analysis', {}).get('activity', []),
                    'topics': data.get('summary', {}).get('topics', [])
                }
                scenes.append(scene_info)
            
            # 繧ｷ繝ｼ繝ｳ繧呈凾髢馴�縺ｫ繧ｽ繝ｼ繝�
            scenes.sort(key=lambda x: x['start_time'])
            
            return {
                'content_id': content_id,
                'scenes': scenes,
                'total_duration': float(data.get('metadata', {}).get('duration', 0))
            }
            
        except Exception as e:
            print(f"隴ｦ蜻�: {content_dir} 縺ｮ隱ｭ縺ｿ霎ｼ縺ｿ荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
            return None
