import os
import sys
import json
import logging

# プロジェクトのルートディレクトリをPythonパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# ロギングの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("simple_test")

def main():
    print("シンプルテスト実行開始")
    
    # テストデータディレクトリの確認
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        print(f"エラー: {test_dir} ディレクトリが見つかりません")
        return
    
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
                    print(f"  シーン数: {len(data.get('scenes', []))}")
                    print(f"  総時間: {data.get('metadata', {}).get('duration', 0)}秒")
                    
                    # シーン情報を表示
                    scenes = data.get("scenes", [])
                    for i, scene in enumerate(scenes[:2]):  # 最初の2シーンのみ表示
                        print(f"  シーン {i}:")
                        print(f"    開始時間: {scene.get('start', 0)}秒")
                        print(f"    終了時間: {scene.get('end', 0)}秒")
                        print(f"    キーフレームパス: {scene.get('keyframe_path', '不明')}")
                        print(f"    プレビューパス: {scene.get('preview_path', '不明')}")
                        
                        # トランスクリプトの表示
                        transcripts = scene.get('transcripts', [])
                        if transcripts:
                            print(f"    トランスクリプト数: {len(transcripts)}")
                            print(f"    最初のトランスクリプト: {transcripts[0].get('text', '')}")
                        else:
                            print("    トランスクリプトなし")
                
                except Exception as e:
                    print(f"  エラー: JSONファイルの読み込みに失敗しました - {e}")
            else:
                print(f"\n{d} - nodes.jsonファイルが見つかりません")
    
    except Exception as e:
        print(f"エラー: {e}")
    
    print("\nシンプルテスト実行完了")

if __name__ == "__main__":
    main() 