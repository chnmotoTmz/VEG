import pytest
from pathlib import Path
import json
from srt_scene_tools.content_analyzer import ContentCrawler, ConceptGenerator, VideoContent

@pytest.fixture
def sample_nodes_data():
    return {
        "summary": {
            "title": "山道散策",
            "overview": "富士山麓での散策動画",
            "topics": ["ハイキング", "自然観察", "風景"],
            "filming_date": "2024-03-15",
            "location": "富士山麓",
            "purpose": "自然風景の撮影",
            "scene_count": 10,
            "total_duration": 600.0,
            "landscape_summary": {
                "main_environments": ["山道", "森林"],
                "notable_views": ["富士山", "山野草"]
            }
        }
    }

@pytest.fixture
def mock_video_folder(tmp_path, sample_nodes_data):
    # テスト用の一時フォルダ構造を作成
    video_nodes_dir = tmp_path / "video_nodes_test"
    video_nodes_dir.mkdir()
    
    nodes_file = video_nodes_dir / "nodes.json"
    nodes_file.write_text(json.dumps(sample_nodes_data))
    
    return tmp_path

def test_content_crawler_initialization(mock_video_folder):
    crawler = ContentCrawler(str(mock_video_folder))
    assert crawler.base_folder == str(mock_video_folder)
    assert len(crawler.video_contents) == 0

def test_content_crawler_crawl(mock_video_folder):
    crawler = ContentCrawler(str(mock_video_folder))
    contents = crawler.crawl()
    
    assert len(contents) == 1
    content = contents[0]
    assert content.title == "山道散策"
    assert content.location == "富士山麓"
    assert "ハイキング" in content.topics
    assert content.scene_count == 10
    assert content.total_duration == 600.0

def test_concept_generator():
    contents = [
        VideoContent(
            title="山道散策",
            overview="富士山麓での散策",
            topics=["ハイキング", "自然観察"],
            filming_date="2024-03-15",
            location="富士山麓",
            purpose="自然風景の撮影",
            scene_count=10,
            total_duration=600.0,
            environments=["山道", "森林"],
            notable_views=["富士山", "山野草"]
        ),
        VideoContent(
            title="高原さんぽ",
            overview="八ヶ岳での散策",
            topics=["ハイキング", "風景撮影"],
            filming_date="2024-03-16",
            location="八ヶ岳",
            purpose="風景撮影",
            scene_count=8,
            total_duration=480.0,
            environments=["高原", "森林"],
            notable_views=["八ヶ岳", "高原の花"]
        )
    ]

    generator = ConceptGenerator()
    concept = generator.analyze_contents(contents)

    assert "ハイキング" in concept["main_topics"]
    assert "森林" in concept["environments"]
    assert concept["total_scenes"] == 18
    assert concept["total_duration"] == 1080.0
    assert len(concept["locations"]) == 2
    assert len(concept["suggested_concepts"]) > 0 