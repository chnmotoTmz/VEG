import traceback

try:
    from srt_scene_tools.scene_selection import _format_timecode
    print("インポートに成功しました")
except ImportError as e:
    print(f"インポートエラー: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"予期せぬエラー: {e}")
    traceback.print_exc()

print("完了") 