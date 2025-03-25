# API Documentation

## 概要
このドキュメントは、SRT Scene Toolsで使用されているAPIの仕様を説明します。

## Gemini API

### 基本設定
- モデル: gemini-1.5-flash
- エンドポイント: Google AI Studio API
- 認証: APIキー（環境変数`GEMINI_API_KEY`で設定）

### 主要なメソッド

#### text_analysis
テキスト分析を実行し、JSON形式で結果を返します。

```python
def text_analysis(prompt: str) -> str:
    """
    入力: プロンプト文字列
    出力: JSON形式の分析結果
    """
```

#### analyze_image
画像分析を実行し、JSON形式で結果を返します。

```python
def analyze_image(image_path: str, prompt: str = None) -> str:
    """
    入力:
    - image_path: 画像ファイルのパス
    - prompt: オプションのプロンプト
    出力: JSON形式の分析結果
    """
```

### エラーハンドリング
- APIキー未設定: 警告ログを出力し、空のJSONを返す
- API制限: 自動的にリトライ（最大3回）
- ネットワークエラー: 適切なエラーメッセージを表示

### レスポンス形式
すべてのレスポンスは以下の形式のJSONで返されます：

```json
{
    "status": "success|error",
    "data": {
        // 分析結果
    },
    "message": "エラーメッセージ（エラー時のみ）"
}
```

## FFmpeg インターフェース

### 基本設定
- コマンドライン引数: 環境変数`FFMPEG_PATH`で設定
- 出力形式: MP4（H.264）
- フレームレート: 設定ファイルで指定（デフォルト30fps）

### 主要な機能
1. シーン抽出
2. キーフレーム生成
3. プレビュー動画作成

### 出力仕様
- キーフレーム: JPEG形式（品質90%）
- プレビュー: MP4（低ビットレート）
- タイムコード: NDF形式

## エラーコード一覧

| コード | 説明 | 対処方法 |
|--------|------|----------|
| E001 | APIキー未設定 | .envファイルを確認 |
| E002 | API制限到達 | しばらく待機 |
| E003 | ファイル未検出 | パスを確認 |
| E004 | 解析エラー | ログを確認 |

## 更新履歴

### v1.0.0
- Gemini APIへの移行完了
- エラーハンドリングの改善
- 日本語対応の強化 