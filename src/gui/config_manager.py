"""設定管理モジュール"""

import os
import json
from tkinter import filedialog, messagebox
from typing import Optional, Callable, Dict, Any

from ..evolve_chip import EvolveChip
from ..main import VideoEditAgent

class ConfigManager:
    """設定ファイルの管理を担当するクラス"""
    
    def __init__(self, on_config_loaded: Callable):
        """
        コンストラクタ
        
        Args:
            on_config_loaded: 設定読み込み完了時のコールバック
        """
        self.config_file: Optional[str] = None
        self.agent: Optional[VideoEditAgent] = None
        self.on_config_loaded = on_config_loaded
    
    @EvolveChip
    def select_config(self) -> None:
        """設定ファイルを選択"""
        # まず入力ディレクトリを選択
        input_dir = filedialog.askdirectory(title="入力ディレクトリを選択")
        if not input_dir:
            return
            
        # 出力ディレクトリを選択
        output_dir = filedialog.askdirectory(title="出力ディレクトリを選択", 
                                          initialdir=input_dir)
        if not output_dir:
            return
            
        # 設定ファイルのパスを生成
        config_dir = os.path.dirname(input_dir)
        config_file = os.path.join(config_dir, "config.json")
        
        # 設定ファイルを作成
        config = {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "scenario_file": os.path.join(output_dir, "scenario.json"),
            "options": {
                "language": "ja",
                "timecode_format": "NDF",
                "frame_rate": 60,
                "max_scenes": 50,
                "min_scene_duration": 3.0,
                "max_scene_duration": 60.0
            }
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8-sig') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.config_file = config_file
            self.load_config()
            
            messagebox.showinfo("成功", f"設定ファイルを作成しました:\n{config_file}")
        except Exception as e:
            messagebox.showerror("エラー", f"設定ファイルの作成に失敗しました: {str(e)}")

    @EvolveChip
    def load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            with open(self.config_file, 'r', encoding='utf-8-sig') as f:
                config = json.load(f)
            self.agent = VideoEditAgent(config)
            
            # コールバックを呼び出し
            self.on_config_loaded(self.config_file, self.agent)
        except Exception as e:
            messagebox.showerror("エラー", f"設定ファイルの読み込みに失敗しました: {str(e)}") 