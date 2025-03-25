import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import logging
import subprocess
from typing import List, Dict, Any, Optional
from ..editing_agent import EditingAgent, SceneMatch
from ..utils import ContentCrawler
from ..scenario_writer import EnhancedScenarioWriter, ScenarioInput
from moviepy.editor import VideoFileClip, concatenate_videoclips

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

class SceneSelectionGUI:
    """
    シーン選択とプレビュー機能を提供するGUIクラス
    """
    
    def __init__(self):
        """
        GUIの初期化
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # ログレベルをDEBUGに設定
        
        self.root = tk.Tk()
        self.root.title("シーン選択ツール")
        self.root.geometry("1200x800")
        
        self.folder_path = tk.StringVar()
        self.scenario_input = None
        self.content_crawler = None
        self.scenario_writer = None
        self.editing_agent = None
        self.video_data = []
        self.selected_scenes = []
        self.current_section = None
        self.scene_vars = {}  # シーンの選択状態を保持する辞書
        
        self._create_widgets()
        self.logger.info("SceneSelectionGUI initialized")
    
    def _create_widgets(self):
        """GUIウィジェットの作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # トップフレーム（フォルダ選択など）
        top_frame = ttk.LabelFrame(main_frame, text="フォルダ選択", padding=5)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="フォルダパス:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Entry(top_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(top_frame, text="参照", command=self._browse_folder).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(top_frame, text="読み込み", command=self._load_content).grid(row=0, column=3, padx=5, pady=5)
        
        # 中央フレーム（シナリオ作成、セクション表示）
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左側：シナリオ作成
        scenario_frame = ttk.LabelFrame(middle_frame, text="シナリオ作成", padding=5)
        scenario_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(scenario_frame, text="タイトル:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.title_entry = ttk.Entry(scenario_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(scenario_frame, text="対象視聴者:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.audience_entry = ttk.Entry(scenario_frame, width=30)
        self.audience_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(scenario_frame, text="スタイル:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.style_entry = ttk.Entry(scenario_frame, width=30)
        self.style_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(scenario_frame, text="メインメッセージ:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.message_entry = ttk.Entry(scenario_frame, width=30)
        self.message_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(scenario_frame, text="長さ (秒):").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.length_entry = ttk.Entry(scenario_frame, width=30)
        self.length_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Label(scenario_frame, text="キーポイント (1行に1つ):").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.keypoints_text = tk.Text(scenario_frame, width=30, height=5)
        self.keypoints_text.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        ttk.Button(scenario_frame, text="シナリオ生成", command=self._generate_scenario).grid(row=6, column=0, columnspan=2, padx=5, pady=10)
        
        # 右側：セクション表示
        section_frame = ttk.LabelFrame(middle_frame, text="シナリオセクション", padding=5)
        section_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.section_listbox = tk.Listbox(section_frame, height=10)
        self.section_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.section_listbox.bind('<<ListboxSelect>>', self._on_section_select)
        
        # 詳細フレーム（セクション詳細、シーン一覧）
        detail_frame = ttk.Frame(main_frame)
        detail_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左側：セクション詳細
        section_detail_frame = ttk.LabelFrame(detail_frame, text="セクション詳細", padding=5)
        section_detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.section_detail_text = tk.Text(section_detail_frame, width=40, height=10, wrap=tk.WORD)
        self.section_detail_text.pack(fill=tk.BOTH, expand=True)
        
        # 右側：マッチするシーン
        scene_frame = ttk.LabelFrame(detail_frame, text="候補シーン", padding=5)
        scene_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        scene_list_frame = ttk.Frame(scene_frame)
        scene_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scene_listbox = tk.Listbox(scene_list_frame, height=10)
        self.scene_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scene_scroll = ttk.Scrollbar(scene_list_frame, command=self.scene_listbox.yview)
        scene_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.scene_listbox.config(yscrollcommand=scene_scroll.set)
        
        scene_button_frame = ttk.Frame(scene_frame)
        scene_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(scene_button_frame, text="プレビュー", command=self._preview_scene).pack(side=tk.LEFT, padx=5)
        ttk.Button(scene_button_frame, text="追加", command=self._add_scene).pack(side=tk.LEFT, padx=5)
        
        # 下部フレーム（選択済みシーン）
        bottom_frame = ttk.LabelFrame(main_frame, text="選択済みシーン", padding=5)
        bottom_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        selected_list_frame = ttk.Frame(bottom_frame)
        selected_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.selected_listbox = tk.Listbox(selected_list_frame, height=10)
        self.selected_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        selected_scroll = ttk.Scrollbar(selected_list_frame, command=self.selected_listbox.yview)
        selected_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.selected_listbox.config(yscrollcommand=selected_scroll.set)
        
        selected_button_frame = ttk.Frame(bottom_frame)
        selected_button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(selected_button_frame, text="削除", command=self._remove_scene).pack(side=tk.LEFT, padx=5)
        ttk.Button(selected_button_frame, text="上へ", command=lambda: self._move_scene(-1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(selected_button_frame, text="下へ", command=lambda: self._move_scene(1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(selected_button_frame, text="お試し再生", command=self._trial_playback).pack(side=tk.LEFT, padx=5)
        ttk.Button(selected_button_frame, text="EDL生成", command=self._generate_edl).pack(side=tk.RIGHT, padx=5)
    
    def _browse_folder(self):
        """フォルダ選択ダイアログを表示"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def _load_content(self):
        """選択されたフォルダからコンテンツを読み込む"""
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("エラー", "有効なフォルダを選択してください")
            return
        
        try:
            # コンテンツクローラーの初期化
            self.content_crawler = ContentCrawler(folder)
            self.video_data = self.content_crawler.crawl()
            
            if not self.video_data:
                messagebox.showwarning("警告", "フォルダ内にビデオデータが見つかりません")
                return
            
            # エディティングエージェントの初期化
            self.editing_agent = EditingAgent(self.video_data)
            
            # シナリオライターの初期化
            self.scenario_writer = EnhancedScenarioWriter()
            
            messagebox.showinfo("成功", f"{len(self.video_data)}件のビデオデータを読み込みました")
            self.logger.info(f"Loaded {len(self.video_data)} videos from {folder}")
            
        except Exception as e:
            messagebox.showerror("エラー", f"コンテンツの読み込み中にエラーが発生しました: {str(e)}")
            self.logger.error(f"Error loading content: {str(e)}", exc_info=True)
    
    def _generate_scenario(self):
        """入力されたパラメータからシナリオを生成"""
        if not self.video_data:
            messagebox.showerror("エラー", "まずコンテンツを読み込んでください")
            return
        
        try:
            # 入力値の取得
            title = self.title_entry.get()
            audience = self.audience_entry.get()
            style = self.style_entry.get()
            message = self.message_entry.get()
            
            try:
                length = int(self.length_entry.get())
            except ValueError:
                messagebox.showerror("エラー", "長さは整数で入力してください")
                return
            
            key_points = self.keypoints_text.get("1.0", tk.END).strip().split("\n")
            key_points = [p for p in key_points if p.strip()]
            
            # ScenarioInputの作成
            self.scenario_input = ScenarioInput(
                title=title,
                target_audience=audience,
                style=style,
                main_message=message,
                length=length,
                key_points=key_points
            )
            
            # シナリオの生成
            scenario_json = self.scenario_writer.generate(self.video_data, self.scenario_input)
            self.scenario_data = json.loads(scenario_json)
            
            # セクションリストの更新
            self._update_section_list()
            
            messagebox.showinfo("成功", "シナリオを生成しました")
            self.logger.info(f"Generated scenario with {len(self.scenario_data['sections'])} sections")
            
        except Exception as e:
            messagebox.showerror("エラー", f"シナリオ生成中にエラーが発生しました: {str(e)}")
            self.logger.error(f"Error generating scenario: {str(e)}", exc_info=True)
    
    def _update_section_list(self):
        """シナリオセクションリストを更新"""
        if not hasattr(self, 'scenario_data'):
            return
        
        self.section_listbox.delete(0, tk.END)
        
        for i, section in enumerate(self.scenario_data["sections"]):
            title = section["title"]
            duration = section["duration"]
            self.section_listbox.insert(tk.END, f"{i+1}. {title} ({duration}秒)")
    
    def _on_section_select(self, event):
        """セクションが選択されたときの処理"""
        if not hasattr(self, 'scenario_data'):
            return
        
        selection = self.section_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < 0 or index >= len(self.scenario_data["sections"]):
            return
        
        # 選択されたセクション情報の取得
        self.current_section = self.scenario_data["sections"][index]
        
        # セクション詳細の表示
        self._update_section_detail()
        
        # シーン候補の取得と表示
        self._find_matching_scenes()
    
    def _update_section_detail(self):
        """選択されたセクションの詳細を表示"""
        if not self.current_section:
            return
        
        # テキストクリア
        self.section_detail_text.delete("1.0", tk.END)
        
        # セクション情報の表示
        details = (
            f"タイトル: {self.current_section['title']}\n"
            f"長さ: {self.current_section['duration']}秒\n\n"
            f"説明: {self.current_section['description']}\n\n"
            f"ナレーション: {self.current_section['narration_notes']}\n\n"
            f"主要シーン: \n"
        )
        
        for scene in self.current_section['key_scenes']:
            details += f"- {scene}\n"
        
        self.section_detail_text.insert("1.0", details)
    
    def _find_matching_scenes(self):
        """現在のセクションにマッチするシーンを検索"""
        if not self.current_section or not self.editing_agent:
            return
        
        # シナリオからクエリを生成
        query = self.scenario_writer.parse_scenario(self.current_section["description"])
        
        # マッチするシーンを検索
        matching_scenes = self.editing_agent.match_scenes(query, limit=10)
        
        # シーンリストを更新
        self.scene_listbox.delete(0, tk.END)
        
        for i, scene in enumerate(matching_scenes):
            self.scene_listbox.insert(tk.END, f"{i+1}. 類似度: {scene.similarity:.2f} - {scene.text[:50]}...")
    
    def _preview_scene(self):
        """選択されたシーンをプレビュー"""
        # 候補シーンリストから選択されたシーンを取得
        selection = self.scene_listbox.curselection()
        if not selection:
            messagebox.showinfo("情報", "プレビューするシーンを選択してください")
            return
        
        index = selection[0]
        query = self.scenario_writer.parse_scenario(self.current_section["description"])
        matching_scenes = self.editing_agent.match_scenes(query)
        
        if index >= len(matching_scenes):
            return
        
        selected_scene = matching_scenes[index]
        
        # プレビュークリップの生成
        clip_path = self.editing_agent.generate_preview_clip(selected_scene)
        
        if not clip_path or not os.path.exists(clip_path):
            # 元の動画ファイルのパスを試す
            for video in self.video_data:
                video_path = video.get("video_path", "")
                if video_path and os.path.exists(video_path):
                    clip_path = video_path
                    break
        
        if clip_path and os.path.exists(clip_path):
            # クリップを再生
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(clip_path)
                else:  # macOS/Linux
                    subprocess.call(['xdg-open', clip_path])
            except Exception as e:
                messagebox.showerror("エラー", f"クリップの再生中にエラーが発生しました: {str(e)}")
        else:
            messagebox.showwarning("警告", "プレビュークリップが見つかりません")
    
    def _add_scene(self):
        """選択されたシーンを追加"""
        selection = self.scene_listbox.curselection()
        if not selection:
            messagebox.showinfo("情報", "追加するシーンを選択してください")
            return
        
        index = selection[0]
        query = self.scenario_writer.parse_scenario(self.current_section["description"])
        matching_scenes = self.editing_agent.match_scenes(query)
        
        if index >= len(matching_scenes):
            return
        
        selected_scene = matching_scenes[index]
        
        # 選択済みリストに追加
        self.selected_scenes.append(selected_scene)
        self._update_selected_list()
    
    def _update_selected_list(self):
        """選択済みシーンリストを更新"""
        self.selected_listbox.delete(0, tk.END)
        
        for i, scene in enumerate(self.selected_scenes):
            self.selected_listbox.insert(tk.END, f"{i+1}. {scene.text[:50]}...")
    
    def _remove_scene(self):
        """選択済みシーンから削除"""
        selection = self.selected_listbox.curselection()
        if not selection:
            messagebox.showinfo("情報", "削除するシーンを選択してください")
            return
        
        index = selection[0]
        if index < 0 or index >= len(self.selected_scenes):
            return
        
        # リストから削除
        del self.selected_scenes[index]
        self._update_selected_list()
    
    def _move_scene(self, direction):
        """選択済みシーンを上下に移動"""
        selection = self.selected_listbox.curselection()
        if not selection:
            messagebox.showinfo("情報", "移動するシーンを選択してください")
            return
        
        index = selection[0]
        if index < 0 or index >= len(self.selected_scenes):
            return
        
        new_index = index + direction
        if new_index < 0 or new_index >= len(self.selected_scenes):
            return
        
        # シーンを入れ替え
        self.selected_scenes[index], self.selected_scenes[new_index] = self.selected_scenes[new_index], self.selected_scenes[index]
        self._update_selected_list()
        
        # 新しい位置を選択状態に
        self.selected_listbox.selection_clear(0, tk.END)
        self.selected_listbox.selection_set(new_index)
    
    def _trial_playback(self):
        """選択されたシーンを連続再生"""
        if not self.selected_scenes:
            messagebox.showinfo("情報", "シーンが選択されていません")
            return
        
        try:
            # 各シーンのクリップパスを収集
            clip_paths = []
            for scene in self.selected_scenes:
                clip_path = self.editing_agent.generate_preview_clip(scene)
                if clip_path and os.path.exists(clip_path):
                    clip_paths.append(clip_path)
            
            if not clip_paths:
                messagebox.showwarning("警告", "再生可能なクリップがありません")
                return
            
            # MoviePyを使用してクリップを結合
            clips = [VideoFileClip(path) for path in clip_paths]
            final_clip = concatenate_videoclips(clips)
            
            # 一時ファイルとして保存
            output_path = os.path.join(os.getcwd(), "trial_playback.mp4")
            final_clip.write_videofile(output_path)
            
            # 再生
            if os.name == 'nt':  # Windows
                os.startfile(output_path)
            else:  # macOS/Linux
                subprocess.call(['xdg-open', output_path])
            
        except Exception as e:
            messagebox.showerror("エラー", f"お試し再生中にエラーが発生しました: {str(e)}")
            self.logger.error(f"Error in trial playback: {str(e)}", exc_info=True)
    
    def _generate_edl(self):
        """選択されたシーンからEDLファイルを生成"""
        if not self.selected_scenes:
            messagebox.showinfo("情報", "シーンが選択されていません")
            return
        
        try:
            # 保存先の選択
            output_path = filedialog.asksaveasfilename(
                defaultextension=".edl",
                filetypes=[("EDL Files", "*.edl"), ("All Files", "*.*")],
                title="EDLファイルの保存先を選択"
            )
            
            if not output_path:
                return
            
            # EDLファイルの生成
            success = self.editing_agent.generate_edl(self.selected_scenes, output_path)
            
            if success:
                messagebox.showinfo("成功", f"EDLファイルを保存しました: {output_path}")
                self.logger.info(f"Generated EDL file: {output_path}")
            else:
                messagebox.showerror("エラー", "EDLファイルの生成に失敗しました")
            
        except Exception as e:
            messagebox.showerror("エラー", f"EDL生成中にエラーが発生しました: {str(e)}")
            self.logger.error(f"Error generating EDL: {str(e)}", exc_info=True)


def main():
    """メイン関数"""
    root = tk.Tk()
    app = SceneSelectionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main() 