import re
import os
import json
import logging
from typing import List, Dict, Any

class LanguageHandler:
    """Handles language code conversions."""

    def __init__(self):
        # Initialize language mapping (extend as needed)
        self.language_map = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
            # Add more languages as needed
        }

    def glc(self, lnm: str) -> str:
        lnm = lnm.strip().title()
        return self.language_map.get(lnm)


class Scene:
    """Represents a scene in an SRT file."""

    def __init__(self, start_time: str, end_time: str, text: str, video_id: str = None):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.narration = ""  # Store narration for this scene
        self.st = start_time  # 互換性のために保持
        self.et = end_time    # 互換性のために保持
        self.txt = text       # 互換性のために保持
        self.nar = ""         # 互換性のために保持
        self.video_id = video_id  # 動画の識別子

    def app_nar(self, narration: str):
        self.narration += narration + "\n"  # Add newline for readability
        self.text += "\n" + narration  # Append to original text
        self.nar = self.narration      # 互換性のために保持
        self.txt = self.text           # 互換性のために保持

    def __str__(self):
        return f"Start: {self.start_time}, End: {self.end_time}, Text: {self.text}"


class ContentCrawler:
    """Crawls through a directory to find and process video content and metadata."""
    
    def __init__(self, folder_path: str):
        """
        初期化処理
        
        Args:
            folder_path: 処理するフォルダのパス
        """
        self.folder_path = folder_path
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)  # ログレベルをDEBUGに設定
        self.logger.info(f"ContentCrawler initialized for folder: {folder_path}")
    
    def crawl(self) -> List[Dict[str, Any]]:
        """
        フォルダ内のvideo_nodes_*ディレクトリからJSONデータを取得
        
        Returns:
            フォルダ内のビデオコンテンツとメタデータのリスト
        """
        contents = []
        
        try:
            # デバッグ: フォルダの内容を表示
            self.logger.debug(f"フォルダパス: {self.folder_path}")
            self.logger.debug(f"フォルダ内のファイル: {os.listdir(self.folder_path)}")
            
            # video_nodes_* ディレクトリの検索
            for item in os.listdir(self.folder_path):
                item_path = os.path.join(self.folder_path, item)
                if item.startswith("video_nodes_") and os.path.isdir(item_path):
                    self.logger.debug(f"Processing directory: {item_path}")
                    json_path = os.path.join(item_path, "nodes.json")
                    
                    if not os.path.exists(json_path):
                        self.logger.warning(f"nodes.json not found in {item_path}")
                        continue
                        
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # データの検証
                        if "scenes" not in data:
                            self.logger.warning(f"No scenes field in {json_path}")
                            continue
                            
                        contents.append(data)
                        self.logger.debug(f"Successfully loaded {json_path}")
                        
                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON decode error in {json_path}: {e}")
                    except UnicodeDecodeError as e:
                        self.logger.error(f"Unicode decode error in {json_path}: {e}")
                        # Try with different encodings
                        for encoding in ['shift-jis', 'cp932', 'euc-jp']:
                            try:
                                with open(json_path, 'r', encoding=encoding) as f:
                                    data = json.load(f)
                                contents.append(data)
                                self.logger.info(f"Successfully loaded {json_path} with {encoding}")
                                break
                            except:
                                continue
                    except Exception as e:
                        self.logger.error(f"Error processing {json_path}: {e}")
                        
            self.logger.info(f"Found {len(contents)} content items")
            return contents
            
        except Exception as e:
            self.logger.error(f"Error crawling directory: {e}", exc_info=True)
            return []
    
    def _process_json(self, json_path: str) -> Dict[str, Any]:
        """
        JSONファイルからコンテンツデータを抽出
        
        Args:
            json_path: JSONファイルのパス
            
        Returns:
            処理されたコンテンツデータ
        """
        try:
            self.logger.info(f"Processing JSON file: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # JSONデータのキーを確認（デバッグ用）
            self.logger.debug(f"JSON keys: {list(data.keys())}")
            
            # シーンデータの確認（デバッグ用）
            scenes = data.get("scenes", [])
            
            # 優先順位を付けてデータを抽出
            title = (
                data.get("title") or 
                data.get("metadata", {}).get("filename") or
                os.path.splitext(os.path.basename(json_path))[0]
            )
            
            # ビデオの長さを確認
            metadata = data.get("metadata", {})
            
            # 複数のソースから動画の長さを取得
            duration = 0
            # 1. metadata.durationから取得
            if metadata.get("duration", 0) > 0:
                duration = metadata.get("duration", 0)
            # 2. summary.total_durationから取得
            elif data.get("summary", {}).get("total_duration", 0) > 0:
                duration = data.get("summary", {}).get("total_duration", 0)
            # 3. シーンの合計時間から計算
            elif scenes:
                # 最後のシーンのend時間を取得
                last_scene = scenes[-1]
                duration = last_scene.get("end", 0)
                if duration == 0 and "duration" in last_scene:
                    # 全シーンのdurationを合計
                    duration = sum(scene.get("duration", 0) for scene in scenes)
            
            self.logger.debug(f"動画の長さ: {duration}秒")
            
            # サマリー情報を抽出
            summary = data.get("summary", {})
            if isinstance(summary, str):
                overview = summary
                topics = []
                location = ""
            else:
                overview = summary.get("overview", "")
                topics = summary.get("topics", [])
                location = summary.get("location", "")
                
                # トピックが空の場合、他のソースから抽出を試みる
                if not topics:
                    # 1. シーンのcontext_analysisから抽出
                    for scene in scenes:
                        context = scene.get("context_analysis", {})
                        if context:
                            # 環境情報を追加
                            env = context.get("environment", [])
                            if env:
                                topics.extend(env)
                            # 活動情報を追加
                            act = context.get("activity", [])
                            if act:
                                topics.extend(act)
                    
                    # 2. シーンのdescriptionから抽出（英語のキーワード除去）
                    if not topics:
                        stop_words = ["the", "a", "and", "in", "on", "at", "to", "for", "of", "with", "by"]
                        for scene in scenes:
                            desc = scene.get("description", "")
                            if desc:
                                # 単語に分割（句読点などを除去）
                                import re
                                words = re.findall(r'\b\w+\b', desc.lower())
                                # 短すぎる単語と一般的な単語を除去
                                keywords = [w for w in words if len(w) > 3 and w not in stop_words]
                                topics.extend(keywords[:5])  # 最大5語
                
                # locationが空の場合、context_analysisから抽出
                if not location and scenes:
                    for scene in scenes:
                        context = scene.get("context_analysis", {})
                        if context:
                            loc_type = context.get("location_type", "")
                            if loc_type:
                                location = loc_type
                                break
                            
                            # 環境情報から場所を推測
                            env = context.get("environment", [])
                            for e in env:
                                if any(place in e.lower() for place in ["山", "河", "海", "屋外", "屋内", "室内", "バス", "車", "室外"]):
                                    location = e
                                    break
            
            # 重複を削除してリストを整形
            if topics:
                topics = list(set(topics))
            
            # シーンが無い場合は、動画全体を1つのシーンとして扱う
            if not scenes and duration > 0:
                self.logger.warning(f"シーンデータがないため、動画全体を1つのシーンとして処理します: {json_path}")
                scenes = [{
                    "id": 0,
                    "start": 0,
                    "end": duration,
                    "duration": duration,
                    "transcript": overview,
                    "description": overview
                }]
            
            # 各シーンのduration値を確認し、ない場合は計算する
            for scene in scenes:
                if "duration" not in scene and "start" in scene and "end" in scene:
                    scene["duration"] = scene["end"] - scene["start"]
            
            content = {
                "title": title,
                "overview": overview,
                "topics": topics,
                "location": location,
                "total_duration": duration,
                "scenes": scenes,
                "metadata": metadata,
                "gopro_start_time": summary.get("gopro_start_time", "") if isinstance(summary, dict) else "",
                "json_path": json_path,
                "video_path": metadata.get("filepath", "")
            }
            
            # 処理結果の詳細をログに出力
            self.logger.info(f"Processed content: title={content['title']}, "
                           f"scenes={len(content['scenes'])}, "
                           f"duration={content['total_duration']}, "
                           f"topics={content['topics'][:3] if content['topics'] else []}, "
                           f"location={content['location']}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error processing JSON file {json_path}: {e}", exc_info=True)
            return {}
