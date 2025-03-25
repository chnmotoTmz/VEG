"""ユーザーインターフェース管理モジュール

動画編集AIエージェントのUIを管理する
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from typing import Optional, Callable, Dict, Any

class UIManager:
    def __init__(self):
        """UIマネージャーの初期化"""
        self.root = tk.Tk()
        self.root.title("動画編集AIエージェント")
        
        # 状態変数
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.processing = tk.BooleanVar(value=False)
        
        # UIコンポーネントの初期化
        self._setup_ui()
        
    def _setup_ui(self):
        """UIコンポーネントをセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 入出力設定セクション
        io_frame = ttk.LabelFrame(main_frame, text="入出力設定", padding="10")
        io_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 入力ディレクトリ
        ttk.Label(io_frame, text="入力ディレクトリ:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(io_frame, textvariable=self.input_dir, width=40).grid(row=0, column=1)
        ttk.Button(io_frame, text="参照", command=self._select_input_dir).grid(row=0, column=2)
        
        # 出力ディレクトリ
        ttk.Label(io_frame, text="出力ディレクトリ:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(io_frame, textvariable=self.output_dir, width=40).grid(row=1, column=1)
        ttk.Button(io_frame, text="参照", command=self._select_output_dir).grid(row=1, column=2)
        
        # 処理ボタンセクション
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.process_btn = ttk.Button(button_frame, text="処理開始")
        self.process_btn.grid(row=0, column=0, padx=5)
        
        # コンセプト表示セクション
        concept_frame = ttk.LabelFrame(main_frame, text="生成されたコンセプト", padding="10")
        concept_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.concept_text = scrolledtext.ScrolledText(concept_frame, height=10, wrap=tk.WORD)
        self.concept_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # ログ表示セクション
        log_frame = ttk.LabelFrame(main_frame, text="処理ログ", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, sticky=tk.W)
        
    def _select_input_dir(self):
        """入力ディレクトリを選択"""
        dir_path = filedialog.askdirectory(title="入力ディレクトリを選択")
        if dir_path:
            self.input_dir.set(dir_path)
            
    def _select_output_dir(self):
        """出力ディレクトリを選択"""
        dir_path = filedialog.askdirectory(title="出力ディレクトリを選択")
        if dir_path:
            self.output_dir.set(dir_path)
            
    def update_status(self, message: str):
        """ステータスを更新"""
        self.status_var.set(message)
        self.root.update()
        
    def log_message(self, message: str):
        """ログにメッセージを追加"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def display_concept(self, concept_data: Dict[str, Any]):
        """コンセプトを表示"""
        self.concept_text.delete(1.0, tk.END)
        
        text = f"タイトル: {concept_data.get('title', 'N/A')}\n"
        text += f"コンセプト: {concept_data.get('concept_description', 'N/A')}\n"
        text += f"キートピック: {', '.join(concept_data.get('key_topics', []))}\n"
        
        self.concept_text.insert(tk.END, text)
        
    def set_process_callback(self, callback: Callable):
        """処理開始ボタンのコールバックを設定"""
        self.process_btn.config(command=callback)
        
    def run(self):
        """UIを実行"""
        self.root.mainloop()
