"""SRTファイル生成モジュール"""

from typing import List, Dict, Any
import os

class SRTGenerator:
    def __init__(self):
        pass

    def generate(self, scenes: List[Dict[str, Any]], output_path: str) -> None:
        """SRTファイルを生成"""
        # 出力ディレクトリの作成
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # SRTファイルの生成
        srt_lines = []
        
        # シーンの処理
        for i, scene in enumerate(scenes, 1):
            try:
                # タイムコードの変換
                start_time = self._seconds_to_srt_time(scene['start_time'])
                end_time = self._seconds_to_srt_time(scene['end_time'])
                
                # SRTエントリの作成
                entry = self._create_srt_entry(
                    i, start_time, end_time, scene.get('transcript', '')
                )
                srt_lines.append(entry)
            except Exception as e:
                print(f"警告: シーン {i} の処理中にエラーが発生しました: {str(e)}")
                continue
        
        # ファイルの書き込み
        with open(output_path, 'w', encoding='utf-8-sig', newline='\n') as f:
            f.write('\n'.join(srt_lines))

    def _create_srt_entry(self, index: int, start_time: str,
                         end_time: str, transcript: str) -> str:
        """SRTエントリを生成"""
        return f"{index}\n{start_time} --> {end_time}\n{transcript}\n"

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """秒数をSRT形式のタイムコードに変換"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
