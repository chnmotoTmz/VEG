"""処理タブモジュール"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Callable

from ..evolve_chip import EvolveChip
from ..main import VideoEditAgent

class ProcessTab:
    """処理タブのUIとロジックを管理するクラス"""
    
    def __init__(self, parent: ttk.Notebook, agent_provider: Callable[[], Optional[VideoEditAgent]]):
        """
        コンストラクタ
        
        Args:
            parent: 親ウィジェット（Notebook）
            agent_provider: VideoEditAgentを提供するコールバック
        """
        self.parent = parent
        self.agent_provider = agent_provider
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="処理")
        
        self._init_ui()
    
    @EvolveChip
    def _init_ui(self) -> None:
        """UIの初期化"""
        # 処理ボタン
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.analyze_button = ttk.Button(button_frame, text="コンテンツ分析", 
                                       command=lambda: self.run_phase("analyze"))
        self.select_button = ttk.Button(button_frame, text="シーン選択", 
                                      command=lambda: self.run_phase("select"))
        self.generate_button = ttk.Button(button_frame, text="出力生成", 
                                        command=lambda: self.run_phase("generate"))
        self.run_button = ttk.Button(button_frame, text="全フェーズ実行", 
                                   command=lambda: self.run_phase("run"))
        
        self.analyze_button.pack(side=tk.LEFT, padx=2)
        self.select_button.pack(side=tk.LEFT, padx=2)
        self.generate_button.pack(side=tk.LEFT, padx=2)
        self.run_button.pack(side=tk.LEFT, padx=2)
        
        # プログレスバー
        self.progress = ttk.Progressbar(self.frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=5, pady=5)
        
        # ログ表示
        self.log_text = scrolledtext.ScrolledText(self.frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    @EvolveChip
    def update_button_states(self, enabled: bool) -> None:
        """
        ボタンの状態を更新
        
        Args:
            enabled: ボタンを有効にするかどうか
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        self.analyze_button.config(state=state)
        self.select_button.config(state=state)
        self.generate_button.config(state=state)
        self.run_button.config(state=state)
    
    @EvolveChip
    def run_phase(self, phase: str) -> None:
        """
        処理フェーズを実行
        
        Args:
            phase: 実行するフェーズ名
        """
        agent = self.agent_provider()
        if not agent:
            messagebox.showwarning("警告", "設定ファイルを選択してください")
            return
        
        # ボタンを無効化
        self.update_button_states(False)
        
        # プログレスバーを開始
        self.progress.start()
        
        try:
            if phase == "analyze":
                self.log_message("コンテンツ分析を開始...")
                agent.analyze_contents()
                self.log_message("コンテンツ分析が完了しました")
            elif phase == "select":
                self.log_message("シーン選択を開始...")
                contents = agent.analyze_contents()
                agent.select_scenes(contents)
                self.log_message("シーン選択が完了しました")
            elif phase == "generate":
                self.log_message("出力生成を開始...")
                contents = agent.analyze_contents()
                scenes = agent.select_scenes(contents)
                agent.generate_outputs(contents, scenes)
                self.log_message("出力生成が完了しました")
            elif phase == "run":
                self.log_message("全フェーズの実行を開始...")
                agent.run()
                self.log_message("全フェーズの実行が完了しました")
                
            messagebox.showinfo("成功", f"{phase}フェーズが完了しました")
        except Exception as e:
            self.log_message(f"エラーが発生しました: {str(e)}")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {str(e)}")
        finally:
            # プログレスバーを停止
            self.progress.stop()
            
            # ボタンを有効化
            self.update_button_states(True)
    
    def log_message(self, message: str) -> None:
        """
        ログメッセージを追加
        
        Args:
            message: 追加するメッセージ
        """
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END) 