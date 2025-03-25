import tkinter as tk
from tkinter import ttk
import sys
import logging
from .gui.scene_selection_gui import SceneSelectionGUI

# ログの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scene_selection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """メイン関数"""
    app = SceneSelectionGUI()  # rootパラメータを削除
    app.root.mainloop()

if __name__ == "__main__":
    main() 