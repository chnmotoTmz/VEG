# SRT Scene Tools

SRT Scene Toolsは、動画編集のシナリオ作成とシーン選択を支援するPythonアプリケーションです。このツールを使用することで、GoPro等で撮影した映像から適切なシーンを選び、編集ソフトウェア（DaVinci Resolve等）で利用できるEDLファイルを生成できます。

## 主な機能

1. **コンテンツ分析**: 指定フォルダから動画ファイルとメタデータを読み込み、要約を生成
2. **シナリオ作成**: 動画の目的、対象視聴者、スタイルに基づいたシナリオを自動生成
3. **シーン選択**: 各シナリオセクションに合った最適なシーンを提案
4. **シーンプレビュー**: 選択されたシーンをプレビュー再生
5. **お試し再生**: 選択したシーンを連続再生して確認
6. **EDL生成**: DaVinci Resolveで読み込み可能なEDLファイルを生成

## 動作環境

- Python 3.8以上
- FFmpeg（クリップ生成に使用）
- 必要なPythonパッケージ（requirements.txtに記載）

## インストール方法

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/srt_scene_tools.git
cd srt_scene_tools

# 開発モードでインストール（推奨）
pip install -e .

# または通常のインストール
pip install .

# 必要なパッケージをインストール
pip install -r requirements.txt

# FFmpegのインストール（Windowsの場合）
# https://ffmpeg.org/download.html からダウンロードしてPATHに追加
```

## 使用方法

### GUIの起動

```bash
# パッケージとしてインストールした場合
python -m srt_scene_tools.main_gui

# または直接実行する場合
cd srt_scene_tools
python main_gui.py
```

### コマンドラインからの使用（SRTファイル解析）

```bash
python -m srt_scene_tools.scene_selection
```

### 基本的な操作手順

1. **コンテンツの読み込み**:
   - 「フォルダ選択」セクションでフォルダを選択し、「読み込み」ボタンをクリック
   - フォルダ内の`video_nodes_*`ディレクトリからJSONデータを検索

2. **シナリオの作成**:
   - タイトル、対象視聴者、スタイル、メインメッセージ、長さ、キーポイントを入力
   - 「シナリオ生成」ボタンをクリック

3. **シーンの選択**:
   - 右側の「シナリオセクション」リストからセクションを選択
   - 「候補シーン」リストから適切なシーンを選び、「プレビュー」で確認後、「追加」ボタンをクリック

4. **シーンの整理**:
   - 「上へ」「下へ」ボタンでシーンの順序を変更
   - 「お試し再生」ボタンですべてのシーンを連続再生して確認

5. **EDLファイルの生成**:
   - 「EDL生成」ボタンをクリックして保存先を選択

## ファイル構成

- `main_gui.py`: アプリケーションのエントリーポイント
- `utils.py`: ユーティリティクラス（Scene, LanguageHandler, ContentCrawler）
- `scenario_writer.py`: シナリオ生成機能
- `editing_agent.py`: シーン選択と類似度計算機能
- `scene_selection.py`: SRTファイル解析機能
- `gui/scene_selection_gui.py`: メインGUIインターフェース

## 既知の問題と解決方法

### モジュールインポートの問題

モジュールのインポートエラーが発生する場合（例: `ModuleNotFoundError: No module named 'utils'`）は、以下の解決策を試してください：

1. **開発モードでインストール**:
   ```bash
   pip install -e .
   ```

2. **直接実行する場合**:
   リポジトリのルートディレクトリから実行する代わりに、srt_scene_toolsディレクトリ内で実行：
   ```bash
   cd srt_scene_tools
   python main_gui.py
   ```

3. **PYTHONPATH環境変数の設定**:
   ```bash
   # Windowsの場合
   set PYTHONPATH=%PYTHONPATH%;C:\path\to\srt_scene_tools

   # Linuxの場合
   export PYTHONPATH=$PYTHONPATH:/path/to/srt_scene_tools
   ```

### その他の一般的な問題

- **tkinterのインポートエラー**: Pythonのインストール時にTkinterが含まれていない場合は、システムにTkinterをインストールしてください:
  - Windows: Python公式インストーラーで「tcl/tk and IDLE」オプションを選択
  - Linux: `sudo apt-get install python3-tk`（Debian/Ubuntu）
  - macOS: `brew install python-tk@3.9`（Homebrew使用時）

- **FFmpegの不足**: クリップ生成エラーが発生した場合、FFmpegがインストールされていることを確認してください

## 開発者向け情報

### パッケージ構成の設定

このプロジェクトはPythonパッケージとして構成されています。`setup.py`ファイルが正しく設定されていることを確認してください：

```python
from setuptools import setup, find_packages

setup(
    name="srt_scene_tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "srt",
        "moviepy",
        "pillow",
        "numpy",
        "ffmpeg-python",
    ],
)
```

### 相対インポートの使用

パッケージとして正しく動作させるには、相対インポートを使用してください：

```python
# 同じパッケージ内のモジュールをインポートする場合
from .utils import Scene
```

## 注意事項

- 適切な動作にはフォルダ内に正しい形式のJSONファイルが必要です
- GoProの時間情報が正確に記録されている場合、EDLのタイムコードも正確になります
- 大量のビデオファイルを処理する場合はメモリ使用量に注意してください

## ライセンス

MIT License

## 謝辞

このプロジェクトは以下のオープンソースライブラリを使用しています：
- moviepy
- tkinter
- srt 