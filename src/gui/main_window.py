"""メインウィンドウモジュール"""

import os
import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any

from ..main import VideoEditAgent
from .config_manager import ConfigManager
from .process_tab import ProcessTab
from .scenario_tab import ScenarioTab
from .files_tab import FilesTab

class MainWindow:
    """アプリケーションのメインウィンドウを管理するクラス"""
    
    def __init__(self, root: tk.Tk):
        """
        コンストラクタ
        
        Args:
            root: Tkinterのルートウィンドウ
        """
        self.root = root
        self.root.title("SRT Scene Tools")
        self.root.geometry("800x600")
        
        # 初期状態の設定
        self.config_manager = ConfigManager(self._on_config_loaded)
        
        # 設定ファイル選択UI
        self._init_config_ui()
        
        # ノートブック（タブ）
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タブの初期化
        self.process_tab = ProcessTab(self.notebook, self._get_agent)
        self.scenario_tab = ScenarioTab(self.notebook, self._get_config)
        self.files_tab = FilesTab(self.notebook, self._get_config)
        
        # 初期状態ではボタンを無効化
        self.process_tab.update_button_states(False)
    
    def _init_config_ui(self) -> None:
        """設定ファイル選択UIの初期化"""
        config_frame = ttk.Frame(self.root)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(config_frame, text="設定ファイル:").pack(side=tk.LEFT)
        self.config_path = ttk.Label(config_frame, text="未選択")
        self.config_path.pack(side=tk.LEFT, padx=5)
        ttk.Button(config_frame, text="選択", 
                  command=self.config_manager.select_config).pack(side=tk.LEFT)
    
    def _on_config_loaded(self, config_file: str, agent: VideoEditAgent) -> None:
        """
        設定ファイル読み込み完了時のコールバック
        
        Args:
            config_file: 読み込まれた設定ファイルのパス
            agent: 初期化されたVideoEditAgentインスタンス
        """
        self.config_path.config(text=config_file)
        
        # ボタンを有効化
        self.process_tab.update_button_states(True)
        
        # シナリオを読み込む
        config = self._get_config()
        if config and 'scenario_file' in config and os.path.exists(config['scenario_file']):
            self.scenario_tab.load_scenario(config['scenario_file'])
        
        # ファイルリストを更新
        self.files_tab.refresh_file_list()
    
    def _get_agent(self) -> Optional[VideoEditAgent]:
        """
        VideoEditAgentを取得
        
        Returns:
            初期化されたVideoEditAgentインスタンス、または未初期化の場合はNone
        """
        return self.config_manager.agent
    
    def _get_config(self) -> Optional[Dict[str, Any]]:
        """
        設定情報を取得
        
        Returns:
            設定情報の辞書、または未初期化の場合はNone
        """
        if not self.config_manager.agent:
            return None
        return self.config_manager.agent.config 