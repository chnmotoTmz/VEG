import os
import sys
import json

def main():
    """最小限のテストスクリプト"""
    print("最小限テスト開始")
    
    # テストデータの作成
    test_dir = "test_data"
    
    if not os.path.exists(test_dir):
        print(f"{test_dir}ディレクトリを作成します")
        os.makedirs(test_dir, exist_ok=True)
        
        # サンプルディレクトリとJSONファイルの作成
        sample_dir = os.path.join(test_dir, "sample_video")
        os.makedirs(sample_dir, exist_ok=True)
        
        # 最小限のJSONデータ
        sample_data = {
            "metadata": {
                "duration": 10.0
            },
            "scenes": [
                {
                    "transcripts": [
                        {"text": "テストトランスクリプト"}
                    ]
                }
            ]
        }
        
        # ファイル書き込み
        with open(os.path.join(sample_dir, "nodes.json"), "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
            
        print(f"サンプルデータを{sample_dir}に作成しました")
    else:
        print(f"{test_dir}ディレクトリが存在します")
    
    # ディレクトリ内のファイルを表示
    for root, dirs, files in os.walk(test_dir):
        print(f"ディレクトリ: {root}")
        for d in dirs:
            print(f"  サブディレクトリ: {d}")
        for f in files:
            print(f"  ファイル: {f}")
    
    # JSONファイルがあれば読み込む
    json_files = []
    for root, _, files in os.walk(test_dir):
        for file in files:
            if file == "nodes.json":
                json_files.append(os.path.join(root, file))
    
    print(f"見つかったnodes.jsonファイル: {len(json_files)}")
    
    success = True
    
    # 各JSONファイルを処理
    for json_path in json_files:
        print(f"\nファイル処理: {json_path}")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 基本情報を表示
            duration = data.get("metadata", {}).get("duration", 0)
            scenes = data.get("scenes", [])
            print(f"  シーン数: {len(scenes)}")
            print(f"  動画時間: {duration}秒")
            
            # トランスクリプトの抽出
            all_transcripts = []
            for scene in scenes:
                for transcript in scene.get("transcripts", []):
                    text = transcript.get("text", "")
                    if text:
                        all_transcripts.append(text)
            
            print(f"  抽出されたトランスクリプト数: {len(all_transcripts)}")
            for i, text in enumerate(all_transcripts[:3]):
                print(f"    トランスクリプト {i+1}: {text}")
                
        except Exception as e:
            print(f"  エラー: {str(e)}")
            success = False
    
    print("\n最小限テスト完了")
    print(f"結果: {'成功' if success else '失敗'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 