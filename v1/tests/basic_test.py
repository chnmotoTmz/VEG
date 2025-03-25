import os
import sys
import json
import logging

# プロジェクトのルートディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('content_test.log'), logging.StreamHandler()]
)
logger = logging.getLogger("basic_test")

def main():
    """基本的なnodes.jsonの解析とトランスクリプト抽出テスト"""
    print("基本テスト開始")
    
    # テストデータディレクトリの確認
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        print(f"エラー: {test_dir} ディレクトリが見つかりません")
        return 1
    
    print(f"{test_dir} ディレクトリが見つかりました")
    
    # ディレクトリ内のフォルダを列挙
    try:
        dirs = [d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))]
        print(f"サブディレクトリ: {dirs}")
        
        # 各ディレクトリ内のnodes.jsonファイルを確認
        for d in dirs:
            json_path = os.path.join(test_dir, d, "nodes.json")
            if os.path.exists(json_path):
                print(f"\n{d} - nodes.jsonファイルが見つかりました")
                # ファイルの内容を読み込む
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 基本情報を表示
                    print(f"  タイトル: {data.get('summary', {}).get('title', 'タイトルなし')}")
                    scenes = data.get("scenes", [])
                    print(f"  シーン数: {len(scenes)}")
                    print(f"  総時間: {data.get('metadata', {}).get('duration', 0)}秒")
                    
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
                    
                    print(f"  抽出された台詞数: {len(all_transcripts)}")
                    for i, transcript in enumerate(all_transcripts[:3]):  # 最初の3つの台詞のみ表示
                        print(f"    台詞 {i+1}: {transcript['text']}")
                    
                    # トピックの抽出と表示
                    topics = data.get("topics", [])
                    if not topics:
                        for scene in scenes:
                            # 説明とコンテキスト分析からトピックを抽出
                            description = scene.get("description", "")
                            context = scene.get("context_analysis", {})
                            environment = context.get("environment", [])
                            activity = context.get("activity", [])
                            topics.extend(environment + activity)
                    
                    # 重複を削除
                    topics = list(set(topics))
                    print(f"  抽出されたトピック数: {len(topics)}")
                    if topics:
                        print(f"  トピック例: {', '.join(topics[:5])}")
                    
                    # 場所の抽出と表示
                    location = data.get("location", "")
                    if not location:
                        # バスが環境にあれば「バス内」と推測
                        for scene in scenes:
                            context = scene.get("context_analysis", {})
                            environment = context.get("environment", [])
                            for env in environment:
                                if "バス" in env:
                                    location = "バス内"
                                    break
                            if location:
                                break
                    
                    print(f"  推測された場所: {location or '不明'}")
                    
                    # 主題の推測
                    theme_keywords = []
                    for transcript in all_transcripts:
                        text = transcript["text"]
                        if "ありがとう" in text or "ご視聴" in text:
                            theme_keywords.append("感謝のメッセージ")
                        if "バス" in str(location) or "バス" in str(topics):
                            theme_keywords.append("バスの旅")
                    
                    theme = "と".join(list(set(theme_keywords))) or "不明"
                    print(f"  推測された主題: {theme}")
                
                except Exception as e:
                    print(f"  エラー: JSONファイルの読み込みに失敗しました - {e}")
            else:
                print(f"\n{d} - nodes.jsonファイルが見つかりません")
    
    except Exception as e:
        print(f"エラー: {e}")
        return 1
    
    print("\n基本テスト完了")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 