# SRT Scene Tools

映像編集支援ツール - コンテンツ解析、シーン選択、EDL/SRT生成をサポート

## 機能概要

このツールは、映像コンテンツの編集作業を3つのフェーズに分けて支援します：

1. **コンテンツ解析フェーズ**
   - 映像コンテンツの自動解析
   - タイトルとコンセプトの生成
   - シナリオテンプレートの作成

2. **シーン選択フェーズ**
   - シナリオに基づくシーン選択
   - セクションごとのシーン割り当て
   - 選択理由の記録

3. **出力生成フェーズ**
   - EDLファイルの生成
   - SRTファイルの生成
   - エフェクト情報の付与

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. コンテンツ解析フェーズ

```bash
python -m src.cli analyze -c config.json
```

このフェーズでは以下のファイルが生成されます：
- `concept.json`: 生成されたタイトルとコンセプト
- `scenario_template.json`: シナリオ作成用テンプレート
- `logs/concept_prompt.txt`: コンセプト生成に使用したプロンプト

### 2. シーン選択フェーズ

```bash
python -m src.cli select -c config.json
```

このフェーズでは以下のファイルが生成されます：
- `selected.json`: 選択されたシーン情報
- `logs/selection_prompt.txt`: シーン選択に使用したプロンプト

### 3. 出力生成フェーズ

```bash
python -m src.cli generate -c config.json
```

このフェーズでは以下のファイルが生成されます：
- `output.edl`: 編集決定リスト
- `output.srt`: 字幕ファイル

## 設定ファイル形式

```json
{
  "input_dir": "動画ファイルのディレクトリパス",
  "output_dir": "出力先ディレクトリパス",
  "video_format": "mp4",
  "concept_params": {
    "title_style": "魅力的",
    "focus_keywords": ["自然", "旅行"]
  },
  "selection_params": {
    "max_scenes": 10,
    "min_scene_duration": 3,
    "prefer_action": true
  },
  "output_params": {
    "edl_format": "standard",
    "srt_style": "minimal"
  }
}
```

## GUI モード

グラフィカルインターフェースを使用する場合：

```bash
python -m src.gui
```

## 開発者向け情報

### 開発モードの有効化

開発モードではAI支援機能が有効になります：

```bash
export DEVELOPMENT_MODE=1
```

または、.envファイルに記述：

```
DEVELOPMENT_MODE=1
```

### モジュール構成

- `content_crawler.py`: 映像ファイルの解析
- `scenario_writer.py`: コンセプトとシナリオテンプレート生成
- `scene_selector.py`: シーン選択ロジック
- `edl_generator.py`: EDLファイル生成
- `srt_generator.py`: 字幕ファイル生成
- `api_client.py`: AI APIクライアント
- `evolve_chip.py`: AI開発支援機能

## ライセンス

MIT License 