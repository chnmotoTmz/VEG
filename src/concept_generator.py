"""コンセプト生成モジュール"""

from typing import List, Dict, Any
import json
import time
from .api_client import GeminiClient

class ConceptGenerator:
    def __init__(self, api_client: GeminiClient):
        """コンセプト生成器の初期化"""
        self.api_client = api_client
        self.max_retries = 3
        self.retry_delay = 1.0  # 秒

    def generate(self, contents: List[Dict[str, Any]]) -> str:
        """コンテンツからコンセプトを生成"""
        try:
            # コンテンツの特徴を分析
            themes = self._analyze_themes(contents)
            tone = self._analyze_tone(contents)
            
            # 生成AIを使用してコンセプトを生成
            concept = self._generate_concept_with_ai(themes, tone, contents)
            
            return concept
        except Exception as e:
            print(f"警告: コンセプト生成中にエラーが発生しました: {str(e)}")
            return "未分類のコンテンツ"

    def _analyze_themes(self, contents: List[Dict[str, Any]]) -> List[str]:
        """コンテンツからテーマを分析"""
        # コンテンツの概要を準備
        content_summary = self._format_contents_summary(contents)
        
        # プロンプトテンプレート
        prompt = f"""以下のコンテンツから主要なテーマを抽出してください：

コンテンツ概要:
{content_summary}

以下の形式で出力してください：
{{
    "themes": ["テーマ1", "テーマ2", ...],
    "main_theme": "主要テーマ",
    "sub_themes": ["サブテーマ1", "サブテーマ2", ...]
}}"""

        # 生成AIにリクエスト
        response = self.api_client.text_analysis(prompt)
        
        # レスポンスをパース
        try:
            result = json.loads(response)
            return result["themes"]
        except Exception as e:
            print(f"警告: テーマ分析中にエラーが発生しました: {str(e)}")
            return ["未分類"]

    def _analyze_tone(self, contents: List[Dict[str, Any]]) -> str:
        """コンテンツのトーンを分析"""
        # コンテンツの概要を準備
        content_summary = self._format_contents_summary(contents)
        
        # プロンプトテンプレート
        prompt = f"""以下のコンテンツのトーンを分析してください：

コンテンツ概要:
{content_summary}

以下の形式で出力してください：
{{
    "tone": "トーン（positive/negative/neutral）",
    "emotions": ["感情1", "感情2", ...],
    "intensity": "強度（high/medium/low）"
}}"""

        # 生成AIにリクエスト
        response = self.api_client.text_analysis(prompt)
        
        # レスポンスをパース
        try:
            result = json.loads(response)
            return result["tone"]
        except Exception as e:
            print(f"警告: トーン分析中にエラーが発生しました: {str(e)}")
            return "neutral"

    def _generate_concept_with_ai(self, themes: List[str], tone: str, 
                                contents: List[Dict[str, Any]]) -> str:
        """生成AIを使用してコンセプトを生成"""
        # プロンプトテンプレート
        prompt = f"""以下の情報に基づいて、映像作品のコンセプトを生成してください：

テーマ: {', '.join(themes)}
トーン: {tone}

コンテンツ概要:
{self._format_contents_summary(contents)}

以下の形式で出力してください：
{{
    "concept": "コンセプト文",
    "title": "タイトル",
    "description": "詳細な説明",
    "keywords": ["キーワード1", "キーワード2", ...],
    "target_audience": "ターゲット視聴者",
    "style": "映像スタイル"
}}"""

        # 生成AIにリクエスト
        response = self.api_client.text_analysis(prompt)
        
        # レスポンスをパース
        try:
            result = json.loads(response)
            return result["concept"]
        except Exception as e:
            print(f"警告: コンセプト生成中にエラーが発生しました: {str(e)}")
            return "未分類のコンテンツ"

    def _format_contents_summary(self, contents: List[Dict[str, Any]]) -> str:
        """コンテンツの概要をフォーマット"""
        summary = []
        for content in contents:
            # シーンリストが存在するか確認し、空の場合は安全に処理
            scenes = content.get('scenes', [])
            
            # トピックの取得を安全に行う
            topics = []
            if scenes and len(scenes) > 0:
                topics = scenes[0].get('topics', [])
            
            content_summary = f"""
コンテンツID: {content.get('content_id', 'unknown')}
総再生時間: {content.get('total_duration', 0)}秒
シーン数: {len(scenes)}
主なトピック: {', '.join(topics)}
"""
            summary.append(content_summary)
        return '\n'.join(summary)

    def generate_scenario_prompt(self, concept: str) -> str:
        """シナリオ作成プロンプトを生成"""
        # プロンプトテンプレート
        prompt = f"""以下のコンセプトに基づいて、映像作品のシナリオを生成してください：

コンセプト: {concept}

以下の形式で出力してください：
{{
    "title": "作品タイトル",
    "concept": "コンセプト",
    "themes": ["テーマ1", "テーマ2", ...],
    "sections": [
        {{
            "section_id": "セクションID",
            "type": "intro/main/outro",
            "title": "セクションタイトル",
            "description": "セクションの説明",
            "key_messages": ["メッセージ1", "メッセージ2", ...],
            "duration": 推奨時間（秒）,
            "content_ids": ["使用するコンテンツID", ...],
            "effects": ["エフェクト1", ...]
        }},
        ...
    ],
    "narration": {{
        "style": "ナレーションスタイル",
        "tone": "トーン",
        "keywords": ["キーワード1", ...]
    }}
}}"""

        # 生成AIにリクエスト
        response = self.api_client.text_analysis(prompt)
        
        # レスポンスをパース
        try:
            result = json.loads(response)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"警告: シナリオプロンプト生成中にエラーが発生しました: {str(e)}")
            # デフォルトの空のシナリオを返す
            default_scenario = {
                "title": "タイトル未設定",
                "concept": concept,
                "themes": [],
                "sections": []
            }
            return json.dumps(default_scenario, ensure_ascii=False, indent=2)

    def _generate_title(self, topics: List[str], locations: List[str]) -> str:
        """トピックと場所からタイトルを生成"""
        if locations:
            return f"{locations[0]}の{topics[0]}"
        return topics[0]

    def _generate_concept_description(self, topics: List[str], 
                                   locations: List[str], 
                                   duration: float) -> str:
        """コンセプト説明を生成"""
        location_str = "、".join(locations) if locations else "様々な場所"
        topic_str = "、".join(topics)
        minutes = int(duration / 60)
        
        return f"{location_str}で撮影された{topic_str}についての{minutes}分の映像作品です。"
