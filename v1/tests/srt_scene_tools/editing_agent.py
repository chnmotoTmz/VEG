import logging
import json
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass
import os
try:
    # パッケージの一部として実行される場合
    from .utils import Scene
except ImportError:
    # スクリプトとして直接実行される場合
    from utils import Scene

logger = logging.getLogger(__name__)

@dataclass
class SceneMatch:
    """シーンマッチングの結果を表すデータクラス"""
    scene_id: str
    clip_path: str
    video_path: str
    similarity: float
    start_time: float
    end_time: float
    text: str
    metadata: Dict[str, Any] = None

    def __str__(self):
        """文字列表現"""
        return f"Scene: {self.scene_id}, Similarity: {self.similarity:.2f}, Text: {self.text[:30]}..."

    def __lt__(self, other):
        """ソート用の比較演算子（類似度の降順でソート）"""
        return self.similarity > other.similarity


class EditingAgent:
    """
    動画編集支援エージェント
    - シナリオセクションに合うシーンの選択
    - 類似度計算によるシーン提案
    """
    
    def __init__(self, video_data: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """
        編集エージェントの初期化
        
        Args:
            video_data: 単一または複数のビデオデータ
        """
        self.logger = logging.getLogger(__name__)
        
        # 単一のビデオデータの場合はリストに変換
        if isinstance(video_data, dict):
            self.video_data = [video_data]
        else:
            self.video_data = video_data
            
        self.all_scenes = []
        self._load_scenes()
        self.logger.info(f"EditingAgent initialized with {len(self.all_scenes)} scenes from {len(self.video_data)} videos")
    
    def _load_scenes(self):
        """ビデオデータからシーン情報を読み込む"""
        for video in self.video_data:
            video_path = video.get("video_path", "")
            scenes = video.get("scenes", [])
            
            for scene in scenes:
                scene_id = scene.get("id", f"unknown_{len(self.all_scenes)}")
                
                # クリップパスの構築
                clip_path = ""
                if video_path and os.path.exists(video_path):
                    base_dir = os.path.dirname(video_path)
                    clip_filename = f"clip_{scene_id}.mp4"
                    clip_path = os.path.join(base_dir, "clips", clip_filename)
                    # クリップフォルダがなければ作成
                    os.makedirs(os.path.join(base_dir, "clips"), exist_ok=True)
                
                # シーン情報の追加
                self.all_scenes.append({
                    "id": scene_id,
                    "video_path": video_path,
                    "clip_path": clip_path,
                    "start": scene.get("start", 0.0),
                    "end": scene.get("end", 0.0),
                    "duration": scene.get("end", 0.0) - scene.get("start", 0.0),
                    "text": scene.get("text", ""),
                    "transcript": scene.get("transcript", ""),
                    "emotions": scene.get("emotions", {}),
                    "topics": scene.get("topics", []),
                    "metadata": scene.get("metadata", {})
                })
    
    def match_scenes(self, query, limit: int = 5) -> List[SceneMatch]:
        """
        クエリに基づいてシーンをマッチング
        
        Args:
            query: マッチングクエリ
                - 文字列: クエリテキスト
                - 辞書: {
                    "emotion": 感情タイプ,
                    "keywords": キーワードリスト,
                    "scene_type": シーンタイプ
                  }
            limit: 返すマッチの最大数
            
        Returns:
            マッチしたシーンのリスト（類似度順）
        """
        self.logger.info(f"Matching scenes for query: {query}")
        
        # 文字列クエリの場合は辞書に変換
        if isinstance(query, str):
            query_text = query.strip()
            query = {
                "emotion": "",
                "keywords": query_text.split(),
                "scene_type": query_text
            }
        
        emotion = query.get("emotion", "")
        keywords = query.get("keywords", [])
        scene_type = query.get("scene_type", "")
        
        matches = []
        
        for scene in self.all_scenes:
            # テキスト類似度計算
            text_similarity = self._calculate_text_similarity(scene, keywords)
            
            # 感情類似度計算
            emotion_similarity = self._calculate_emotion_similarity(scene, emotion)
            
            # シーンタイプ類似度計算
            type_similarity = self._calculate_type_similarity(scene, scene_type)
            
            # 総合類似度計算（重み付け）
            total_similarity = (text_similarity * 0.6) + (emotion_similarity * 0.3) + (type_similarity * 0.1)
            
            if total_similarity > 0:
                # textフィールドを設定（transcriptが優先、なければtext）
                scene_text = scene.get("transcript", "") or scene.get("text", "")
                
                matches.append(SceneMatch(
                    scene_id=scene["id"],
                    clip_path=scene["clip_path"],
                    video_path=scene["video_path"],
                    similarity=total_similarity,
                    start_time=scene["start"],
                    end_time=scene["end"],
                    text=scene_text,
                    metadata=scene["metadata"]
                ))
        
        # 類似度でソート
        matches.sort()
        
        self.logger.info(f"Found {len(matches)} matching scenes, returning top {min(limit, len(matches))}")
        return matches[:limit]
    
    def _calculate_text_similarity(self, scene: Dict[str, Any], keywords: List[str]) -> float:
        """
        シーンテキストとキーワードの類似度を計算
        
        Args:
            scene: シーン情報
            keywords: キーワードリスト
            
        Returns:
            類似度スコア（0.0～1.0）
        """
        if not keywords:
            return 0.1  # キーワードがない場合は最低スコア
        
        # シーンのテキスト（トランスクリプトと説明を結合）
        transcript = scene.get("transcript", "")
        description = scene.get("description", "")
        scene_text = f"{transcript} {description}".lower()
        
        # 正規化
        import re
        scene_text = re.sub(r'[^\w\s]', '', scene_text)
        scene_words = set(scene_text.split())
        
        # キーワードマッチング
        matched_keywords = 0
        for keyword in keywords:
            keyword = keyword.lower()
            # 完全一致
            if keyword in scene_words:
                matched_keywords += 1
            # 部分一致
            elif keyword in scene_text:
                matched_keywords += 0.5
        
        # 類似度計算
        similarity = matched_keywords / len(keywords)
        
        # トランスクリプトの長さによる調整（短すぎるテキストはスコアを下げる）
        if len(transcript) < 10:
            similarity *= 0.5
        
        self.logger.debug(f"Text similarity for scene {scene.get('id')}: {similarity}")
        return similarity
    
    def _calculate_emotion_similarity(self, scene: Dict[str, Any], target_emotion: str) -> float:
        """
        感情類似度の計算
        
        Args:
            scene: シーン情報
            target_emotion: 目標感情
            
        Returns:
            0.0～1.0の類似度スコア
        """
        if not target_emotion:
            return 0.0
        
        # シーンから感情データを取得
        emotions = scene.get("emotions", {})
        
        # 感情マッピング
        emotion_map = {
            "exciting": ["joy", "surprise", "anticipation"],
            "calm": ["neutral", "calm"],
            "inspiring": ["trust", "joy", "anticipation"],
            "informative": ["neutral", "trust"],
            "humorous": ["joy", "surprise"]
        }
        
        # ターゲット感情に関連する感情リスト
        related_emotions = emotion_map.get(target_emotion.lower(), [])
        
        if not related_emotions or not emotions:
            return 0.0
        
        # 関連感情のスコアを合計
        total_score = sum(emotions.get(emotion, 0.0) for emotion in related_emotions)
        max_possible = len(related_emotions)
        
        return min(total_score / max_possible, 1.0) if max_possible > 0 else 0.0
    
    def _calculate_type_similarity(self, scene: Dict[str, Any], scene_type: str) -> float:
        """
        シーンタイプの類似度計算
        
        Args:
            scene: シーン情報
            scene_type: 目標シーンタイプ
            
        Returns:
            0.0～1.0の類似度スコア
        """
        if not scene_type:
            return 0.0
        
        # テキストベースの簡易判定
        text = scene.get("text", "").lower()
        duration = scene.get("duration", 0.0)
        
        type_indicators = {
            "establishing": ["紹介", "導入", "風景", "全体", "概要"],
            "action": ["行動", "動き", "走る", "移動", "アクション"],
            "closeup": ["接写", "詳細", "クローズアップ", "表情"],
            "interview": ["会話", "話す", "インタビュー", "説明"],
            "montage": ["連続", "まとめ", "ハイライト"]
        }
        
        # シーンタイプに関連するキーワード
        keywords = type_indicators.get(scene_type.lower(), [])
        
        # キーワードマッチによる類似度
        matches = sum(1 for keyword in keywords if keyword in text)
        
        # 長さに基づく補正
        # エスタブリッシングショットは長め、クローズアップは短め
        duration_factor = 0.0
        if scene_type.lower() == "establishing" and duration > 5.0:
            duration_factor = 0.3
        elif scene_type.lower() == "closeup" and duration < 3.0:
            duration_factor = 0.3
        elif scene_type.lower() == "action" and 2.0 < duration < 10.0:
            duration_factor = 0.3
        elif scene_type.lower() == "montage" and duration < 2.0:
            duration_factor = 0.3
        
        keyword_factor = (matches / len(keywords)) * 0.7 if keywords else 0.0
        
        return keyword_factor + duration_factor
    
    def generate_preview_clip(self, scene_match: SceneMatch) -> str:
        """
        シーンのプレビュークリップを生成
        
        Args:
            scene_match: マッチしたシーン情報
            
        Returns:
            生成されたクリップのパス
        """
        # まず、シーンに関連するビデオデータを検索
        for video in self.video_data:
            video_path = video.get("video_path", "")
            scenes = video.get("scenes", [])
            
            for scene in scenes:
                scene_id = scene.get("id", "")
                
                # シーンIDが一致する場合
                if str(scene_id) == str(scene_match.scene_id):
                    # プレビューパスをチェック
                    preview_path = scene.get("preview_path", "")
                    json_path = video.get("json_path", "")
                    
                    if preview_path:
                        # パスの調整（相対パスを絶対パスに変換）
                        if not os.path.isabs(preview_path):
                            # jsonファイルが存在する場合、そのディレクトリを基準にする
                            if json_path and os.path.exists(json_path):
                                base_dir = os.path.dirname(json_path)
                                preview_path = os.path.join(base_dir, preview_path)
                            # ビデオパスが存在する場合、そのディレクトリを基準にする
                            elif video_path and os.path.exists(video_path):
                                base_dir = os.path.dirname(video_path)
                                preview_path = os.path.join(base_dir, preview_path)
                        
                        # プレビューファイルが存在するか確認
                        if os.path.exists(preview_path):
                            self.logger.info(f"Found preview clip: {preview_path}")
                            return preview_path
                        else:
                            self.logger.warning(f"Preview path found but file does not exist: {preview_path}")
        
        # プレビューが見つからない場合、クリップパスを生成する
        if not os.path.exists(scene_match.clip_path) and scene_match.video_path and os.path.exists(scene_match.video_path):
            # クリップが存在しない場合、元の動画から切り出す処理をここに実装
            # この例では、FFmpegを使用する前提
            try:
                import subprocess
                source_video = scene_match.video_path
                start_time = scene_match.start_time
                duration = scene_match.end_time - scene_match.start_time
                
                # クリップディレクトリの作成
                os.makedirs(os.path.dirname(scene_match.clip_path), exist_ok=True)
                
                cmd = [
                    "ffmpeg", "-i", source_video,
                    "-ss", str(start_time),
                    "-t", str(duration),
                    "-c:v", "copy", "-c:a", "copy",
                    scene_match.clip_path
                ]
                
                subprocess.run(cmd, check=True)
                self.logger.info(f"Generated preview clip: {scene_match.clip_path}")
                
                return scene_match.clip_path
                
            except Exception as e:
                self.logger.error(f"Error generating preview clip: {e}")
        
        self.logger.warning(f"Could not find or generate preview for scene: {scene_match.scene_id}")
        return ""
    
    def generate_edl(self, selected_scenes: List[SceneMatch], output_path: str) -> bool:
        """
        選択されたシーンからEDLファイルを生成
        
        Args:
            selected_scenes: 選択されたシーンのリスト
            output_path: 出力EDLファイルのパス
            
        Returns:
            成功したかどうか
        """
        try:
            edl_lines = ["TITLE: Auto-Generated EDL\nFCM: NON-DROP FRAME\n\n"]
            reel = "TAPE01"
            
            # GoPro開始時間を取得（最初のビデオから）
            gopro_start_time = None
            if self.video_data and len(self.video_data) > 0:
                gopro_start_time = self.video_data[0].get("gopro_start_time", None)
            
            for i, scene in enumerate(selected_scenes):
                # シーンIDからソースビデオを特定
                source_video = ""
                for video in self.video_data:
                    for s in video.get("scenes", []):
                        if s.get("id") == scene.scene_id:
                            source_video = os.path.basename(video.get("video_path", f"CLIP_{i+1}"))
                            break
                
                # EDLエントリの作成
                start_timecode = self._format_timecode(scene.start_time)
                end_timecode = self._format_timecode(scene.end_time)
                rec_start = self._format_timecode(sum(s.end_time - s.start_time for s in selected_scenes[:i]))
                rec_end = self._format_timecode(sum(s.end_time - s.start_time for s in selected_scenes[:i+1]))
                
                edl_lines.append(
                    f"{i+1:03d}  {reel}   V     C        "
                    f"{start_timecode} {end_timecode} "
                    f"{rec_start} {rec_end}\n"
                    f"* FROM CLIP NAME: {source_video}\n\n"
                )
            
            # EDLファイルの書き込み
            with open(output_path, "w", encoding="utf-8") as f:
                f.writelines(edl_lines)
            
            self.logger.info(f"Generated EDL file: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating EDL file: {e}")
            return False
    
    def _format_timecode(self, seconds: float) -> str:
        """
        秒数をタイムコード形式（HH:MM:SS:FF）に変換
        
        Args:
            seconds: 秒数
            
        Returns:
            タイムコード文字列
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        frames = int((seconds % 1) * 30)  # 30fpsと仮定
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}:{frames:02d}"
    
    def filter_scenes_by_duration(self, min_duration: float = 1.0, max_duration: float = 30.0) -> List[Dict[str, Any]]:
        """
        指定された長さ範囲内のシーンをフィルタリング
        
        Args:
            min_duration: 最小シーン長（秒）
            max_duration: 最大シーン長（秒）
            
        Returns:
            フィルタリングされたシーンのリスト
        """
        filtered_scenes = []
        
        for scene in self.all_scenes:
            duration = scene.get("duration", 0.0)
            if min_duration <= duration <= max_duration:
                filtered_scenes.append(scene)
        
        return filtered_scenes
    
    def get_scene_by_id(self, scene_id: str) -> Optional[Dict[str, Any]]:
        """
        IDによるシーンの取得
        
        Args:
            scene_id: シーンID
            
        Returns:
            シーン情報（見つからない場合はNone）
        """
        for scene in self.all_scenes:
            if scene["id"] == scene_id:
                return scene
        return None 