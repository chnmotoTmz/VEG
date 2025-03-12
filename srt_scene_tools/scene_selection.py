import re
from srt import SRTFile
from utils import LanguageHandler, Scene


class SceneSelectionTool:
    def __init__(self, srt_file_path: str):
        self.srt_file_parser = SRTFileParser(srt_file_path)
        self.selected_scenes = []
        self.language_handler = LanguageHandler()

    def select_scenes(self, scenario: str, language: str) -> list[Scene]:
        """
        Selects scenes based on a scenario and language.

        Args:
            scenario: The scenario for scene selection (e.g., "introduction").
            language: The language code (e.g., "en").

        Returns:
            A list of selected Scene objects. Returns an empty list if no scenes are found or if the scenario is invalid.
            Raises TypeError if input types are incorrect.
        """
        if not isinstance(scenario, str) or not isinstance(language, str):
            raise TypeError("Scenario and language must be strings.")

        scenes = self.srt_file_parser.parse_srt()
        if not scenes:
            return []

        # Placeholder for scenario-based selection logic.
        # Replace with your actual selection logic based on keywords or time ranges.
        selected_scenes = []
        for scene in scenes:
            if "introduction" in scenario.lower() and "introduction" in scene.text.lower():
                selected_scenes.append(scene)
        return selected_scenes


class SRTFileParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse_srt(self) -> list[Scene]:
        """Parses an SRT file and returns a list of Scene objects."""
        try:
            srt_file = SRTFile(self.file_path)
            scenes = []
            for scene in srt_file:
                scenes.append(Scene(scene.start, scene.end, scene.content))
            return scenes
        except Exception as e:
            print(f"Error parsing SRT file: {e}")
            return []  # Return empty list on error


# Example Usage (replace with your actual file path and scenario)
# Replace with your actual file path
srt_file_path = "your_srt_file.srt"  # Replace with your file path
scenario = "introduction"
language = "en"

try:
    scene_selection_tool = SceneSelectionTool(srt_file_path)
    selected_scenes = scene_selection_tool.select_scenes(scenario, language)
    for scene in selected_scenes:
        print(scene)
except TypeError as e:
    print(f"Error: {e}")

