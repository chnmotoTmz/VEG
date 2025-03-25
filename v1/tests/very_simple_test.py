import os
import json

def main():
    print("基本テスト実行開始")
    
    # 現在のディレクトリを表示
    current_dir = os.getcwd()
    print(f"現在のディレクトリ: {current_dir}")
    
    # テストデータディレクトリの確認
    test_dir = "test_data"
    if os.path.exists(test_dir):
        print(f"{test_dir} ディレクトリが存在します")
        
        # サブディレクトリを列挙
        subdirs = [d for d in os.listdir(test_dir) if os.path.isdir(os.path.join(test_dir, d))]
        print(f"サブディレクトリ: {subdirs}")
        
        # シナリオファイルの確認
        scenario_file = "scenario.json"
        if os.path.exists(scenario_file):
            print(f"{scenario_file} ファイルが存在します")
            try:
                with open(scenario_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"シナリオタイトル: {data.get('title', '不明')}")
            except Exception as e:
                print(f"シナリオファイル読み込みエラー: {e}")
        else:
            print(f"{scenario_file} ファイルが見つかりません")
    else:
        print(f"{test_dir} ディレクトリが見つかりません")
    
    print("基本テスト実行完了")

if __name__ == "__main__":
    main() 