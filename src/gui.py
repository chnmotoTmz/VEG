"""GUIインターフェース"""

import sys
import os
import tkinter as tk

# PYTHONPATHにsrcの親ディレクトリを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_window import MainWindow

def main():
    """アプリケーションのメインエントリーポイント"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main() 