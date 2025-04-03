"""SRT繝輔ぃ繧､繝ｫ逕滓�舌Δ繧ｸ繝･繝ｼ繝ｫ"""

from typing import List, Dict, Any
import os

class SRTGenerator:
    def __init__(self):
        pass

    def generate(self, scenes: List[Dict[str, Any]], output_path: str) -> None:
        """SRT繝輔ぃ繧､繝ｫ繧堤函謌�"""
        # 蜃ｺ蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ縺ｮ菴懈��
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # SRT繝輔ぃ繧､繝ｫ縺ｮ逕滓��
        srt_lines = []
        
        # 繧ｷ繝ｼ繝ｳ縺ｮ蜃ｦ逅�
        for i, scene in enumerate(scenes, 1):
            try:
                # 繧ｿ繧､繝繧ｳ繝ｼ繝峨�ｮ螟画鋤
                start_time = self._seconds_to_srt_time(scene['start_time'])
                end_time = self._seconds_to_srt_time(scene['end_time'])
                
                # SRT繧ｨ繝ｳ繝医Μ縺ｮ菴懈��
                entry = self._create_srt_entry(
                    i, start_time, end_time, scene.get('transcript', '')
                )
                srt_lines.append(entry)
            except Exception as e:
                print(f"隴ｦ蜻�: 繧ｷ繝ｼ繝ｳ {i} 縺ｮ蜃ｦ逅�荳ｭ縺ｫ繧ｨ繝ｩ繝ｼ縺檎匱逕溘＠縺ｾ縺励◆: {str(e)}")
                continue
        
        # 繝輔ぃ繧､繝ｫ縺ｮ譖ｸ縺崎ｾｼ縺ｿ
        with open(output_path, 'w', encoding='utf-8-sig', newline='\n') as f:
            f.write('\n'.join(srt_lines))

    def _create_srt_entry(self, index: int, start_time: str,
                         end_time: str, transcript: str) -> str:
        """SRT繧ｨ繝ｳ繝医Μ繧堤函謌�"""
        return f"{index}\n{start_time} --> {end_time}\n{transcript}\n"

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """遘呈焚繧担RT蠖｢蠑上�ｮ繧ｿ繧､繝繧ｳ繝ｼ繝峨↓螟画鋤"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
