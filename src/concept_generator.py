"""コンセプト生成モジュール"""

import os
import json
from typing import Dict, Any, List, Optional
import random
from .evolve_chip import EvolveChip

class TopicExtractor:
    """コンテンツからトピック（キーワード）を抽出するクラス"""
    
    def extract_topics(self, contents: Dict[str, Any]) -> List[str]:
        """
        コンテンツからトピックを抽出
        
        Args:
            contents: 解析されたコンテンツ情報
            
        Returns:
            抽出されたトピックのリスト
        """
        topics = []
        
        # 動画ノードからキーワードを抽出
        for video_file, video_data in contents.get('videos', {}).items():
            for scene in video_data.get('scenes', []):
                for tag in scene.get('tags', []):
                    if tag not in topics:
                        topics.append(tag)
        
        # トピックが少ない場合はデフォルトトピックを追加
        if len(topics) < 3:
            default_topics = ["自然", "風景", "日常", "旅行", "文化", "アドベンチャー"]
            for topic in default_topics:
                if topic not in topics:
                    topics.append(topic)
                    if len(topics) >= 5:
                        break
        
        return topics


class LocationExtractor:
    """コンテンツから場所情報を抽出するクラス"""
    
    def extract_locations(self, contents: Dict[str, Any]) -> List[str]:
        """
        コンテンツから場所情報を抽出
        
        Args:
            contents: 解析されたコンテンツ情報
            
        Returns:
            抽出された場所のリスト
        """
        locations = []
        
        # 動画メタデータから場所情報を抽出
        for video_file, video_data in contents.get('videos', {}).items():
            location = video_data.get('metadata', {}).get('location')
            if location and location not in locations:
                locations.append(location)
        
        # 場所情報がない場合はデフォルト値を使用
        if not locations:
            locations = ["様々な場所"]
        
        return locations


class ContentAnalyzer:
    """コンテンツの特性を分析するクラス"""
    
    def calculate_total_duration(self, contents: Dict[str, Any]) -> float:
        """
        コンテンツの合計時間を計算
        
        Args:
            contents: 解析されたコンテンツ情報
            
        Returns:
            合計時間（秒）
        """
        total_duration = 0.0
        
        for video_file, video_data in contents.get('videos', {}).items():
            duration = video_data.get('metadata', {}).get('duration', 0)
            total_duration += float(duration)
        
        return total_duration
    
    def determine_content_type(self, contents: Dict[str, Any]) -> str:
        """
        コンテンツタイプを判定
        
        Args:
            contents: 解析されたコンテンツ情報
            
        Returns:
            判定されたコンテンツタイプ
        """
        # 動画のシーン数から判定
        scene_count = 0
        fast_scene_count = 0
        
        for video_file, video_data in contents.get('videos', {}).items():
            scenes = video_data.get('scenes', [])
            scene_count += len(scenes)
            
            for scene in scenes:
                duration = scene.get('end_time', 0) - scene.get('start_time', 0)
                if duration < 3.0:  # 3秒未満のシーンは速いシーンとみなす
                    fast_scene_count += 1
        
        # 速いシーンの割合で判定
        if scene_count > 0:
            fast_ratio = fast_scene_count / scene_count
            if fast_ratio > 0.5:
                return "アクション/ダイナミック"
            elif fast_ratio > 0.3:
                return "バランス"
            else:
                return "ドキュメンタリー/スローペース"
        
        return "一般"
    
    def determine_target_audience(self, topics: List[str]) -> str:
        """
        ターゲットオーディエンスを判定
        
        Args:
            topics: トピックのリスト
            
        Returns:
            想定されるターゲットオーディエンス
        """
        # キーワードベースでターゲットを推定
        nature_keywords = ["自然", "風景", "山", "海", "川", "動物"]
        adventure_keywords = ["アドベンチャー", "スポーツ", "アクション", "挑戦"]
        culture_keywords = ["文化", "歴史", "伝統", "芸術", "食"]
        
        nature_count = sum(1 for t in topics if t in nature_keywords)
        adventure_count = sum(1 for t in topics if t in adventure_keywords)
        culture_count = sum(1 for t in topics if t in culture_keywords)
        
        max_count = max(nature_count, adventure_count, culture_count)
        
        if max_count == nature_count:
            return "自然愛好家と旅行者"
        elif max_count == adventure_count:
            return "アドベンチャー志向の視聴者"
        elif max_count == culture_count:
            return "文化や歴史に興味がある視聴者"
        else:
            return "一般視聴者"


class ConceptBuilder:
    """コンセプトを生成、構築するクラス"""
    
    def __init__(self):
        """コンストラクタ"""
        self.title_templates = [
            "「{keyword}」で見る{location}の魅力",
            "{location}の{keyword}を探る旅",
            "{location}で出会った{keyword}の世界",
            "{keyword}から考える{location}の今",
            "未知なる{location}の{keyword}",
            "{location}の隠された{keyword}",
            "{keyword}が変える{location}の姿"
        ]
    
    def generate_title(self, topics: List[str], locations: List[str], style: str) -> str:
        """
        タイトルを生成
        
        Args:
            topics: トピックのリスト
            locations: 場所のリスト
            style: タイトルのスタイル
            
        Returns:
            生成されたタイトル
        """
        if not topics or not locations:
            return "映像プロジェクト"
        
        keyword = random.choice(topics[:3]) if len(topics) >= 3 else topics[0]
        location = random.choice(locations)
        
        template = random.choice(self.title_templates)
        title = template.format(keyword=keyword, location=location)
        
        # スタイルに基づく修飾
        if style == "dramatic":
            title = f"衝撃の{title}"
        elif style == "emotional":
            title = f"心に響く{title}"
        elif style == "informative":
            title = f"徹底解説！{title}"
        
        return title
    
    def generate_concept_description(self, topics: List[str], 
                              locations: List[str],
                              duration: float) -> str:
        """
        コンセプト説明文を生成
        
        Args:
            topics: トピックのリスト
            locations: 場所のリスト
            duration: 動画の合計時間（秒）
            
        Returns:
            生成されたコンセプト説明文
        """
        location_str = "、".join(locations) if locations else "様々な場所"
        topic_str = "、".join(topics)
        minutes = int(duration / 60)

        return f"{location_str}で撮影された{topic_str}についての{minutes}分の映像作品です。"
    
    def generate_style_suggestions(self, topics: List[str], params: Dict[str, Any]) -> List[str]:
        """
        スタイル提案を生成
        
        Args:
            topics: トピックのリスト
            params: 生成パラメータ
            
        Returns:
            スタイル提案のリスト
        """
        suggestions = []
        
        # トピックに基づく提案
        if "自然" in topics or "風景" in topics:
            suggestions.append("ワイドショットで風景の壮大さを表現")
        
        if "動物" in topics or "生き物" in topics:
            suggestions.append("被写体の動きに焦点を当てた編集")
        
        if "文化" in topics or "歴史" in topics:
            suggestions.append("ゆっくりとしたペースで文化的背景を解説")
        
        # 基本的な提案を追加
        base_suggestions = [
            "色調補正で統一感を出す",
            "BGMは場面に合わせて変化をつける",
            "重要なシーンではスローモーションを効果的に使用"
        ]
        
        # カスタムスタイルのパラメータを適用
        custom_style = params.get('style', '')
        if custom_style == "cinematic":
            suggestions.append("シネマティックな映像比率（2.35:1）を使用")
            suggestions.append("映画的な色調補正と明暗のコントラスト")
        elif custom_style == "documentary":
            suggestions.append("解説ナレーションを追加")
            suggestions.append("インタビューカットを入れる")
        
        # 提案を結合して返す
        return suggestions + [s for s in base_suggestions if s not in suggestions]


class ConceptGenerator:
    """映像コンテンツからコンセプトを生成するクラス"""
    
    def __init__(self):
        """コンストラクタ"""
        self.topic_extractor = TopicExtractor()
        self.location_extractor = LocationExtractor()
        self.content_analyzer = ContentAnalyzer()
        self.concept_builder = ConceptBuilder()
    
    @EvolveChip
    def generate(self, contents: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        コンテンツからコンセプトを生成
        
        Args:
            contents: 解析されたコンテンツ情報
            params: 生成パラメータ
            
        Returns:
            生成されたコンセプト情報
        """
        if params is None:
            params = {}
        
        # コンテンツから情報を抽出
        topics = self.topic_extractor.extract_topics(contents)
        locations = self.location_extractor.extract_locations(contents)
        duration = self.content_analyzer.calculate_total_duration(contents)
        
        # タイトル生成
        title = self.concept_builder.generate_title(topics, locations, params.get('title_style', 'standard'))
        
        # コンセプト説明文生成
        description = self.concept_builder.generate_concept_description(topics, locations, duration)
        
        # コンセプトの構造を生成
        concept = {
            'title': title,
            'description': description,
            'keywords': topics[:5],  # 上位5つのキーワードを含める
            'locations': locations,
            'duration': duration,
            'content_type': self.content_analyzer.determine_content_type(contents),
            'target_audience': self.content_analyzer.determine_target_audience(topics),
            'style_suggestions': self.concept_builder.generate_style_suggestions(topics, params)
        }
        
        return concept
    
    def save_concept(self, concept: Dict[str, Any], file_path: str) -> None:
        """
        生成したコンセプトをファイルに保存
        
        Args:
            concept: 生成されたコンセプト情報
            file_path: 保存先のファイルパス
        """
        # 出力ディレクトリを作成
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # ファイルに書き出し
        with open(file_path, 'w', encoding='utf-8-sig') as f:
            json.dump(concept, f, ensure_ascii=False, indent=2) 