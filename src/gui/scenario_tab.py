"""シナリオ編集タブモジュール"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from typing import Optional, Callable, Dict, Any

from ..evolve_chip import EvolveChip

class ScenarioTab:
    """シナリオ編集タブのUIとロジックを管理するクラス"""
    
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
        parent.add(self.frame, text="シナリオ編集")
        
        self._init_ui()
    
    @EvolveChip
    def _init_ui(self) -> None:
        """UIの初期化"""
        self.scenario_edit = scrolledtext.ScrolledText(self.frame)
        self.scenario_edit.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(self.frame, text="シナリオを保存", 
                  command=self.save_scenario).pack(pady=5)
    
    @EvolveChip
    def load_scenario(self, file_path: str) -> None:
        """
        シナリオファイルを読み込む
        
        Args:
            file_path: 読み込むファイルのパス
        """
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                scenario = json.load(f)
                self.scenario_edit.delete('1.0', tk.END)
                self.scenario_edit.insert('1.0', 
                    json.dumps(scenario, ensure_ascii=False, indent=2))
        except Exception as e:
            messagebox.showerror("エラー", f"シナリオファイルの読み込みに失敗しました: {str(e)}")
    
    @EvolveChip
    def save_scenario(self) -> None:
        """シナリオを保存"""
        config = self.config_provider()
        if not config:
            messagebox.showwarning("警告", "設定ファイルが読み込まれていません")
            return
            
        scenario_file = config.get('scenario_file')
        if not scenario_file:
            scenario_file = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not scenario_file:
                return
        
        try:
            # テキストエリアからJSONを取得
            scenario_text = self.scenario_edit.get('1.0', tk.END)
            scenario = json.loads(scenario_text)
            
            # ファイルに保存
            os.makedirs(os.path.dirname(scenario_file), exist_ok=True)
            with open(scenario_file, 'w', encoding='utf-8-sig') as f:
                json.dump(scenario, f, ensure_ascii=False, indent=2)
                
            messagebox.showinfo("成功", f"シナリオを保存しました:\n{scenario_file}")
        except json.JSONDecodeError:
            messagebox.showerror("エラー", "無効なJSON形式です")
        except Exception as e:
            messagebox.showerror("エラー", f"シナリオの保存に失敗しました: {str(e)}") 