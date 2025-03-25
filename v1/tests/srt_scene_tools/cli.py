#!/usr/bin/env python
"""
SRT Scene Tools CLI
シンプルなコマンドラインインターフェース
"""

import os
import sys
import json
import logging
import argparse
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Scene:
    """シンプルなシーンクラス"""
    start_time: str
    end_time: str
    text: str
    video_id: str = ""

def setup_logging(log_level_name="INFO"):
    """ロギングのセットアップ"""
    log_level = getattr(logging, log_level_name)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    return logging.getLogger("srt_cli")

def format_timecode(seconds: float) -> str:
    """秒数をタイムコード形式（HH:MM:SS.mmm）に変換する"""
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def read_test_data(content_dir: str) -> List[Dict[str, Any]]:
    """テストデータディレクトリからJSONファイルを読み込む"""
    logger = logging.getLogger("srt_cli")
    content_data = []
    
    try:
        logger.info(f"Reading test data from: {content_dir}")
        
        # video_nodes_* ディレクトリをスキャン
        nodes_dirs = []
        for item in os.listdir(content_dir):
            if item.startswith("video_nodes_") and os.path.isdir(os.path.join(content_dir, item)):
                nodes_dirs.append(os.path.join(content_dir, item))
        
        if not nodes_dirs:
            logger.warning("No video_nodes_* directories found")
            # 直接JSONファイルを検索
            for root, _, files in os.walk(content_dir):
                for file in files:
                    if file.endswith(".json"):
                        json_path = os.path.join(root, file)
                        process_json_file(json_path, content_data)
        else:
            for node_dir in nodes_dirs:
                logger.info(f"Processing directory: {node_dir}")
                for file in os.listdir(node_dir):
                    if file.endswith(".json"):
                        json_path = os.path.join(node_dir, file)
                        process_json_file(json_path, content_data)
                
        logger.info(f"Found {len(content_data)} content items")
        return content_data
    
    except Exception as e:
        logger.error(f"Error reading test data: {e}", exc_info=True)
        return []

def process_json_file(json_path: str, content_data: List[Dict[str, Any]]) -> None:
    """JSONファイルを処理してコンテンツデータに追加"""
    logger = logging.getLogger("srt_cli")
    
    try:
        logger.info(f"Reading JSON file: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # データを正規化してコンテンツリストに追加
        content = {
            "title": data.get("title", os.path.basename(json_path)),
            "summary": data.get("summary", {}),
            "scenes": data.get("scenes", []),
            "filepath": json_path,
            "video_path": data.get("metadata", {}).get("filepath", "")
        }
        
        content_data.append(content)
        logger.info(f"Processed: {content['title']} - {len(content['scenes'])} scenes")
    
    except Exception as e:
        logger.error(f"Error processing {json_path}: {e}")

def select_scenes(content_data: List[Dict[str, Any]], scenario_data: Dict[str, Any]) -> List[Scene]:
    """シナリオデータに基づいてシーンを選択"""
    logger = logging.getLogger("srt_cli")
    selected_scenes = []
    
    try:
        # シナリオの要件をループ
        for req in scenario_data.get("scene_requirements", []):
            description = req.get("description", "")
            keywords = req.get("keywords", [])
            emotions = req.get("emotions", [])
            min_count = req.get("min_count", 1)
            max_count = req.get("max_count", 3)
            
            logger.info(f"Scene requirement: {description}, keywords: {keywords}")
            
            # キーワードマッチングでシーンを選択
            matches = []
            for content in content_data:
                for scene in content.get("scenes", []):
                    # キーワードマッチング（簡易実装）
                    scene_text = scene.get("text", "") + " " + scene.get("transcript", "")
                    keyword_matches = sum(keyword.lower() in scene_text.lower() for keyword in keywords)
                    
                    if keyword_matches > 0 or description.lower() in scene_text.lower():
                        similarity = keyword_matches / len(keywords) if keywords else 0.5
                        
                        # 感情マッチング
                        if emotions and scene.get("emotions"):
                            scene_emotions = scene.get("emotions", {})
                            emotion_matches = sum(scene_emotions.get(emotion, 0) for emotion in emotions)
                            similarity += emotion_matches / len(emotions) if emotions else 0
                        
                        # マッチ結果を記録
                        matches.append({
                            "id": scene.get("id", "unknown"),
                            "content_title": content.get("title", ""),
                            "start": scene.get("start", 0.0),
                            "end": scene.get("end", 0.0),
                            "text": scene_text,
                            "similarity": similarity
                        })
            
            # 類似度でソート
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            
            # 必要な数のシーンを選択
            count = min(max_count, len(matches))
            if count < min_count:
                logger.warning(f"Found only {count} scenes matching requirement: {description}")
            
            # シーンオブジェクトに変換して追加
            for i in range(min(count, len(matches))):
                match = matches[i]
                scene = Scene(
                    start_time=format_timecode(match["start"]),
                    end_time=format_timecode(match["end"]),
                    text=match["text"],
                    video_id=match["id"]
                )
                selected_scenes.append(scene)
                logger.info(f"Selected scene: {match['id']} - {match['text'][:50]}...")
        
        return selected_scenes
    
    except Exception as e:
        logger.error(f"Error selecting scenes: {e}", exc_info=True)
        return []

def generate_srt(scenes: List[Scene], output_path: str) -> None:
    """SRTファイルを生成"""
    logger = logging.getLogger("srt_cli")
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, scene in enumerate(scenes):
                f.write(f"{i+1}\n")
                f.write(f"{scene.start_time} --> {scene.end_time}\n")
                f.write(f"{scene.text}\n\n")
        
        logger.info(f"Generated SRT file: {output_path}")
    
    except Exception as e:
        logger.error(f"Error generating SRT file: {e}", exc_info=True)

def generate_edl(scenes: List[Scene], scenario_data: Dict[str, Any], output_path: str) -> None:
    """EDLファイルを生成"""
    logger = logging.getLogger("srt_cli")
    
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"TITLE: {scenario_data.get('title', 'Scene Selection')}\n")
            f.write("FCM: NON-DROP FRAME\n\n")
            
            for i, scene in enumerate(scenes):
                start_parts = scene.start_time.split(':')
                end_parts = scene.end_time.split(':')
                
                if len(start_parts) >= 3 and len(end_parts) >= 3:
                    f.write(f"{i+1:03d}  AX       AA/V  C        ")
                    f.write(f"{start_parts[0]}:{start_parts[1]}:{start_parts[2]} ")
                    f.write(f"{end_parts[0]}:{end_parts[1]}:{end_parts[2]} ")
                    f.write(f"{start_parts[0]}:{start_parts[1]}:{start_parts[2]} ")
                    f.write(f"{end_parts[0]}:{end_parts[1]}:{end_parts[2]}\n")
                    f.write(f"* FROM CLIP NAME: {scene.video_id or 'UNKNOWN'}\n\n")
        
        logger.info(f"Generated EDL file: {output_path}")
    
    except Exception as e:
        logger.error(f"Error generating EDL file: {e}", exc_info=True)

def main():
    """メイン関数"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description="SRT Scene Tools CLI")
    parser.add_argument("--scenario", required=True, help="シナリオJSONファイルのパス")
    parser.add_argument("--content_dir", required=True, help="コンテンツディレクトリのパス")
    parser.add_argument("--output_srt", required=True, help="出力SRTファイルのパス")
    parser.add_argument("--output_edl", required=True, help="出力EDLファイルのパス")
    parser.add_argument("--log_level", default="INFO", 
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="ログレベル")
    
    args = parser.parse_args()
    logger = setup_logging(args.log_level)
    
    try:
        # シナリオファイルの読み込み
        logger.info(f"Reading scenario file: {args.scenario}")
        with open(args.scenario, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        # テストデータの読み込み
        content_data = read_test_data(args.content_dir)
        
        if not content_data:
            logger.error("No content data found")
            sys.exit(1)
        
        # シーンの選択
        selected_scenes = select_scenes(content_data, scenario_data)
        
        if not selected_scenes:
            logger.error("No scenes matched the scenario requirements")
            sys.exit(1)
        
        logger.info(f"Selected {len(selected_scenes)} scenes")
        
        # SRTファイルの生成
        generate_srt(selected_scenes, args.output_srt)
        
        # EDLファイルの生成
        generate_edl(selected_scenes, scenario_data, args.output_edl)
        
        logger.info("Process completed successfully")
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 