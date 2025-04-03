"""GUIモジュールのテスト"""

import unittest
import sys
import os
import json
import tkinter as tk
from unittest.mock import patch, MagicMock, mock_open
from tkinter import ttk

# テスト対象のモジュールパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.gui.config_manager import ConfigManager
from src.gui.process_tab import ProcessTab
from src.gui.scenario_tab import ScenarioTab
from src.gui.files_tab import FilesTab
from src.gui.main_window import MainWindow
from src.main import VideoEditAgent

class TestConfigManager(unittest.TestCase):
    """ConfigManagerクラスのテスト"""
    
    def setUp(self):
        self.on_config_loaded = MagicMock()
        self.config_manager = ConfigManager(self.on_config_loaded)
    
    @patch("tkinter.filedialog.askdirectory")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_select_config(self, mock_json_dump, mock_file, mock_askdirectory):
        """設定ファイル選択処理が正しく機能するかテスト"""
        # askdirectoryの戻り値を設定
        mock_askdirectory.side_effect = ["/test/input", "/test/output"]
        
        # load_configをモック化
        self.config_manager.load_config = MagicMock()
        
        # メソッド実行
        self.config_manager.select_config()
        
        # 検証
        self.assertEqual(mock_askdirectory.call_count, 2)
        mock_file.assert_called_once()
        mock_json_dump.assert_called_once()
        self.assertEqual(self.config_manager.config_file, "/test/config.json")
        self.config_manager.load_config.assert_called_once()
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"input_dir": "/test/input", "output_dir": "/test/output"}')
    @patch("json.load")
    @patch("src.main.VideoEditAgent")
    def test_load_config(self, mock_agent_class, mock_json_load, mock_file):
        """設定ファイル読み込み処理が正しく機能するかテスト"""
        # jsonロード結果をモック
        test_config = {"input_dir": "/test/input", "output_dir": "/test/output"}
        mock_json_load.return_value = test_config
        
        # エージェントインスタンスをモック
        mock_agent = MagicMock()
        mock_agent_class.return_value = mock_agent
        
        # 準備
        self.config_manager.config_file = "/test/config.json"
        
        # メソッド実行
        self.config_manager.load_config()
        
        # 検証
        mock_file.assert_called_once_with("/test/config.json", "r", encoding="utf-8-sig")
        mock_json_load.assert_called_once()
        mock_agent_class.assert_called_once_with(test_config)
        self.assertEqual(self.config_manager.agent, mock_agent)
        self.on_config_loaded.assert_called_once_with("/test/config.json", mock_agent)

class TestProcessTab(unittest.TestCase):
    """ProcessTabクラスのテスト"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.notebook = ttk.Notebook(self.root)
        self.agent_provider = MagicMock()
        self.process_tab = ProcessTab(self.notebook, self.agent_provider)
    
    def tearDown(self):
        if self.root:
            self.root.destroy()
    
    def test_init(self):
        """初期化が正しく行われるかテスト"""
        # 検証
        self.assertEqual(self.process_tab.parent, self.notebook)
        self.assertEqual(self.process_tab.agent_provider, self.agent_provider)
        self.assertIsInstance(self.process_tab.frame, ttk.Frame)
        self.assertIsInstance(self.process_tab.analyze_button, ttk.Button)
        self.assertIsInstance(self.process_tab.select_button, ttk.Button)
        self.assertIsInstance(self.process_tab.generate_button, ttk.Button)
        self.assertIsInstance(self.process_tab.run_button, ttk.Button)
        self.assertIsInstance(self.process_tab.progress, ttk.Progressbar)
        self.assertIsInstance(self.process_tab.log_text, tk.scrolledtext.ScrolledText)
    
    def test_update_button_states(self):
        """ボタン状態更新が正しく機能するかテスト"""
        # 有効化
        self.process_tab.update_button_states(True)
        self.assertEqual(self.process_tab.analyze_button["state"], "normal")
        self.assertEqual(self.process_tab.select_button["state"], "normal")
        self.assertEqual(self.process_tab.generate_button["state"], "normal")
        self.assertEqual(self.process_tab.run_button["state"], "normal")
        
        # 無効化
        self.process_tab.update_button_states(False)
        self.assertEqual(self.process_tab.analyze_button["state"], "disabled")
        self.assertEqual(self.process_tab.select_button["state"], "disabled")
        self.assertEqual(self.process_tab.generate_button["state"], "disabled")
        self.assertEqual(self.process_tab.run_button["state"], "disabled")
    
    @patch("tkinter.messagebox.showwarning")
    def test_run_phase_no_agent(self, mock_showwarning):
        """エージェントがない場合の処理が正しく機能するかテスト"""
        # エージェントがない状態を設定
        self.agent_provider.return_value = None
        
        # メソッド実行
        self.process_tab.run_phase("analyze")
        
        # 検証
        mock_showwarning.assert_called_once()
    
    @patch("tkinter.messagebox.showinfo")
    def test_run_phase_analyze(self, mock_showinfo):
        """分析フェーズの実行が正しく機能するかテスト"""
        # モックエージェント
        mock_agent = MagicMock()
        self.agent_provider.return_value = mock_agent
        
        # プログレスバーのメソッドをモック化
        self.process_tab.progress.start = MagicMock()
        self.process_tab.progress.stop = MagicMock()
        
        # ボタン状態更新をモック化
        self.process_tab.update_button_states = MagicMock()
        
        # ログ出力をモック化
        self.process_tab.log_message = MagicMock()
        
        # メソッド実行
        self.process_tab.run_phase("analyze")
        
        # 検証
        self.agent_provider.assert_called_once()
        mock_agent.analyze_contents.assert_called_once()
        self.process_tab.progress.start.assert_called_once()
        self.process_tab.progress.stop.assert_called_once()
        self.assertEqual(self.process_tab.update_button_states.call_count, 2)
        self.assertEqual(self.process_tab.log_message.call_count, 2)
        mock_showinfo.assert_called_once()
    
    def test_log_message(self):
        """ログメッセージ追加が正しく機能するかテスト"""
        # テキストエリアのメソッドをモック化
        self.process_tab.log_text.insert = MagicMock()
        self.process_tab.log_text.see = MagicMock()
        
        # メソッド実行
        self.process_tab.log_message("テストメッセージ")
        
        # 検証
        self.process_tab.log_text.insert.assert_called_once_with(tk.END, "テストメッセージ\n")
        self.process_tab.log_text.see.assert_called_once_with(tk.END)

class TestScenarioTab(unittest.TestCase):
    """ScenarioTabクラスのテスト"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.notebook = ttk.Notebook(self.root)
        self.config_provider = MagicMock()
        self.scenario_tab = ScenarioTab(self.notebook, self.config_provider)
    
    def tearDown(self):
        if self.root:
            self.root.destroy()
    
    def test_init(self):
        """初期化が正しく行われるかテスト"""
        # 検証
        self.assertEqual(self.scenario_tab.parent, self.notebook)
        self.assertEqual(self.scenario_tab.config_provider, self.config_provider)
        self.assertIsInstance(self.scenario_tab.frame, ttk.Frame)
        self.assertIsInstance(self.scenario_tab.scenario_edit, tk.scrolledtext.ScrolledText)
    
    @patch("builtins.open", new_callable=mock_open, read_data='{"title": "テストシナリオ"}')
    @patch("json.load")
    def test_load_scenario(self, mock_json_load, mock_file):
        """シナリオ読み込みが正しく機能するかテスト"""
        # jsonロード結果をモック
        test_scenario = {"title": "テストシナリオ"}
        mock_json_load.return_value = test_scenario
        
        # テキストエリアのメソッドをモック化
        self.scenario_tab.scenario_edit.delete = MagicMock()
        self.scenario_tab.scenario_edit.insert = MagicMock()
        
        # メソッド実行
        self.scenario_tab.load_scenario("/test/scenario.json")
        
        # 検証
        mock_file.assert_called_once_with("/test/scenario.json", "r", encoding="utf-8-sig")
        mock_json_load.assert_called_once()
        self.scenario_tab.scenario_edit.delete.assert_called_once_with("1.0", tk.END)
        self.scenario_tab.scenario_edit.insert.assert_called_once()
    
    @patch("tkinter.messagebox.showwarning")
    def test_save_scenario_no_config(self, mock_showwarning):
        """設定がない場合のシナリオ保存処理が正しく機能するかテスト"""
        # 設定がない状態を設定
        self.config_provider.return_value = None
        
        # メソッド実行
        self.scenario_tab.save_scenario()
        
        # 検証
        mock_showwarning.assert_called_once()
    
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_scenario(self, mock_json_dump, mock_file, mock_makedirs):
        """シナリオ保存が正しく機能するかテスト"""
        # 設定を設定
        self.config_provider.return_value = {"scenario_file": "/test/scenario.json"}
        
        # テキストエリアの内容をモック
        self.scenario_tab.scenario_edit.get = MagicMock(return_value='{"title": "テストシナリオ"}')
        
        # メソッド実行
        self.scenario_tab.save_scenario()
        
        # 検証
        mock_makedirs.assert_called_once_with(os.path.dirname("/test/scenario.json"), exist_ok=True)
        mock_file.assert_called_once_with("/test/scenario.json", "w", encoding="utf-8-sig")
        mock_json_dump.assert_called_once()

class TestFilesTab(unittest.TestCase):
    """FilesTabクラスのテスト"""
    
    def setUp(self):
        self.root = tk.Tk()
        self.notebook = ttk.Notebook(self.root)
        self.config_provider = MagicMock()
        self.files_tab = FilesTab(self.notebook, self.config_provider)
    
    def tearDown(self):
        if self.root:
            self.root.destroy()
    
    def test_init(self):
        """初期化が正しく行われるかテスト"""
        # 検証
        self.assertEqual(self.files_tab.parent, self.notebook)
        self.assertEqual(self.files_tab.config_provider, self.config_provider)
        self.assertIsInstance(self.files_tab.frame, ttk.Frame)
        self.assertIsInstance(self.files_tab.file_combo, ttk.Combobox)
        self.assertIsInstance(self.files_tab.file_content, tk.scrolledtext.ScrolledText)
        self.assertEqual(self.files_tab.file_list, [])
    
    @patch("tkinter.messagebox.showwarning")
    def test_refresh_file_list_no_config(self, mock_showwarning):
        """設定がない場合のファイルリスト更新が正しく機能するかテスト"""
        # 設定がない状態を設定
        self.config_provider.return_value = None
        
        # メソッド実行
        self.files_tab.refresh_file_list()
        
        # 検証
        mock_showwarning.assert_called_once()
    
    @patch("os.path.isdir")
    @patch("os.walk")
    def test_refresh_file_list(self, mock_walk, mock_isdir):
        """ファイルリスト更新が正しく機能するかテスト"""
        # 設定を設定
        self.config_provider.return_value = {"output_dir": "/test/output"}
        
        # ディレクトリ存在チェックをモック
        mock_isdir.return_value = True
        
        # ファイル一覧をモック
        mock_walk.return_value = [
            ("/test/output", [], ["file1.json", "file2.srt", "ignore.txt"]),
            ("/test/output/subdir", [], ["file3.edl"])
        ]
        
        # コンボボックスと読み込みメソッドをモック
        self.files_tab.file_combo = MagicMock()
        self.files_tab.load_selected_file = MagicMock()
        
        # メソッド実行
        self.files_tab.refresh_file_list()
        
        # 検証
        mock_isdir.assert_called_once_with("/test/output")
        mock_walk.assert_called_once_with("/test/output")
        
        # ファイルリストが正しく設定されているか
        expected_files = [
            "/test/output/file1.json",
            "/test/output/file2.srt",
            "/test/output/subdir/file3.edl"
        ]
        self.assertEqual(sorted(self.files_tab.file_list), sorted(expected_files))
        
        # コンボボックスが更新されているか
        self.files_tab.file_combo.__setitem__.assert_called_once_with("values", self.files_tab.file_list)
        self.files_tab.file_combo.current.assert_called_once_with(0)
        self.files_tab.load_selected_file.assert_called_once()
    
    @patch("os.path.isfile")
    @patch("builtins.open", new_callable=mock_open, read_data="テストファイル内容")
    def test_load_selected_file(self, mock_file, mock_isfile):
        """選択されたファイルの読み込みが正しく機能するかテスト"""
        # ファイル存在チェックをモック
        mock_isfile.return_value = True
        
        # コンボボックスの取得をモック
        self.files_tab.file_combo.get = MagicMock(return_value="/test/file.json")
        
        # テキストエリアのメソッドをモック
        self.files_tab.file_content.delete = MagicMock()
        self.files_tab.file_content.insert = MagicMock()
        
        # メソッド実行
        self.files_tab.load_selected_file()
        
        # 検証
        mock_isfile.assert_called_once_with("/test/file.json")
        mock_file.assert_called_once_with("/test/file.json", "r", encoding="utf-8-sig")
        self.files_tab.file_content.delete.assert_called_once_with("1.0", tk.END)
        self.files_tab.file_content.insert.assert_called_once_with("1.0", "テストファイル内容")

class TestMainWindow(unittest.TestCase):
    """MainWindowクラスのテスト"""
    
    def setUp(self):
        self.root = tk.Tk()
        
        # ProcessTab, ScenarioTab, FilesTabクラスをモック
        self.process_tab_patcher = patch("src.gui.main_window.ProcessTab")
        self.scenario_tab_patcher = patch("src.gui.main_window.ScenarioTab")
        self.files_tab_patcher = patch("src.gui.main_window.FilesTab")
        self.config_manager_patcher = patch("src.gui.main_window.ConfigManager")
        
        self.mock_process_tab_class = self.process_tab_patcher.start()
        self.mock_scenario_tab_class = self.scenario_tab_patcher.start()
        self.mock_files_tab_class = self.files_tab_patcher.start()
        self.mock_config_manager_class = self.config_manager_patcher.start()
        
        # モックインスタンス
        self.mock_process_tab = MagicMock()
        self.mock_scenario_tab = MagicMock()
        self.mock_files_tab = MagicMock()
        self.mock_config_manager = MagicMock()
        
        self.mock_process_tab_class.return_value = self.mock_process_tab
        self.mock_scenario_tab_class.return_value = self.mock_scenario_tab
        self.mock_files_tab_class.return_value = self.mock_files_tab
        self.mock_config_manager_class.return_value = self.mock_config_manager
        
        # MainWindowインスタンス作成
        self.main_window = MainWindow(self.root)
    
    def tearDown(self):
        self.process_tab_patcher.stop()
        self.scenario_tab_patcher.stop()
        self.files_tab_patcher.stop()
        self.config_manager_patcher.stop()
        
        if self.root:
            self.root.destroy()
    
    def test_init(self):
        """初期化が正しく行われるかテスト"""
        # 検証
        self.assertEqual(self.main_window.root, self.root)
        self.mock_config_manager_class.assert_called_once()
        self.mock_process_tab_class.assert_called_once()
        self.mock_scenario_tab_class.assert_called_once()
        self.mock_files_tab_class.assert_called_once()
        self.mock_process_tab.update_button_states.assert_called_once_with(False)
    
    def test_on_config_loaded(self):
        """設定読み込み完了時のコールバックが正しく機能するかテスト"""
        # 初期化
        self.main_window.config_path = MagicMock()
        
        # テスト用データ
        mock_agent = MagicMock()
        mock_config = {"scenario_file": "/test/scenario.json"}
        
        # _get_configメソッドをモック
        self.main_window._get_config = MagicMock(return_value=mock_config)
        
        # ファイル存在チェックをモック
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            
            # メソッド実行
            self.main_window._on_config_loaded("/test/config.json", mock_agent)
            
            # 検証
            self.main_window.config_path.config.assert_called_once_with(text="/test/config.json")
            self.mock_process_tab.update_button_states.assert_called_with(True)
            self.mock_scenario_tab.load_scenario.assert_called_once_with("/test/scenario.json")
            self.mock_files_tab.refresh_file_list.assert_called_once()
    
    def test_get_agent(self):
        """エージェント取得メソッドが正しく機能するかテスト"""
        # モックエージェント
        mock_agent = MagicMock()
        self.mock_config_manager.agent = mock_agent
        
        # メソッド実行
        result = self.main_window._get_agent()
        
        # 検証
        self.assertEqual(result, mock_agent)
    
    def test_get_config(self):
        """設定取得メソッドが正しく機能するかテスト"""
        # モックエージェントと設定
        mock_agent = MagicMock()
        mock_agent.config = {"test": "config"}
        self.mock_config_manager.agent = mock_agent
        
        # メソッド実行
        result = self.main_window._get_config()
        
        # 検証
        self.assertEqual(result, {"test": "config"})
    
    def test_get_config_no_agent(self):
        """エージェントがない場合の設定取得メソッドが正しく機能するかテスト"""
        # エージェントなし
        self.mock_config_manager.agent = None
        
        # メソッド実行
        result = self.main_window._get_config()
        
        # 検証
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main() 