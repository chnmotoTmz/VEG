import re
import logging
import srt
import os
import json
import argparse
from pathlib import Path
try:
    # パッケージの一部として実行される場合
    from .utils import LanguageHandler, Scene, ContentCrawler
    from .editing_agent import EditingAgent, SceneMatch
except ImportError:
    # スクリプトとして直接実行される場合
    from utils import LanguageHandler, Scene, ContentCrawler
    from editing_agent import EditingAgent, SceneMatch


def _format_timecode(seconds):
    """秒数をタイムコード形式（HH:MM:SS.mmm）に変換する"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"


class SRTFileParser:
    def __init__(self, file_path: str):
        self.logger = logging.getLogger(__name__)
        self.file_path = file_path
        self.logger.info(f"Initialized SRTFileParser for file: {file_path}")

    def parse_srt(self) -> list[Scene]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            subtitle_generator = srt.parse(srt_content)
            scenes = []
            for subtitle in subtitle_generator:
                scenes.append(Scene(
                    start_time=str(subtitle.start),
                    end_time=str(subtitle.end),
                    text=subtitle.content
                ))
            return scenes
        except Exception as e:
            self.logger.error(f"Error parsing SRT file: {e}")
            return []


class SceneSelectionTool:
    def __init__(self, srt_file_path: str):
        self.logger = logging.getLogger(__name__)
        self.srt_file_parser = SRTFileParser(srt_file_path)
        self.selected_scenes = []
        self.language_handler = LanguageHandler()
        self.logger.info(f"Initialized SceneSelectionTool for file: {srt_file_path}")

    def select_scenes(self, scenario: str, language: str) -> list[Scene]:
        """
        Selects scenes based on a scenario and language.

        Args:
            scenario: The scenario for scene selection (e.g., "introduction").
            language: The language code (e.g., "en").

        Returns:
            A list of selected Scene objects. Returns an empty list if no scenes are found or if the scenario is invalid.
            Raises TypeError if input types are incorrect.
        """
        if not isinstance(scenario, str) or not isinstance(language, str):
            raise TypeError("Scenario and language must be strings.")

        scenes = self.srt_file_parser.parse_srt()
        if not scenes:
            return []

        # Placeholder for scenario-based selection logic.
        # Replace with your actual selection logic based on keywords or time ranges.
        selected_scenes = []
        for scene in scenes:
            if "introduction" in scenario.lower() and "introduction" in scene.text.lower():
                selected_scenes.append(scene)
        return selected_scenes


# 直接実行された場合のサンプルコード
if __name__ == "__main__":
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="シーン選択ツール")
    parser.add_argument("--scenario", required=True, help="シナリオJSONファイルのパス")
    parser.add_argument("--content_dir", required=True, help="コンテンツディレクトリのパス")
    parser.add_argument("--output_srt", required=True, help="出力SRTファイルのパス")
    parser.add_argument("--output_edl", required=True, help="出力EDLファイルのパス")
    parser.add_argument("--log_level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="ログレベル（デフォルト: INFO）")
    
    args = parser.parse_args()
    
    # ロギングの設定
    log_level = getattr(logging, args.log_level)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"シナリオファイル: {args.scenario}")
    logger.info(f"コンテンツディレクトリ: {args.content_dir}")
    
    try:
        # シナリオファイルの読み込み
        with open(args.scenario, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        logger.info(f"シナリオ '{scenario_data.get('title', 'Unknown')}' を読み込みました")
        
        # コンテンツの読み込み
        crawler = ContentCrawler(args.content_dir)
        content_data = crawler.crawl()
        
        if not content_data:
            logger.error("コンテンツデータが見つかりませんでした")
            exit(1)
        
        logger.info(f"{len(content_data)} 件のコンテンツが見つかりました")
        
        # 編集エージェントの初期化とシーン選択
        editing_agent = EditingAgent(content_data)
        
        # シナリオの要件に合致するシーンを選択
        selected_scenes = []
        target_language = scenario_data.get("target_language", "ja")
        
        for req in scenario_data.get("scene_requirements", []):
            query = req.get("description", "")
            keywords = req.get("keywords", [])
            emotions = req.get("emotions", [])
            min_count = req.get("min_count", 1)
            max_count = req.get("max_count", 3)
            
            logger.info(f"シーン要件: {query}, キーワード: {keywords}, 感情: {emotions}")
            
            # 文字列クエリを使用
            query_str = f"{query} {' '.join(keywords)}"
            matches = editing_agent.match_scenes(query_str, limit=max_count)
            
            if matches:
                # 必要な数のシーンを選択
                count = min(max_count, len(matches))
                count = max(min_count, count)
                
                # SceneMatchオブジェクトをSceneオブジェクトに変換
                for i in range(count):
                    match = matches[i]
                    scene = Scene(
                        start_time=_format_timecode(match.start_time), 
                        end_time=_format_timecode(match.end_time),
                        text=match.text,
                        video_id=match.scene_id
                    )
                    selected_scenes.append(scene)
                
                logger.info(f"{count} 件のシーンが選択されました")
            else:
                logger.warning(f"要件 '{query}' に一致するシーンが見つかりませんでした")
        
        if not selected_scenes:
            logger.error("シナリオに一致するシーンが見つかりませんでした")
            exit(1)
        
        # SRTファイルの生成
        os.makedirs(os.path.dirname(args.output_srt), exist_ok=True)
        with open(args.output_srt, 'w', encoding='utf-8') as f:
            for i, scene in enumerate(selected_scenes):
                f.write(f"{i+1}\n")
                f.write(f"{scene.start_time} --> {scene.end_time}\n")
                f.write(f"{scene.text}\n\n")
        
        logger.info(f"SRTファイルを作成しました: {args.output_srt}")
        
        # EDLファイルの生成
        os.makedirs(os.path.dirname(args.output_edl), exist_ok=True)
        with open(args.output_edl, 'w', encoding='utf-8') as f:
            f.write("TITLE: {}\n".format(scenario_data.get('title', 'Scene Selection')))
            f.write("FCM: NON-DROP FRAME\n\n")
            
            for i, scene in enumerate(selected_scenes):
                # タイムコードの変換（簡易実装）
                start_parts = scene.start_time.split(':')
                end_parts = scene.end_time.split(':')
                
                if len(start_parts) >= 3 and len(end_parts) >= 3:
                    f.write(f"{i+1:03d}  AX       AA/V  C        ")
                    f.write(f"{start_parts[0]}:{start_parts[1]}:{start_parts[2]} ")
                    f.write(f"{end_parts[0]}:{end_parts[1]}:{end_parts[2]} ")
                    f.write(f"{start_parts[0]}:{start_parts[1]}:{start_parts[2]} ")
                    f.write(f"{end_parts[0]}:{end_parts[1]}:{end_parts[2]}\n")
                    f.write(f"* FROM CLIP NAME: {scene.video_id or 'UNKNOWN'}\n\n")
        
        logger.info(f"EDLファイルを作成しました: {args.output_edl}")
        logger.info("処理が完了しました")
        
    except FileNotFoundError as e:
        logger.error(f"ファイルが見つかりません: {e}")
        exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"JSONの解析エラー: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}", exc_info=True)
        exit(1)
