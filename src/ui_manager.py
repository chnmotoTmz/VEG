"""繝ｦ繝ｼ繧ｶ繝ｼ繧､繝ｳ繧ｿ繝ｼ繝輔ぉ繝ｼ繧ｹ邂｡逅�繝｢繧ｸ繝･繝ｼ繝ｫ

蜍慕判邱ｨ髮�AI繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝医�ｮUI繧堤ｮ｡逅�縺吶ｋ
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from typing import Optional, Callable, Dict, Any

class UIManager:
    def __init__(self):
        """UI繝槭ロ繝ｼ繧ｸ繝｣繝ｼ縺ｮ蛻晄悄蛹�"""
        self.root = tk.Tk()
        self.root.title("蜍慕判邱ｨ髮�AI繧ｨ繝ｼ繧ｸ繧ｧ繝ｳ繝�")
        
        # 迥ｶ諷句､画焚
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.processing = tk.BooleanVar(value=False)
        
        # UI繧ｳ繝ｳ繝昴�ｼ繝阪Φ繝医�ｮ蛻晄悄蛹�
        self._setup_ui()
        
    def _setup_ui(self):
        """UI繧ｳ繝ｳ繝昴�ｼ繝阪Φ繝医ｒ繧ｻ繝�繝医い繝�繝�"""
        # 繝｡繧､繝ｳ繝輔Ξ繝ｼ繝
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 蜈･蜃ｺ蜉幄ｨｭ螳壹そ繧ｯ繧ｷ繝ｧ繝ｳ
        io_frame = ttk.LabelFrame(main_frame, text="蜈･蜃ｺ蜉幄ｨｭ螳�", padding="10")
        io_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # 蜈･蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ
        ttk.Label(io_frame, text="蜈･蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(io_frame, textvariable=self.input_dir, width=40).grid(row=0, column=1)
        ttk.Button(io_frame, text="蜿ら�ｧ", command=self._select_input_dir).grid(row=0, column=2)
        
        # 蜃ｺ蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ
        ttk.Label(io_frame, text="蜃ｺ蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(io_frame, textvariable=self.output_dir, width=40).grid(row=1, column=1)
        ttk.Button(io_frame, text="蜿ら�ｧ", command=self._select_output_dir).grid(row=1, column=2)
        
        # 蜃ｦ逅�繝懊ち繝ｳ繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.process_btn = ttk.Button(button_frame, text="蜃ｦ逅�髢句ｧ�")
        self.process_btn.grid(row=0, column=0, padx=5)
        
        # 繧ｳ繝ｳ繧ｻ繝励ヨ陦ｨ遉ｺ繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ
        concept_frame = ttk.LabelFrame(main_frame, text="逕滓�舌＆繧後◆繧ｳ繝ｳ繧ｻ繝励ヨ", padding="10")
        concept_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.concept_text = scrolledtext.ScrolledText(concept_frame, height=10, wrap=tk.WORD)
        self.concept_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 繝ｭ繧ｰ陦ｨ遉ｺ繧ｻ繧ｯ繧ｷ繝ｧ繝ｳ
        log_frame = ttk.LabelFrame(main_frame, text="蜃ｦ逅�繝ｭ繧ｰ", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # 繧ｹ繝�繝ｼ繧ｿ繧ｹ繝舌�ｼ
        self.status_var = tk.StringVar(value="貅門ｙ螳御ｺ�")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, sticky=tk.W)
        
    def _select_input_dir(self):
        """蜈･蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ繧帝∈謚�"""
        dir_path = filedialog.askdirectory(title="蜈･蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ繧帝∈謚�")
        if dir_path:
            self.input_dir.set(dir_path)
            
    def _select_output_dir(self):
        """蜃ｺ蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ繧帝∈謚�"""
        dir_path = filedialog.askdirectory(title="蜃ｺ蜉帙ョ繧｣繝ｬ繧ｯ繝医Μ繧帝∈謚�")
        if dir_path:
            self.output_dir.set(dir_path)
            
    def update_status(self, message: str):
        """繧ｹ繝�繝ｼ繧ｿ繧ｹ繧呈峩譁ｰ"""
        self.status_var.set(message)
        self.root.update()
        
    def log_message(self, message: str):
        """繝ｭ繧ｰ縺ｫ繝｡繝�繧ｻ繝ｼ繧ｸ繧定ｿｽ蜉"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def display_concept(self, concept_data: Dict[str, Any]):
        """繧ｳ繝ｳ繧ｻ繝励ヨ繧定｡ｨ遉ｺ"""
        self.concept_text.delete(1.0, tk.END)
        
        text = f"繧ｿ繧､繝医Ν: {concept_data.get('title', 'N/A')}\n"
        text += f"繧ｳ繝ｳ繧ｻ繝励ヨ: {concept_data.get('concept_description', 'N/A')}\n"
        text += f"繧ｭ繝ｼ繝医ヴ繝�繧ｯ: {', '.join(concept_data.get('key_topics', []))}\n"
        
        self.concept_text.insert(tk.END, text)
        
    def set_process_callback(self, callback: Callable):
        """蜃ｦ逅�髢句ｧ九�懊ち繝ｳ縺ｮ繧ｳ繝ｼ繝ｫ繝舌ャ繧ｯ繧定ｨｭ螳�"""
        self.process_btn.config(command=callback)
        
    def run(self):
        """UI繧貞ｮ溯｡�"""
        self.root.mainloop()
