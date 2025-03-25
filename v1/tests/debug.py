import sys
import os
import traceback

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("sys.path:", sys.path)

try:
    print("Attempting to import module...")
    import srt_scene_tools
    print("srt_scene_tools imported successfully")
    
    print("Checking contents of srt_scene_tools...")
    print(dir(srt_scene_tools))
    
    print("Attempting to import scene_selection...")
    from srt_scene_tools import scene_selection
    print("scene_selection imported successfully")
    
    print("Checking contents of scene_selection...")
    print(dir(scene_selection))
    
except ImportError as e:
    print(f"Import error: {e}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()

print("Debug completed") 