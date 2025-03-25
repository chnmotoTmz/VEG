# SRT Scene Tools

## 概要
SRT Scene Toolsは、動画ファイルからシーン情報を抽出・分析し、編集作業をサポートするAIツールです。Gemini APIを活用して、動画コンテンツを探索し、シーンごとに分析して、EDL（Edit Decision List）ファイルとSRT（字幕）ファイルを生成することができます。

## 主な機能
- 動画ファイルからのシーン抽出と分析
- AIを活用した作品コンセプト生成
- シナリオに基づいたシーン選別
- 編集用EDLファイルの生成
- 字幕用SRTファイルの生成

## 必要要件
- Python 3.8以上
- Google Gemini API キー
- FFmpeg（動画処理用）

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/srt_scene_tools.git
cd srt_scene_tools

# 依存パッケージのインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPIキーを設定
```

## 環境変数の設定
`.env`ファイルに以下の環境変数を設定してください：

```ini
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## 使用方法

### 基本的な使い方
```bash
python -m src.cli run -c config.json
```

### 設定ファイル
`config_template.json`を参考に、以下の項目を設定してください：

```json
{
  "input_dir": "video_nodes/",
  "scenario_file": "scenario.json",
  "output_dir": "output/",
  "options": {
    "language": "ja",
    "timecode_format": "NDF",
    "frame_rate": 30,
    "max_scenes": 50,
    "min_scene_duration": 3.0,
    "max_scene_duration": 60.0
  }
}
```

## データ構造
処理された動画ファイルのデータは、以下の構造で保存されます：

```
[動画ファイルのあるフォルダ]/
├── 元の動画ファイル.MP4
└── video_nodes_[動画ファイル名]/
    ├── nodes.json          # シーン情報とメタデータ
    ├── keyframes/          # シーンのキーフレーム画像
    │   ├── keyframe_0000.jpg
    │   ├── keyframe_0001.jpg
    │   └── ...
    └── previews/          # シーンのプレビュー動画
        ├── preview_0000.mp4
        ├── preview_0001.mp4
        └── ...
```

## モジュール構成
- `content_crawler.py`: 動画コンテンツの探索
- `concept_generator.py`: AIを活用した作品コンセプトの生成
- `scene_selector.py`: シナリオに基づいたシーン選別
- `edl_generator.py`: 編集リストの生成
- `srt_generator.py`: 字幕ファイルの生成
- `api_client.py`: Gemini API クライアント
- `main.py`: メイン処理フロー
- `cli.py`: コマンドラインインターフェース

## エラー処理
- APIキーが設定されていない場合は適切なエラーメッセージが表示されます
- ネットワークエラーやAPI制限の場合は自動的にリトライを行います
- 処理中のエラーは`debug.log`に記録されます

## 注意事項
- 相対パスはすべて動画ファイルのあるフォルダを基準とします
- 時間はすべて秒単位の浮動小数点数で記録されます
- 日時情報はISO 8601形式で記録されます
- ファイル名に含まれる連番は4桁の0埋めで統一されています
- APIキーは必ず`.env`ファイルで管理し、直接コードに記述しないでください

## 開発ガイドライン
詳細な開発ガイドラインは`CONTRIBUTING.md`を参照してください。

## ライセンス
MIT License

Copyright (c) 2024 Your Name
