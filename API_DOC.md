# シーン記述生成ツール APIドキュメント

## データフォルダ構造

動画ファイルの処理結果は、以下の構造で保存されます：

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

### nodes.jsonの構造

```json
{
    "video_path": "元の動画ファイルへの絶対パス",
    "summary": {
        "title": "動画のタイトル",
        "overview": "動画の概要",
        "topics": ["トピック1", "トピック2", ...],
        "filming_date": "撮影日（YYYY-MM-DD）",
        "location": "撮影場所",
        "weather": ["天候1", "天候2", ...],
        "purpose": "撮影目的",
        "transportation": ["移動手段1", "移動手段2", ...],
        "starting_point": "出発地点",
        "destination": "目的地",
        "scene_count": シーン数,
        "total_duration": 総時間（秒）,
        "landscape_summary": {
            "main_environments": ["環境1", "環境2", ...],
            "terrain_features": ["地形1", "地形2", ...],
            "notable_views": ["景観1", "景観2", ...]
        },
        "gopro_start_time": "GoProの内部時刻（ISO 8601形式）"
    },
    "scenes": [
        {
            "scene_id": シーンID,
            "time_in": 開始時間（秒）,
            "time_out": 終了時間（秒）,
            "transcript": "音声文字起こし",
            "description": "シーンの説明",
            "keyframe_path": "キーフレーム画像の相対パス",
            "preview_path": "プレビュー動画の相対パス",
            "duration": シーンの長さ（秒）,
            "context_analysis": {
                "location_type": "場所の種類",
                "environment": ["環境要素1", "環境要素2", ...],
                "time_of_day": "時間帯",
                "weather": ["天候1", "天候2", ...],
                "activity": ["活動1", "活動2", ...],
                "emotional_tone": "感情トーン"
            },
            "editing_suggestions": {
                "highlight_worthy": ハイライト候補か（true/false）,
                "potential_cutpoint": カットポイントとして適切か（true/false）,
                "b_roll_opportunity": "B-roll撮影の提案",
                "audio_considerations": "音声に関する注意点"
            }
        },
        // ... 他のシーン
    ],
    "completed": 処理完了フラグ（true/false）,
    "last_update": "最終更新日時（ISO 8601形式）"
}
```

## キーフレーム画像

- 形式: JPEG
- サイズ: 320x180ピクセル
- 命名規則: `keyframe_XXXX.jpg`（XXXXは0000から始まる連番）
- 保存場所: `video_nodes_[動画ファイル名]/keyframes/`

## プレビュー動画

- 形式: MP4
- 解像度: 320x180ピクセル
- エンコード設定:
  - ビデオ: H.264, CRF 35, ultrafast preset
  - 音声: AAC, 32kbps, モノラル, 22050Hz
- 命名規則: `preview_XXXX.mp4`（XXXXは0000から始まる連番）
- 保存場所: `video_nodes_[動画ファイル名]/previews/`

## 注意事項

1. 相対パスはすべて動画ファイルのあるフォルダを基準とします
2. 時間はすべて秒単位の浮動小数点数で記録されます
3. 日時情報はISO 8601形式で記録されます
4. ファイル名に含まれる連番は4桁の0埋めで統一されています
5. 子フォルダは処理対象外です（同一フォルダ内の動画ファイルのみ処理） 