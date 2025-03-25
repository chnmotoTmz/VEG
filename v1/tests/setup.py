from setuptools import setup, find_packages

setup(
    name="srt_scene_tools",
    version="0.1.0",
    description="動画編集のシナリオ作成とシーン選択を支援するツール",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "srt",
        "moviepy",
        "pillow",
        "numpy", 
        "ffmpeg-python",
        "openai",
        "google-generativeai",
        "python-dotenv",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'srt-scene-gui=srt_scene_tools.main_gui:main',
            'srt-scene-cli=srt_scene_tools.cli:main',
        ],
    },
) 