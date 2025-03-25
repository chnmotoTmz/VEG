import pytest
from srt_scene_tools.scenario_writer import ScenarioWriter, ScenarioInput

@pytest.fixture
def sample_concept_data():
    return {
        "main_topics": ["ハイキング", "自然観察"],
        "environments": ["山道", "森林"],
        "total_scenes": 18,
        "total_duration": 1080.0,
        "locations": ["富士山麓", "八ヶ岳"],
        "suggested_concepts": ["山道で楽しむハイキングの魅力"]
    }

@pytest.fixture
def sample_scenario_input():
    return ScenarioInput(
        title="初心者のための山歩き入門",
        target_audience="ハイキング初心者",
        video_style="教育・解説",
        main_message="誰でも楽しめる山歩きの魅力",
        video_length=600,
        key_points=[
            "基本的な準備と心構え",
            "実際の歩き方のコツ",
            "自然観察の楽しみ方"
        ]
    )

def test_scenario_writer_initialization(sample_concept_data):
    writer = ScenarioWriter(sample_concept_data)
    assert writer.concept_data == sample_concept_data
    assert writer.total_available_duration == 1080.0

def test_scenario_writer_invalid_initialization():
    with pytest.raises(ValueError, match="concept_data must be a dictionary"):
        ScenarioWriter(None)
    with pytest.raises(ValueError, match="concept_data must be a dictionary"):
        ScenarioWriter("invalid")

def test_create_scenario(sample_concept_data, sample_scenario_input):
    writer = ScenarioWriter(sample_concept_data)
    scenario = writer.create_scenario(sample_scenario_input)

    assert scenario["title"] == "初心者のための山歩き入門"
    assert "sections" in scenario
    assert "notes" in scenario
    assert "source_materials" in scenario

    sections = scenario["sections"]
    assert len(sections) == 5  # イントロ + 3つのキーポイント + アウトロ

    total_duration = sum(section["duration"] for section in sections)
    assert total_duration == sample_scenario_input.video_length

def test_section_duration_distribution(sample_concept_data, sample_scenario_input):
    writer = ScenarioWriter(sample_concept_data)
    scenario = writer.create_scenario(sample_scenario_input)
    
    intro_section = scenario["sections"][0]
    assert intro_section["duration"] == pytest.approx(60, rel=0.1)
    
    outro_section = scenario["sections"][-1]
    assert outro_section["duration"] == pytest.approx(60, rel=0.1)

    main_sections = scenario["sections"][1:-1]
    main_duration = sum(section["duration"] for section in main_sections)
    assert main_duration == pytest.approx(480, rel=0.1)

def test_error_handling(sample_concept_data):
    writer = ScenarioWriter(sample_concept_data)
    
    # None入力のテスト
    with pytest.raises(ValueError, match="input_data must be a ScenarioInput instance"):
        writer.create_scenario(None)
    
    # 無効な入力型のテスト
    with pytest.raises(ValueError, match="input_data must be a ScenarioInput instance"):
        writer.create_scenario("invalid")

def test_empty_key_points(sample_concept_data):
    writer = ScenarioWriter(sample_concept_data)
    
    # 空のキーポイントでのテスト
    empty_input = ScenarioInput(
        title="テスト",
        target_audience="テスト",
        video_style="テスト",
        main_message="テスト",
        video_length=600,
        key_points=[]
    )
    scenario = writer.create_scenario(empty_input)
    
    # イントロとアウトロのみ存在することを確認
    assert len(scenario["sections"]) == 2
    assert scenario["sections"][0]["title"] == "イントロダクション"
    assert scenario["sections"][1]["title"] == "まとめ"
    
    # 時間配分が適切か確認
    total_duration = sum(section["duration"] for section in scenario["sections"])
    assert total_duration == empty_input.video_length
    assert scenario["sections"][0]["duration"] == 300  # 50%
    assert scenario["sections"][1]["duration"] == 300  # 50% 