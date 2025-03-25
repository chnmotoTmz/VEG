import os
import sys
import json
import logging
from pathlib import Path

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('content_test.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("improved_test")

def create_sample_test_data(test_dir: str) -> None:
    """テストデータが存在しない場合にサンプルデータを生成"""
    logger.info(f"テストディレクトリ {test_dir} を作成します")
    os.makedirs(test_dir, exist_ok=True)
    
    # サンプルデータ（提供されたnodes.jsonを基に簡略化）
    sample_nodes_json = {
        "file_path": "G:\\100GOPRO\\GH012575.MP4",
        "metadata": {
            "filename": "GH012575.MP4",
            "duration": 14.485333,
        },
        "summary": {
            "title": "動画のタイトル不明",
            "overview": "動画の概要情報がトランスクリプトに含まれていません。",
            "topics": [],
            "scene_count": 1,
            "total_duration": 14.485333,
        },
        "scenes": [
            {
                "id": 0,
                "start": 0.0,
                "end": 29.98,
                "duration": 29.98,
                "transcripts": [
                    {
                        "start": 0.0,
                        "end": 29.98,
                        "text": "ご視聴ありがとうございました"
                    }
                ],
                "description": "バス車内からの景色を捉えた短い映像の最終シーン。",
                "context_analysis": {
                    "location_type": "indoor",
                    "environment": [
                        "バスの車内",
                        "座席",
                        "窓",
                        "バスの天井",
                        "乗客（後頭部のみ見える）",
                        "建物（窓の外）",
                        "山々（窓の外）",
                        "バスの表示画面（ぼやけていて内容は不明）"
                    ],
                    "activity": [
                        "バスの走行（推測）",
                        "映像の撮影（推測）"
                    ],
                },
            }
        ],
        "processed_at": "2025-03-25T00:21:50.909046"
    }
    
    # シーンがないサンプルデータ
    sample_nodes_json_no_scenes = {
        "file_path": "G:\\100GOPRO\\GH012576.MP4",
        "metadata": {
            "filename": "GH012576.MP4",
            "duration": 0
        },
        "summary": {
            "title": "動画2",
            "overview": "概要なし",
            "topics": [],
            "scene_count": 0,
            "total_duration": 0
        },
        "scenes": [],
        "processed_at": "2025-03-25T00:22:00.000000"
    }
    
    # テストディレクトリ内にサンプルデータを保存
    video_nodes_dir_1 = os.path.join(test_dir, "video_nodes_GH012575")
    video_nodes_dir_2 = os.path.join(test_dir, "video_nodes_GH012576")
    os.makedirs(video_nodes_dir_1, exist_ok=True)
    os.makedirs(video_nodes_dir_2, exist_ok=True)
    
    with open(os.path.join(video_nodes_dir_1, "nodes.json"), 'w', encoding='utf-8') as f:
        json.dump(sample_nodes_json, f, ensure_ascii=False, indent=2)
    with open(os.path.join(video_nodes_dir_2, "nodes.json"), 'w', encoding='utf-8') as f:
        json.dump(sample_nodes_json_no_scenes, f, ensure_ascii=False, indent=2)
    
    logger.info(f"サンプルテストデータを {test_dir} に作成しました")

def main():
    """基本的なnodes.jsonの解析とトランスクリプト抽出テスト"""
    logger.info("基本テスト開始")
    
    # テストデータディレクトリの確認
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        logger.warning(f"{test_dir} ディレクトリが見つかりません。サンプルデータを作成します")
        create_sample_test_data(test_dir)
    else:
        logger.info(f"{test_dir} ディレクトリが見つかりました")
    
    success = True
    
    # ディレクトリ内のフォルダを列挙
    try:
        dirs = [d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))]
        logger.info(f"サブディレクトリ: {dirs}")
        
        if not dirs:
            logger.error("サブディレクトリが見つかりません。テストを中止します")
            return 1
        
        # 各ディレクトリ内のnodes.jsonファイルを確認
        for d in dirs:
            json_path = os.path.join(test_dir, d, "nodes.json")
            if os.path.exists(json_path):
                logger.info(f"\n{d} - nodes.jsonファイルが見つかりました")
                # ファイルの内容を読み込む
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 基本情報を表示
                    logger.info(f"  タイトル: {data.get('summary', {}).get('title', 'タイトルなし')}")
                    scenes = data.get("scenes", [])
                    logger.info(f"  シーン数: {len(scenes)}")
                    duration = data.get("metadata", {}).get("duration", 0)
                    logger.info(f"  総時間: {duration}秒")
                    
                    # すべての台詞を抽出
                    all_transcripts = []
                    for scene in scenes:
                        transcripts = scene.get("transcripts", [])
                        for transcript in transcripts:
                            text = transcript.get("text", "")
                            if text:
                                all_transcripts.append({
                                    "start": transcript.get("start", 0.0),
                                    "end": transcript.get("end", 0.0),
                                    "text": text
                                })
                    
                    logger.info(f"  抽出された台詞数: {len(all_transcripts)}")
                    for i, transcript in enumerate(all_transcripts[:3]):  # 最初の3つの台詞のみ表示
                        logger.info(f"    台詞 {i+1}: {transcript['text']}")
                    
                    # トピックの抽出と表示
                    topics = data.get("topics", [])
                    if not topics:
                        for scene in scenes:
                            description = scene.get("description", "")
                            context = scene.get("context_analysis", {})
                            environment = context.get("environment", [])
                            activity = context.get("activity", [])
                            topics.extend(environment + activity)
                    
                    topics = list(set(topics))
                    logger.info(f"  抽出されたトピック数: {len(topics)}")
                    if topics:
                        logger.info(f"  トピック例: {', '.join(topics[:5])}")
                    
                    # 場所の抽出と表示
                    location = data.get("location", "")
                    if not location:
                        for scene in scenes:
                            context = scene.get("context_analysis", {})
                            environment = context.get("environment", [])
                            for env in environment:
                                if "バス" in env:
                                    location = "バス内"
                                    break
                            if location:
                                break
                    
                    logger.info(f"  推測された場所: {location or '不明'}")
                    
                    # 主題の推測
                    theme_keywords = []
                    for transcript in all_transcripts:
                        text = transcript["text"]
                        if "ありがとう" in text or "ご視聴" in text:
                            theme_keywords.append("感謝のメッセージ")
                        if "バス" in str(location) or "バス" in str(topics):
                            theme_keywords.append("バスの旅")
                    
                    theme = "と".join(list(set(theme_keywords))) or "不明"
                    logger.info(f"  推測された主題: {theme}")
                    
                    # 検証
                    if len(scenes) == 0 and duration > 0:
                        logger.warning(f"  検証失敗: シーン数が0ですが、動画の長さが{duration}秒あります")
                        success = False
                    if duration == 0 and len(scenes) > 0:
                        logger.warning(f"  検証失敗: 動画の長さが0秒ですが、シーン数が{len(scenes)}あります")
                        success = False
                    if not all_transcripts and len(scenes) > 0:
                        logger.warning("  検証失敗: シーンがありますが、台詞が抽出されていません")
                        success = False
                
                except Exception as e:
                    logger.error(f"  エラー: JSONファイルの読み込みに失敗しました - {e}")
                    success = False
            else:
                logger.warning(f"\n{d} - nodes.jsonファイルが見つかりません")
    
    except Exception as e:
        logger.error(f"エラー: {e}")
        return 1
    
    logger.info("\n基本テスト完了")
    logger.info(f"テスト結果: {'成功' if success else '失敗'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 