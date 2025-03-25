# SRT Scene Tools

## 概要
SRT Scene Toolsは、動画ファイルからシーン情報を抽出・分析し、編集作業をサポートするツールです。このツールを使用すると、動画コンテンツを探索し、シーンごとに分析して、EDL（Edit Decision List）ファイルとSRT（字幕）ファイルを生成することができます。

## 主な機能
- 動画ファイルからのシーン抽出と分析
- シーン情報に基づいた作品コンセプト生成
- シナリオに基づいたシーン選別
- 編集用EDLファイルの生成
- 字幕用SRTファイルの生成

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/srt_scene_tools.git
cd srt_scene_tools

# 依存パッケージのインストール
pip install -r requirements.txt
```

## 使用方法

### 基本的な使い方
```bash
python -m srt_scene_tools.cli -c config.json
```

### 設定ファイル
`config_template.json`を参考に、以下の項目を設定してください：

```json
{
  "input_dir": "video_nodes/",
  "scenario_file": "scenario.json",
  "output_edl": "output/output.edl",
  "output_srt": "output/output.srt",
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
- `concept_generator.py`: 作品コンセプトの生成
- `scene_selector.py`: シナリオに基づいたシーン選別
- `edl_generator.py`: 編集リストの生成
- `srt_generator.py`: 字幕ファイルの生成
- `main.py`: メイン処理フロー
- `cli.py`: コマンドラインインターフェース

## 注意事項
- 相対パスはすべて動画ファイルのあるフォルダを基準とします
- 時間はすべて秒単位の浮動小数点数で記録されます
- 日時情報はISO 8601形式で記録されます
- ファイル名に含まれる連番は4桁の0埋めで統一されています

## ライセンス
[ライセンス情報を記載] "# VEG" 
