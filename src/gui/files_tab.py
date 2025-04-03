"""生成ファイル確認タブモジュール"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Callable, Dict, Any, List

from ..evolve_chip import EvolveChip

class FilesTab:
    """生成ファイル確認タブのUIとロジックを管理するクラス"""
    
    def __init__(self, parent: ttk.Notebook, config_provider: Callable[[], Optional[Dict[str, Any]]]):
        """
        コンストラクタ
        
        Args:
            parent: 親ウィジェット（Notebook）
            config_provider: 設定情報を提供するコールバック
        """
        self.parent = parent
        self.config_provider = config_provider
        self.frame = ttk.Frame(parent)
        parent.add(self.frame, text="生成ファイル")
        
        self.file_list: List[str] = []
        self._init_ui()
    
    @EvolveChip
    def _init_ui(self) -> None:
        """UIの初期化"""
        # ファイル選択
        file_frame = ttk.Frame(self.frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_combo = ttk.Combobox(file_frame, state="readonly")
        self.file_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.file_combo.bind('<<ComboboxSelected>>', self.load_selected_file)
        
        ttk.Button(file_frame, text="更新", 
                  command=self.refresh_file_list).pack(side=tk.LEFT)
        
        # ファイル内容表示
        self.file_content = scrolledtext.ScrolledText(self.frame)
        self.file_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    @EvolveChip
    def refresh_file_list(self) -> None:
        """ファイルリストを更新"""
        config = self.config_provider()
        if not config:
            messagebox.showwarning("警告", "設定ファイルが読み込まれていません")
            return
            
        output_dir = config.get('output_dir')
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showwarning("警告", "有効な出力ディレクトリがありません")
            return
            
        # 出力ディレクトリ内のファイルを取得
        self.file_list = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith(('.json', '.srt', '.edl', '.txt')):
                    self.file_list.append(os.path.join(root, file))
        
        # コンボボックスを更新
        if self.file_list:
            self.file_combo['values'] = self.file_list
            self.file_combo.current(0)
            self.load_selected_file()
        else:
            self.file_combo['values'] = ["ファイルがありません"]
            self.file_combo.current(0)
            self.file_content.delete('1.0', tk.END)
    
    @EvolveChip
    def load_selected_file(self, event: Optional[tk.Event] = None) -> None:
        """
        選択されたファイルを読み込む
        
        Args:
            event: コンボボックス選択イベント
        """
        selected = self.file_combo.get()
        if not selected or selected == "ファイルがありません" or not os.path.isfile(selected):
            return
            
        try:
            with open(selected, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                
            self.file_content.delete('1.0', tk.END)
            self.file_content.insert('1.0', content)
        except UnicodeDecodeError:
            # UTF-8以外のエンコーディングで再試行
            try:
                with open(selected, 'r', encoding='shift-jis') as f:
                    content = f.read()
                    
                self.file_content.delete('1.0', tk.END)
                self.file_content.insert('1.0', content)
            except Exception as e:
                messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました: {str(e)}")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました: {str(e)}") 