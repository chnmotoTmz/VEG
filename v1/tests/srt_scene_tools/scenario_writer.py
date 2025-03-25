from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ScenarioInput:
    title: str
    target_audience: str
    style: str  # video_styleから名前変更
    main_message: str
    length: int  # video_lengthから名前変更
    key_points: List[str]

@dataclass
class ScenarioSection:
    title: str
    duration: int
    description: str
    key_scenes: List[str]
    narration_notes: str

class ScenarioWriter:
    def __init__(self, concept_data: Dict = None):
        self.concept_data = concept_data or {}
        self.total_available_duration = self.concept_data.get('total_duration', 0) if concept_data else 0
        logger.info("ScenarioWriter initialized")

    def generate(self, contents: List[Any], scenario_input: ScenarioInput) -> str:
        """コンテンツリストからシナリオを生成"""
        logger.info(f"シナリオ生成開始: タイトル={scenario_input.title}, 対象視聴者={scenario_input.target_audience}")
        
        # コンテンツ情報の記録
        total_contents = len(contents) if contents else 0
        logger.info(f"処理対象のコンテンツ数: {total_contents}")
        
        if not contents:
            logger.warning("コンテンツリストが空です")
            return "コンテンツデータがありません。先にコンテンツ分析を実行してください。"
        
        try:
            # コンテンツ分析からコンセプトデータを抽出
            concept_data = {
                'total_duration': 0,
                'total_scenes': 0,
                'locations': [],
                'main_topics': []
            }
            
            # 各ビデオについて詳細情報をログに記録
            for i, content in enumerate(contents):
                try:
                    # 辞書形式またはオブジェクト形式に対応
                    scenes = []
                    duration = 0
                    title = f"ビデオ {i+1}"
                    
                    # 辞書形式の場合
                    if isinstance(content, dict):
                        scenes = content.get('scenes', [])
                        duration = content.get('total_duration', 0)
                        title = content.get('title', title)
                        location = content.get('location', '')
                        topics = content.get('topics', [])
                        
                        # トピック情報が足りない場合はシーンから直接抽出
                        if not topics and scenes:
                            # シーンのcontext_analysisから抽出
                            for scene in scenes:
                                if isinstance(scene, dict):
                                    context = scene.get("context_analysis", {})
                                    if context:
                                        # 環境情報を追加
                                        env = context.get("environment", [])
                                        if env:
                                            topics.extend(env)
                                        # 活動情報を追加
                                        act = context.get("activity", [])
                                        if act:
                                            topics.extend(act)
                        
                        # 場所情報が足りない場合は最初のシーンから抽出
                        if not location and scenes:
                            for scene in scenes:
                                if isinstance(scene, dict):
                                    context = scene.get("context_analysis", {})
                                    if context:
                                        loc_type = context.get("location_type", "")
                                        if loc_type:
                                            location = loc_type
                                            break
                    # オブジェクト形式の場合
                    else:
                        scenes = getattr(content, 'scenes', [])
                        duration = getattr(content, 'total_duration', 0)
                        title = getattr(content, 'title', title)
                        location = getattr(content, 'location', '')
                        topics = getattr(content, 'topics', [])
                    
                    scenes_count = len(scenes)
                    
                    # 動画の長さが0の場合、シーンからの計算を試みる
                    if duration == 0 and scenes_count > 0:
                        # シーンの最後のend値または各シーンのdurationの合計を使用
                        try:
                            # end値を使用
                            if isinstance(scenes[0], dict):
                                last_scene = scenes[-1]
                                if 'end' in last_scene:
                                    duration = last_scene['end']
                                elif 'duration' in last_scene:
                                    duration = sum(scene.get('duration', 0) for scene in scenes)
                            # オブジェクトを使用
                            else:
                                last_scene = scenes[-1]
                                if hasattr(last_scene, 'end'):
                                    duration = getattr(last_scene, 'end', 0)
                                elif hasattr(last_scene, 'duration'):
                                    duration = sum(getattr(scene, 'duration', 0) for scene in scenes)
                        except (IndexError, TypeError, AttributeError):
                            # エラーの場合は適当な値を設定
                            duration = scenes_count * 60  # シーン数×60秒と仮定
                            logger.warning(f"ビデオ {i+1} の長さを計算できないため、{duration}秒と推定します")
                    
                    logger.info(f"ビデオ {i+1} ({title}): シーン数={scenes_count}, 長さ={duration}秒, 処理結果={'成功' if scenes_count > 0 else '失敗'}")
                    
                    # 成功したビデオのみコンセプトデータに追加
                    if scenes_count > 0:
                        concept_data['total_duration'] += duration
                        concept_data['total_scenes'] += scenes_count
                        
                        if location:
                            concept_data['locations'].append(location)
                        if topics:
                            concept_data['main_topics'].extend(topics)
                except Exception as e:
                    logger.error(f"ビデオ {i+1} の処理中にエラー: {str(e)}", exc_info=True)
            
            # コンセプトデータの重複を除去
            concept_data['locations'] = list(set(concept_data['locations']))
            concept_data['main_topics'] = list(set(concept_data['main_topics']))
            
            logger.info(f"抽出されたコンセプト: トピック数={len(concept_data['main_topics'])}, 場所={len(concept_data['locations'])}")
            
            # シナリオを作成
            self.concept_data = concept_data
            scenario = self.create_scenario(scenario_input)
            
            logger.info(f"シナリオ生成完了: セクション数={len(scenario['sections'])}")
            return json.dumps(scenario, indent=2, ensure_ascii=False)
        
        except Exception as e:
            error_msg = f"シナリオ生成中にエラーが発生: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return error_msg

    def create_scenario(self, input_data: ScenarioInput) -> Dict:
        """シナリオを生成"""
        if not isinstance(input_data, ScenarioInput):
            raise ValueError("input_data must be a ScenarioInput instance")

        sections = self._plan_sections(input_data)
        
        return {
            "title": input_data.title,
            "concept": {
                "target_audience": input_data.target_audience,
                "style": input_data.style,
                "main_message": input_data.main_message,
                "total_duration": input_data.length
            },
            "sections": [self._format_section(s) for s in sections],
            "notes": self._generate_production_notes(sections),
            "source_materials": {
                "available_scenes": self.concept_data.get('total_scenes', 0),
                "locations": self.concept_data.get('locations', []),
                "main_topics": self.concept_data.get('main_topics', [])
            }
        }

    def _plan_sections(self, input_data: ScenarioInput) -> List[ScenarioSection]:
        """動画のセクションを計画"""
        if not input_data.key_points:
            # キーポイントが空の場合は、イントロとアウトロのみ
            return self._create_minimal_sections(input_data.length)

        total_duration = input_data.length
        sections = []

        # イントロセクション（全体の10%）
        intro_duration = int(total_duration * 0.1)
        sections.append(ScenarioSection(
            title="イントロダクション",
            duration=intro_duration,
            description=f"{input_data.main_message}の導入。{input_data.target_audience}の興味を引く展開。",
            key_scenes=["印象的な風景", "アクティビティのハイライト"],
            narration_notes="視聴者の興味を引く印象的なオープニング"
        ))

        # メインコンテンツ（全体の80%）
        main_duration = int(total_duration * 0.8)
        points_duration = main_duration // len(input_data.key_points)
        for point in input_data.key_points:
            sections.append(ScenarioSection(
                title=f"メインパート: {point}",
                duration=points_duration,
                description=f"{point}に関する詳細な展開",
                key_scenes=self._suggest_scenes_for_point(point),
                narration_notes=f"{input_data.style}のスタイルで{point}を解説"
            ))

        # アウトロ（全体の10%）
        outro_duration = total_duration - sum(s.duration for s in sections)
        sections.append(ScenarioSection(
            title="まとめ",
            duration=outro_duration,
            description=f"{input_data.main_message}のまとめと次のアクションへの誘導",
            key_scenes=["印象的なクロージングショット"],
            narration_notes="主要なポイントの要約とコールトゥアクション"
        ))

        return sections

    def _create_minimal_sections(self, total_duration: int) -> List[ScenarioSection]:
        """キーポイントが空の場合の最小構成を作成"""
        intro_duration = int(total_duration * 0.5)
        outro_duration = total_duration - intro_duration
        
        return [
            ScenarioSection(
                title="イントロダクション",
                duration=intro_duration,
                description="基本的な導入",
                key_scenes=["オープニングショット"],
                narration_notes="基本的な導入ナレーション"
            ),
            ScenarioSection(
                title="まとめ",
                duration=outro_duration,
                description="基本的なまとめ",
                key_scenes=["クロージングショット"],
                narration_notes="基本的なまとめナレーション"
            )
        ]

    def _suggest_scenes_for_point(self, point: str) -> List[str]:
        """各ポイントに適したシーンを提案"""
        relevant_topics = [t for t in self.concept_data.get('main_topics', [])
                         if any(word in t.lower() for word in point.lower().split())]
        
        if relevant_topics:
            return [f"{topic}に関連するシーン" for topic in relevant_topics[:2]]
        return ["関連する活動シーン", "説明的なシーン"]

    def _format_section(self, section: ScenarioSection) -> Dict:
        """セクション情報をJSON形式に変換"""
        return {
            "title": section.title,
            "duration": section.duration,
            "description": section.description,
            "key_scenes": section.key_scenes,
            "narration_notes": section.narration_notes
        }

    def _generate_production_notes(self, sections: List[ScenarioSection]) -> Dict:
        """制作上の注意点を生成"""
        return {
            "total_sections": len(sections),
            "estimated_duration": sum(s.duration for s in sections),
            "required_scenes": sum(len(s.key_scenes) for s in sections),
            "available_duration": self.total_available_duration,
            "suggestions": [
                "各セクション間のスムーズな転換を意識する",
                "キーポイントごとに印象的なシーンを選択",
                "ナレーションは視聴者層に合わせたトーンで"
            ]
        } 


class EnhancedScenarioWriter(ScenarioWriter):
    """
    ScenarioWriterを拡張し、感情、トピック、シーンタイプを考慮したシナリオ作成機能を提供
    """
    
    def __init__(self, concept_data: Dict = None):
        super().__init__(concept_data)
        self.emotion_keywords = {
            "exciting": ["ドラマチック", "活気", "熱狂", "挑戦", "冒険"],
            "calm": ["静か", "穏やか", "平和", "リラックス", "くつろぎ"],
            "inspiring": ["感動", "モチベーション", "情熱", "達成感", "成長"],
            "informative": ["詳細", "説明", "解説", "情報", "学び"],
            "humorous": ["面白い", "ユーモア", "笑い", "楽しさ", "遊び心"]
        }
        self.scene_types = {
            "establishing": "場所や状況を紹介する広角ショット",
            "action": "活動や動きが含まれるダイナミックなショット",
            "closeup": "詳細や感情を捉える接写ショット",
            "interview": "会話や説明を含むショット",
            "montage": "複数の短いショットをつなげた連続シーン"
        }
        logger.info("EnhancedScenarioWriter initialized with emotion and scene type support")
    
    def parse_scenario(self, description: str) -> Dict:
        """
        シナリオの説明文からクエリ情報を抽出
        
        Args:
            description: シナリオセクションの説明文
            
        Returns:
            {
                "emotion": 感情タイプ（exciting/calm/inspiring/informative/humorous）,
                "keywords": 関連キーワード,
                "scene_type": 推奨シーンタイプ
            }
        """
        # 説明文を小文字に変換して単語リストにする
        words = description.lower().split()
        
        # 感情タイプを決定
        emotion_scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for k in keywords if any(w in k.lower() for w in words))
            emotion_scores[emotion] = score
        
        # 最も高いスコアの感情を選択（デフォルトはinformative）
        emotion = max(emotion_scores.items(), key=lambda x: x[1])[0] if any(emotion_scores.values()) else "informative"
        
        # キーワードを抽出（一般的な接続詞や助詞を除く）
        stop_words = ["の", "に", "は", "を", "が", "で", "と", "や", "へ", "から", "まで", "より", "による"]
        keywords = [w for w in words if len(w) > 1 and w not in stop_words]
        
        # シーンタイプを決定
        scene_type = "establishing"  # デフォルト
        if "詳細" in description or "接写" in description:
            scene_type = "closeup"
        elif "活動" in description or "動き" in description:
            scene_type = "action"
        elif "インタビュー" in description or "会話" in description:
            scene_type = "interview"
        elif "連続" in description or "短い" in description:
            scene_type = "montage"
        
        return {
            "emotion": emotion,
            "keywords": keywords[:5],  # 上位5つのキーワード
            "scene_type": scene_type
        }
    
    def _plan_sections(self, input_data: ScenarioInput) -> List[ScenarioSection]:
        """
        動画のセクションを計画（拡張版）
        • 感情や雰囲気の変化を考慮
        • より詳細なシーン提案
        """
        if not input_data.key_points:
            return self._create_minimal_sections(input_data.length)
        
        total_duration = input_data.length
        sections = []
        
        # イントロ（全体の10%）
        intro_duration = int(total_duration * 0.1)
        sections.append(ScenarioSection(
            title="イントロダクション",
            duration=intro_duration,
            description=f"{input_data.main_message}の魅力的な導入。{input_data.target_audience}の興味を引くための{self._get_style_description(input_data.style)}な展開。",
            key_scenes=self._enhanced_scene_suggestions(["導入", "紹介"], "establishing", "exciting"),
            narration_notes=f"簡潔で魅力的な{input_data.main_message}の紹介。{input_data.target_audience}の注目を集める。"
        ))
        
        # メインコンテンツ（全体の80%）
        main_duration = int(total_duration * 0.8)
        
        # キーポイントの数に基づいて、各セクションのストーリーアーク（起承転結）を計画
        num_points = len(input_data.key_points)
        
        if num_points <= 2:
            # ポイント数が少ない場合は、各ポイントに十分な時間を割り当て
            points_duration = main_duration // num_points
            
            for i, point in enumerate(input_data.key_points):
                emotion = "exciting" if i == 0 else "inspiring" if i == num_points - 1 else "informative"
                scene_type = "action" if i % 2 == 0 else "closeup"
                
                sections.append(ScenarioSection(
                    title=f"メインパート {i+1}: {point}",
                    duration=points_duration,
                    description=f"{point}に関する詳細な{self._get_emotion_description(emotion)}展開。{input_data.style}のスタイルで視聴者を引き込む。",
                    key_scenes=self._enhanced_scene_suggestions([point], scene_type, emotion),
                    narration_notes=f"{point}の重要性と詳細を{self._get_style_description(input_data.style)}に解説。"
                ))
        else:
            # ポイント数が多い場合は、ストーリーアークを作成
            # 起：導入（20%）
            intro_points = input_data.key_points[:1]
            intro_points_duration = int(main_duration * 0.2) // len(intro_points)
            
            for point in intro_points:
                sections.append(ScenarioSection(
                    title=f"テーマ導入: {point}",
                    duration=intro_points_duration,
                    description=f"{point}を通した{input_data.main_message}の「起」。背景と基本情報の{self._get_emotion_description('informative')}提示。",
                    key_scenes=self._enhanced_scene_suggestions([point], "establishing", "informative"),
                    narration_notes=f"{point}の背景と基本情報を明確に提示。これから展開する内容の基盤を作る。"
                ))
            
            # 承：展開（30%）
            dev_points = input_data.key_points[1:int(num_points/2)]
            if dev_points:
                dev_points_duration = int(main_duration * 0.3) // len(dev_points)
                
                for point in dev_points:
                    sections.append(ScenarioSection(
                        title=f"展開: {point}",
                        duration=dev_points_duration,
                        description=f"{point}を通した内容の「承」。より詳細な{self._get_emotion_description('exciting')}展開。",
                        key_scenes=self._enhanced_scene_suggestions([point], "action", "exciting"),
                        narration_notes=f"{point}について詳しく説明し、視聴者の関心を高める。"
                    ))
            
            # 転：転換点（30%）
            turn_points = input_data.key_points[int(num_points/2):int(num_points*0.75)]
            if turn_points:
                turn_points_duration = int(main_duration * 0.3) // len(turn_points)
                
                for point in turn_points:
                    sections.append(ScenarioSection(
                        title=f"転換点: {point}",
                        duration=turn_points_duration,
                        description=f"{point}を通した内容の「転」。新たな視点や{self._get_emotion_description('inspiring')}要素の導入。",
                        key_scenes=self._enhanced_scene_suggestions([point], "closeup", "inspiring"),
                        narration_notes=f"{point}によって新たな視点を提示し、視聴者の理解を深める。"
                    ))
            
            # 結：結論（20%）
            conclusion_points = input_data.key_points[int(num_points*0.75):]
            if conclusion_points:
                conclusion_points_duration = (main_duration - sum(s.duration for s in sections) + intro_duration) // len(conclusion_points)
                
                for point in conclusion_points:
                    sections.append(ScenarioSection(
                        title=f"結論: {point}",
                        duration=conclusion_points_duration,
                        description=f"{point}を通した内容の「結」。{input_data.main_message}の重要性を{self._get_emotion_description('inspiring')}強調。",
                        key_scenes=self._enhanced_scene_suggestions([point], "montage", "inspiring"),
                        narration_notes=f"{point}を通して{input_data.main_message}の重要性を改めて強調し、視聴者に行動や考えを促す。"
                    ))
        
        # アウトロ（全体の10%）
        outro_duration = total_duration - sum(s.duration for s in sections)
        sections.append(ScenarioSection(
            title="まとめとコールトゥアクション",
            duration=outro_duration,
            description=f"{input_data.main_message}の要点整理と{input_data.target_audience}への明確なメッセージ。次のアクションへの{self._get_emotion_description('inspiring')}誘導。",
            key_scenes=self._enhanced_scene_suggestions(["まとめ", "締めくくり"], "montage", "inspiring"),
            narration_notes=f"全体のポイントを簡潔にまとめ、{input_data.target_audience}に対して明確なアクションを促す。"
        ))
        
        return sections
    
    def _enhanced_scene_suggestions(self, keywords: List[str], scene_type: str, emotion: str) -> List[str]:
        """
        キーワード、シーンタイプ、感情に基づいた具体的なシーン提案を生成
        
        Args:
            keywords: 関連キーワードのリスト
            scene_type: シーンタイプ（establishing/action/closeup/interview/montage）
            emotion: 感情タイプ（exciting/calm/inspiring/informative/humorous）
            
        Returns:
            提案されたシーンのリスト
        """
        base_suggestions = []
        
        # キーワードからの提案
        for keyword in keywords:
            # コンセプトデータから関連トピックを探す
            relevant_topics = [t for t in self.concept_data.get('main_topics', [])
                             if keyword.lower() in t.lower()]
            
            if relevant_topics:
                base_suggestions.extend([f"{topic}のシーン" for topic in relevant_topics[:2]])
            else:
                base_suggestions.append(f"{keyword}に関連するシーン")
        
        # シーンタイプからの提案
        type_desc = self.scene_types.get(scene_type, "一般的なショット")
        base_suggestions.append(f"{type_desc}")
        
        # 感情からの提案
        emotion_keywords = self.emotion_keywords.get(emotion, ["一般的な"])
        base_suggestions.append(f"{emotion_keywords[0] if emotion_keywords else '一般的な'}雰囲気のショット")
        
        # 場所からの提案
        locations = self.concept_data.get('locations', [])
        if locations:
            base_suggestions.append(f"{locations[0]}での{type_desc}")
        
        # 重複除去と整形
        unique_suggestions = []
        for suggestion in base_suggestions:
            if suggestion not in unique_suggestions:
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:4]  # 最大4つの提案を返す
    
    def _get_emotion_description(self, emotion: str) -> str:
        """感情タイプに基づく説明文を生成"""
        descriptions = {
            "exciting": "活気に満ちた",
            "calm": "穏やかな",
            "inspiring": "感動的な",
            "informative": "情報豊かな",
            "humorous": "ユーモアを交えた"
        }
        return descriptions.get(emotion, "")
    
    def _get_style_description(self, style: str) -> str:
        """スタイルに基づく説明文を生成"""
        style_lower = style.lower()
        
        if "ドキュメンタリー" in style_lower:
            return "客観的で情報量の多い"
        elif "チュートリアル" in style_lower or "解説" in style_lower:
            return "段階的でわかりやすい"
        elif "バイラル" in style_lower or "snsショート" in style_lower:
            return "注目を集める簡潔で印象的な"
        elif "冒険" in style_lower or "アクション" in style_lower:
            return "ダイナミックで迫力のある"
        elif "ライフスタイル" in style_lower:
            return "共感を呼ぶ親しみやすい"
        else:
            return "魅力的な" 