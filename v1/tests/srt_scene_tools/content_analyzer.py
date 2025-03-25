import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import glob
import re

# ロガーの設定
logger = logging.getLogger(__name__)

# .envファイルの読み込み
load_dotenv()

# API設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Gemini API設定
genai.configure(api_key=GEMINI_API_KEY)
logger.info("Gemini 1.5 Flashモデルの設定が完了しました")

@dataclass
class VideoContent:
    title: str
    overview: str
    topics: List[str]
    filming_date: str
    location: str
    purpose: str
    scene_count: int
    total_duration: float
    environments: List[str]
    notable_views: List[str]

class ContentCrawler:
    """ビデオノードをクロールしてVideoContentオブジェクトを生成するクラス"""
    
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        logger.info(f"ContentCrawler initialized with folder: {folder_path}")
        
    def crawl(self) -> List[VideoContent]:
        """フォルダ内のvideo_nodes_*ディレクトリをクロールしてVideoContentオブジェクトを生成"""
        contents = []
        error_count = 0
        success_count = 0
        try:
            # フォルダ内のvideo_nodes_*ディレクトリを検索
            for item in os.listdir(self.folder_path):
                if item.startswith('video_nodes_') and os.path.isdir(os.path.join(self.folder_path, item)):
                    node_file = os.path.join(self.folder_path, item, 'nodes.json')
                    if os.path.exists(node_file):
                        try:
                            with open(node_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                try:
                                    content = self._parse_video_content(data)
                                    if content:
                                        contents.append(content)
                                        success_count += 1
                                        logger.info(f"成功: {node_file} のパース完了")
                                except Exception as e:
                                    error_count += 1
                                    if "429 Resource has been exhausted" in str(e):
                                        # APIクォータエラーの場合は基本情報だけで作成を試みる
                                        try:
                                            content = self._create_basic_video_content(data)
                                            if content:
                                                contents.append(content)
                                                success_count += 1
                                                logger.info(f"基本情報のみで作成: {node_file}")
                                        except Exception as inner_e:
                                            logger.error(f"基本情報作成失敗: {node_file}: {inner_e}")
                                    else:
                                        logger.error(f"Error parsing video content in {node_file}: {e}")
                        except Exception as e:
                            error_count += 1
                            logger.error(f"Error parsing {node_file}: {e}")
            
            logger.info(f"Found {len(contents)} video contents (成功: {success_count}, エラー: {error_count})")
            return contents
        except Exception as e:
            logger.error(f"Error during crawling: {e}")
            raise
    
    def _parse_video_content(self, data: Dict) -> VideoContent:
        """nodes.jsonからVideoContentオブジェクトを生成"""
        try:
            # ビデオパスからタイトルを抽出
            video_path = data.get('video_path', '')
            title = os.path.splitext(os.path.basename(video_path))[0] if video_path else ''

            # シーンからの情報抽出
            scenes = data.get('scenes', [])
            if not scenes:
                raise ValueError("No scenes found in the data")

            # シーンのトランスクリプトを結合して概要を生成
            transcripts = [scene.get('transcript', '') for scene in scenes if scene.get('transcript')]
            
            if not transcripts:
                logger.warning(f"{title}: トランスクリプトが見つかりません")
                overview = "トランスクリプトなし"
                # トランスクリプトがない場合でも基本情報を使用してコンテンツを生成
                return self._create_basic_video_content(data)
            
            overview = ' '.join(transcripts) if transcripts else ''  # すべてのシーンのトランスクリプトを結合

            # LLMを使用してトピック、場所、目的を抽出
            content_info = self._extract_content_info_with_llm(transcripts, title)
            topics = content_info.get('topics', [])
            location = content_info.get('location', '')
            purpose = content_info.get('purpose', '')

            # 撮影日時の取得
            filming_date = ''
            gopro_start_time = data.get('summary', {}).get('gopro_start_time', '')
            if gopro_start_time:
                try:
                    filming_date = datetime.fromisoformat(gopro_start_time.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except ValueError:
                    pass

            # シーン数と総時間の計算
            scene_count = len(scenes)
            total_duration = sum(scene.get('duration', 0) for scene in scenes)

            # 環境情報の取得
            landscape_summary = data.get('summary', {}).get('landscape_summary', {})
            environments = landscape_summary.get('main_environments', [])
            notable_views = landscape_summary.get('notable_views', [])

            return VideoContent(
                title=title,
                overview=overview[:200] + '...' if len(overview) > 200 else overview,  # 概要は200文字まで
                topics=topics,
                filming_date=filming_date,
                location=location,
                purpose=purpose,
                scene_count=scene_count,
                total_duration=total_duration,
                environments=environments,
                notable_views=notable_views
            )
        except Exception as e:
            logger.error(f"Error parsing video content: {e}")
            raise

    def _extract_content_info_with_llm(self, transcripts: List[str], title: str) -> Dict:
        """LLMを使用してトランスクリプトからトピック、場所、目的を抽出"""
        # トランスクリプトが少ない場合も処理を続行
        if not transcripts:
            logger.warning(f"{title}: トランスクリプトが不足しています - デフォルト値を使用します")
            return {
                "topics": ["動画記録"],
                "location": "不明",
                "purpose": "記録"
            }
            
        # プロンプトの作成
        full_text = ' '.join(transcripts)  # すべてのトランスクリプトを使用
        # テキストが長すぎる場合は先頭から1000文字に制限
        if len(full_text) > 1000:
            full_text = full_text[:1000] + "..."
            
        prompt = f"""
動画のトランスクリプトと題名から、この動画のトピック、撮影場所、目的を分析してください。
コンテキストを理解し、最も適切な情報を抽出してください。

動画タイトル: {title}
トランスクリプト: 
{full_text}

必ず以下のJSONのみをレスポンスとして返してください。説明文やマークダウン記法は使用しないでください:
{{
  "topics": ["トピック1", "トピック2"],
  "location": "撮影場所",
  "purpose": "撮影目的"
}}

トピックは、動画の主要なテーマを示す単語やフレーズです。例：山登り、観光、旅行、家族イベント、アイドルコンサート、料理、スポーツなど
場所は、動画が撮影された具体的な地名や施設名です。例：大山、東京駅、ディズニーランド、自宅など
目的は、動画の撮影意図です。例：登山記録、観光記録、イベント記録、家族記録など

特に、トランスクリプトに地名や施設名が含まれている場合は、それを「location」として必ず抽出してください。
"""

        try:
            # Gemini 1.5 Flashを使用して分析
            model = self.genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            try:
                # レスポンスからJSONを抽出
                return self._extract_json_from_llm_response(response.text)
            except json.JSONDecodeError as e:
                logger.error(f"JSONデコードエラー: {str(e)}")
                # JSONデコードエラーの場合は単純な抽出を試みる
                return self._extract_basic_info_from_text(full_text, title)
        except Exception as e:
            logger.error(f"LLM分析エラー: {e}")
            return self._extract_basic_info_from_text(full_text, title)

    def _extract_basic_info_from_text(self, text: str, title: str) -> Dict:
        """テキストから基本的な情報を抽出するフォールバックメソッド"""
        # 旅行関連のキーワード
        travel_keywords = ["旅行", "観光", "駅", "電車", "バス", "飛行機", "ホテル", "旅館"]
        
        # 場所に関連する一般的な単語（駅名や地名を含む）
        location_keywords = ["東京", "横浜", "大阪", "名古屋", "京都", "札幌", "福岡", "仙台", 
                           "駅", "空港", "港", "山", "湖", "川", "海", "公園"]
        
        # キーワードマッチング
        topics = []
        if any(keyword in text for keyword in travel_keywords):
            topics.append("旅行")
        
        if "電車" in text or "列車" in text or "鉄道" in text:
            topics.append("鉄道")
            
        if "観光" in text:
            topics.append("観光")
            
        if len(topics) == 0:
            topics = ["動画記録"]
            
        # 場所の検出（単純な文字列マッチング）
        location = "不明"
        for keyword in location_keywords:
            if keyword in text:
                location = keyword
                break
                
        return {
            "topics": topics,
            "location": location,
            "purpose": "記録"
        }

    def _create_basic_video_content(self, data: Dict) -> VideoContent:
        """APIエラー時など、基本情報だけでVideoContentを作成する"""
        try:
            # ビデオパスからタイトルを抽出
            video_path = data.get('video_path', '')
            title = os.path.splitext(os.path.basename(video_path))[0] if video_path else 'Unknown'

            # シーンからの基本情報抽出
            scenes = data.get('scenes', [])
            scene_count = len(scenes)
            total_duration = sum(scene.get('duration', 0) for scene in scenes)

            # シーンのトランスクリプトがあれば結合して概要を生成
            transcripts = [scene.get('transcript', '') for scene in scenes if scene.get('transcript')]
            overview = ' '.join(transcripts[:3]) if transcripts else 'No transcript available'

            # 撮影日時の取得
            filming_date = ''
            gopro_start_time = data.get('summary', {}).get('gopro_start_time', '')
            if gopro_start_time:
                try:
                    filming_date = datetime.fromisoformat(gopro_start_time.replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except ValueError:
                    pass

            # 環境情報の取得
            landscape_summary = data.get('summary', {}).get('landscape_summary', {})
            environments = landscape_summary.get('main_environments', [])
            notable_views = landscape_summary.get('notable_views', [])

            # ファイル名から基本的な情報を推測
            location = data.get('summary', {}).get('location', 'Unknown')
            
            return VideoContent(
                title=title,
                overview=overview[:200] + '...' if len(overview) > 200 else overview,
                topics=["GoPro", "動画"],  # デフォルトのトピック
                filming_date=filming_date,
                location=location,
                purpose="記録",  # デフォルトの目的
                scene_count=scene_count,
                total_duration=total_duration,
                environments=environments,
                notable_views=notable_views
            )
        except Exception as e:
            logger.error(f"Error creating basic video content: {e}")
            raise

def _extract_json_from_text(text: str) -> str:
    """テキストからJSON部分を抽出する"""
    # マークダウンコードブロックが含まれている場合は除去
    if "```json" in text or "```" in text:
        # マークダウンブロックからJSONを抽出
        pattern = r"```(?:json)?(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()
        else:
            # マークダウンブロックがなければバックティックを削除
            text = text.replace("```json", "").replace("```", "").strip()
    
    # それでもJSONが抽出できない場合は、テキスト全体から最初の有効なJSONを探す
    if not text.strip().startswith("{"):
        json_pattern = r'({[\s\S]*})'
        json_match = re.search(json_pattern, text)
        if json_match:
            return json_match.group(1)
    
    return text.strip()

class ConceptGenerator:
    """コンテンツ群から共通のコンセプトを抽出するクラス"""
    
    def __init__(self):
        # Gemini APIクライアントの初期化
        self.genai = genai
        
        # APIキーの設定
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY環境変数が設定されていません。デモモードで動作します。")
        else:
            self.genai.configure(api_key=api_key)
        
        logger.info("Gemini 1.5 Flashモデルを初期化しました")

    def _extract_json_from_llm_response(self, response_text: str) -> Dict:
        """LLMレスポンスからJSONオブジェクトを抽出して返す"""
        try:
            # レスポンスからJSONを抽出
            logger.debug(f"LLMレスポンス: {response_text}")
            
            # JSON部分を抽出
            json_text = _extract_json_from_text(response_text)
            
            try:
                # 通常の解析を試す
                return json.loads(json_text)
            except json.JSONDecodeError:
                # 特殊文字を削除してもう一度試す
                cleaned_text = re.sub(r'[^\x00-\x7F]+', '', json_text)
                return json.loads(cleaned_text)
        except Exception as e:
            logger.error(f"JSON抽出エラー: {e}")
            raise json.JSONDecodeError(f"JSONの抽出と解析に失敗しました: {e}", "", 0)
            
    def _analyze_with_llm(self, prompt: str) -> Dict:
        """LLMを使用して分析を実行"""
        try:
            # Gemini 1.5 Flashを使用して分析
            model = self.genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            
            try:
                # レスポンスからJSONを抽出
                return self._extract_json_from_llm_response(response.text)
            except json.JSONDecodeError:
                logger.error(f"LLMによる分析中にJSONデコードエラーが発生しました: {response.text}")
                return self._create_fallback_analysis(prompt)
        except Exception as e:
            logger.error(f"LLMによる分析中にエラーが発生しました: {str(e)}")
            return self._create_fallback_analysis(prompt)

    def _create_fallback_analysis(self, prompt: str) -> Dict:
        """LLM分析が失敗した場合のフォールバック分析"""
        logger.info("フォールバック分析を使用します")
        
        # プロンプトから動画情報を抽出
        topics_set = set()
        locations_set = set()
        
        for line in prompt.split('\n'):
            if "トピック:" in line:
                topics = line.split("トピック:")[1].strip()
                for topic in topics.split(','):
                    if topic.strip():
                        topics_set.add(topic.strip())
            
            if "場所:" in line:
                location = line.split("場所:")[1].strip()
                if location != "不明":
                    locations_set.add(location)
        
        main_topics = list(topics_set)[:5]  # 上位5つのトピック
        
        return {
            "main_topics": main_topics,
            "content_analysis": f"このコンテンツは主に{', '.join(main_topics[:3])}に関する内容です。" if main_topics else "コンテンツ分析に失敗しました。",
            "suggested_concepts": main_topics,
            "target_audience": ["一般視聴者"],
            "content_suggestions": ["コンテンツをより詳細に分析するには、より多くのメタデータが必要です。"]
        }

    def analyze_contents(self, contents: List[VideoContent]) -> Dict:
        """動画コンテンツのリストから共通するコンセプトを抽出"""
        if not contents:
            logger.warning("分析するコンテンツがありません")
            return {
                "main_topics": [],
                "content_analysis": "分析するコンテンツがありません",
                "suggested_concepts": [],
                "target_audience": [],
                "content_suggestions": []
            }
            
        # コンテンツサマリーの集約
        content_summaries = []
        for content in contents:
            summary = {
                "title": content.title,
                "overview": content.overview,
                "topics": content.topics,
                "location": content.location,
                "purpose": content.purpose,
                "duration": content.total_duration
            }
            content_summaries.append(summary)
            
        try:
            # LLMによる分析
            prompt = self._create_analysis_prompt(content_summaries)
            logger.info("LLMを使用してコンテンツを分析します")
            return self._analyze_with_llm(prompt)
        except Exception as e:
            logger.error(f"分析中にエラーが発生しました: {str(e)}")
            # フォールバック：基本的な集計を返す
            return self._create_fallback_analysis(self._create_analysis_prompt(content_summaries))

    def _create_analysis_prompt(self, content_summaries: List[Dict]) -> str:
        """LLM用の分析プロンプトを作成"""
        prompt = "あなたは動画コンテンツアナリストです。以下の動画コンテンツ群を分析し、共通するテーマ、トピック、特徴を抽出してください。\n\n"
        prompt += "動画コンテンツ一覧：\n"
        
        # コンテンツの数を制限（最大20件まで）
        content_summaries = content_summaries[:20] if len(content_summaries) > 20 else content_summaries
        
        for i, summary in enumerate(content_summaries, 1):
            prompt += f"\n{i}. タイトル: {summary['title']}\n"
            prompt += f"   概要: {summary['overview']}\n"
            prompt += f"   トピック: {', '.join(summary['topics'])}\n"
            prompt += f"   場所: {summary['location']}\n"
            prompt += f"   目的: {summary['purpose']}\n"
            prompt += f"   長さ: {summary['duration']}秒\n"

        prompt += "\n以下の形式でJSON形式で回答してください：\n"
        prompt += "{\n"
        prompt += '  "main_topics": ["主要なトピック1", "トピック2", ...],\n'
        prompt += '  "content_analysis": "コンテンツ全体の分析結果と特徴",\n'
        prompt += '  "suggested_concepts": ["提案されるコンセプト1", "コンセプト2", ...],\n'
        prompt += '  "target_audience": ["想定される視聴者層1", "視聴者層2", ...],\n'
        prompt += '  "content_suggestions": ["コンテンツ改善の提案1", "提案2", ...]\n'
        prompt += "}"

        return prompt 