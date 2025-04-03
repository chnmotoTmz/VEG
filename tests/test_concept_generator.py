"""ConceptGeneratorのテスト"""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# テスト対象のモジュールパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.concept_generator import ConceptGenerator, TopicExtractor, LocationExtractor, ContentAnalyzer, ConceptBuilder

class TestTopicExtractor(unittest.TestCase):
    """TopicExtractorクラスのテスト"""
    
    def setUp(self):
        self.extractor = TopicExtractor()
        
    def test_extract_topics_from_content(self):
        """コンテンツからトピックを正しく抽出できるかテスト"""
        # テスト用のコンテンツデータ
        content = {
            "videos": {
                "video1.mp4": {
                    "scenes": [
                        {"tags": ["自然", "山", "風景"]},
                        {"tags": ["川", "自然"]}
                    ]
                },
                "video2.mp4": {
                    "scenes": [
                        {"tags": ["都市", "建物"]},
                        {"tags": ["人物", "文化"]}
                    ]
                }
            }
        }
        
        # トピック抽出
        topics = self.extractor.extract_topics(content)
        
        # 検証
        self.assertIsInstance(topics, list)
        self.assertIn("自然", topics)
        self.assertIn("山", topics)
        self.assertIn("風景", topics)
        self.assertIn("川", topics)
        self.assertIn("都市", topics)
        self.assertIn("建物", topics)
        self.assertIn("人物", topics)
        self.assertIn("文化", topics)
        
        # 重複がないことを確認
        self.assertEqual(len(topics), len(set(topics)))
        
    def test_default_topics_when_empty(self):
        """トピックが少ない場合にデフォルトトピックが追加されるかテスト"""
        # トピックが少ないコンテンツ
        content = {
            "videos": {
                "video1.mp4": {
                    "scenes": [
                        {"tags": ["自然"]}
                    ]
                }
            }
        }
        
        # トピック抽出
        topics = self.extractor.extract_topics(content)
        
        # 検証: デフォルトトピックが追加されていること
        self.assertGreaterEqual(len(topics), 3)
        self.assertIn("自然", topics)

class TestLocationExtractor(unittest.TestCase):
    """LocationExtractorクラスのテスト"""
    
    def setUp(self):
        self.extractor = LocationExtractor()
        
    def test_extract_locations(self):
        """コンテンツから場所情報を正しく抽出できるかテスト"""
        # テスト用のコンテンツデータ
        content = {
            "videos": {
                "video1.mp4": {
                    "metadata": {"location": "東京"}
                },
                "video2.mp4": {
                    "metadata": {"location": "京都"}
                },
                "video3.mp4": {
                    "metadata": {"location": "東京"}  # 重複
                }
            }
        }
        
        # 場所抽出
        locations = self.extractor.extract_locations(content)
        
        # 検証
        self.assertIsInstance(locations, list)
        self.assertEqual(len(locations), 2)  # 重複が除去されていること
        self.assertIn("東京", locations)
        self.assertIn("京都", locations)
        
    def test_default_location_when_empty(self):
        """場所情報がない場合にデフォルト値が使用されるかテスト"""
        # 場所情報がないコンテンツ
        content = {
            "videos": {
                "video1.mp4": {
                    "metadata": {}
                }
            }
        }
        
        # 場所抽出
        locations = self.extractor.extract_locations(content)
        
        # 検証
        self.assertEqual(locations, ["様々な場所"])

class TestContentAnalyzer(unittest.TestCase):
    """ContentAnalyzerクラスのテスト"""
    
    def setUp(self):
        self.analyzer = ContentAnalyzer()
        
    def test_calculate_total_duration(self):
        """コンテンツの合計時間を正しく計算できるかテスト"""
        # テスト用のコンテンツデータ
        content = {
            "videos": {
                "video1.mp4": {
                    "metadata": {"duration": 120.5}
                },
                "video2.mp4": {
                    "metadata": {"duration": 60.0}
                }
            }
        }
        
        # 時間計算
        duration = self.analyzer.calculate_total_duration(content)
        
        # 検証
        self.assertEqual(duration, 180.5)
        
    def test_determine_content_type_dynamic(self):
        """コンテンツタイプが動的なコンテンツを正しく判定できるかテスト"""
        # 短いシーンが多いコンテンツ
        content = {
            "videos": {
                "video1.mp4": {
                    "scenes": [
                        {"start_time": 0, "end_time": 2.5},
                        {"start_time": 2.5, "end_time": 5.0},
                        {"start_time": 5.0, "end_time": 7.0}
                    ]
                }
            }
        }
        
        # コンテンツタイプ判定
        content_type = self.analyzer.determine_content_type(content)
        
        # 検証
        self.assertEqual(content_type, "アクション/ダイナミック")
        
    def test_determine_target_audience(self):
        """ターゲットオーディエンスを正しく判定できるかテスト"""
        # 自然関連のトピック
        nature_topics = ["自然", "山", "海", "風景"]
        adventure_topics = ["アドベンチャー", "挑戦", "スポーツ"]
        culture_topics = ["文化", "歴史", "芸術"]
        
        # 判定
        nature_audience = self.analyzer.determine_target_audience(nature_topics)
        adventure_audience = self.analyzer.determine_target_audience(adventure_topics)
        culture_audience = self.analyzer.determine_target_audience(culture_topics)
        
        # 検証
        self.assertEqual(nature_audience, "自然愛好家と旅行者")
        self.assertEqual(adventure_audience, "アドベンチャー志向の視聴者")
        self.assertEqual(culture_audience, "文化や歴史に興味がある視聴者")

class TestConceptBuilder(unittest.TestCase):
    """ConceptBuilderクラスのテスト"""
    
    def setUp(self):
        self.builder = ConceptBuilder()
        
    def test_generate_title(self):
        """タイトルを正しく生成できるかテスト"""
        topics = ["自然", "山", "風景"]
        locations = ["富士山"]
        
        # タイトル生成
        title = self.builder.generate_title(topics, locations, "standard")
        
        # 検証
        self.assertIsInstance(title, str)
        self.assertTrue(
            any(kw in title for kw in topics) and 
            any(loc in title for loc in locations)
        )
        
    def test_generate_title_with_style(self):
        """スタイル指定ありでタイトルを正しく生成できるかテスト"""
        topics = ["文化", "歴史"]
        locations = ["京都"]
        
        # 各スタイルでタイトル生成
        dramatic_title = self.builder.generate_title(topics, locations, "dramatic")
        emotional_title = self.builder.generate_title(topics, locations, "emotional")
        informative_title = self.builder.generate_title(topics, locations, "informative")
        
        # 検証
        self.assertTrue(dramatic_title.startswith("衝撃の"))
        self.assertTrue(emotional_title.startswith("心に響く"))
        self.assertTrue(informative_title.startswith("徹底解説！"))
        
    def test_generate_concept_description(self):
        """コンセプト説明文を正しく生成できるかテスト"""
        topics = ["自然", "山"]
        locations = ["富士山"]
        duration = 180.0  # 3分
        
        # 説明文生成
        description = self.builder.generate_concept_description(topics, locations, duration)
        
        # 検証
        self.assertIn("富士山", description)
        self.assertIn("自然", description)
        self.assertIn("山", description)
        self.assertIn("3分", description)
        
    def test_generate_style_suggestions(self):
        """スタイル提案を正しく生成できるかテスト"""
        # 各種トピックでのテスト
        nature_suggestions = self.builder.generate_style_suggestions(["自然", "風景"], {})
        animal_suggestions = self.builder.generate_style_suggestions(["動物", "生き物"], {})
        culture_suggestions = self.builder.generate_style_suggestions(["文化", "歴史"], {})
        
        # 検証
        self.assertTrue(any("風景" in s for s in nature_suggestions))
        self.assertTrue(any("被写体の動き" in s for s in animal_suggestions))
        self.assertTrue(any("ゆっくり" in s for s in culture_suggestions))
        
        # カスタムスタイルのテスト
        cinematic_suggestions = self.builder.generate_style_suggestions(
            ["自然"], {"style": "cinematic"}
        )
        documentary_suggestions = self.builder.generate_style_suggestions(
            ["自然"], {"style": "documentary"}
        )
        
        # 検証
        self.assertTrue(any("シネマティック" in s for s in cinematic_suggestions))
        self.assertTrue(any("ナレーション" in s for s in documentary_suggestions))

class TestConceptGenerator(unittest.TestCase):
    """ConceptGeneratorクラスのテスト"""
    
    def setUp(self):
        self.generator = ConceptGenerator()
        
        # テスト用のコンテンツデータ
        self.test_content = {
            "videos": {
                "video1.mp4": {
                    "metadata": {"duration": 120.0, "location": "東京"},
                    "scenes": [
                        {"tags": ["都市", "建物"], "start_time": 0, "end_time": 30}
                    ]
                },
                "video2.mp4": {
                    "metadata": {"duration": 180.0, "location": "富士山"},
                    "scenes": [
                        {"tags": ["自然", "山"], "start_time": 0, "end_time": 60}
                    ]
                }
            }
        }
        
    def test_generate(self):
        """コンセプト生成が正しく機能するかテスト"""
        # コンセプト生成
        concept = self.generator.generate(self.test_content)
        
        # 検証: 必要なキーが含まれていること
        self.assertIsInstance(concept, dict)
        self.assertIn("title", concept)
        self.assertIn("description", concept)
        self.assertIn("keywords", concept)
        self.assertIn("locations", concept)
        self.assertIn("duration", concept)
        self.assertIn("content_type", concept)
        self.assertIn("target_audience", concept)
        self.assertIn("style_suggestions", concept)
        
        # データ型の検証
        self.assertIsInstance(concept["title"], str)
        self.assertIsInstance(concept["description"], str)
        self.assertIsInstance(concept["keywords"], list)
        self.assertIsInstance(concept["locations"], list)
        self.assertIsInstance(concept["duration"], float)
        self.assertIsInstance(concept["content_type"], str)
        self.assertIsInstance(concept["target_audience"], str)
        self.assertIsInstance(concept["style_suggestions"], list)
        
        # 値の検証
        self.assertEqual(concept["duration"], 300.0)
        self.assertIn("東京", concept["locations"])
        self.assertIn("富士山", concept["locations"])
        
    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("os.makedirs")
    def test_save_concept(self, mock_makedirs, mock_open):
        """コンセプトの保存が正しく機能するかテスト"""
        # テスト用のコンセプト
        concept = {
            "title": "テストタイトル",
            "description": "テスト説明文",
            "keywords": ["テスト", "キーワード"],
            "locations": ["テスト場所"],
            "duration": 300.0,
            "content_type": "テストタイプ",
            "target_audience": "テスト視聴者",
            "style_suggestions": ["テスト提案"]
        }
        
        # コンセプト保存
        self.generator.save_concept(concept, "/path/to/output.json")
        
        # 検証
        mock_makedirs.assert_called_once_with(os.path.dirname("/path/to/output.json"), exist_ok=True)
        mock_open.assert_called_once_with("/path/to/output.json", "w", encoding="utf-8-sig")
        mock_file = mock_open()
        # json.dumpが呼ばれたことを確認（引数の完全一致は複雑なので省略）
        self.assertGreaterEqual(mock_file.write.call_count, 1)

if __name__ == "__main__":
    unittest.main() 