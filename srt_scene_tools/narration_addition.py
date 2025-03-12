import re
from srt import SRTFile
from api_integration import GeminiAPI, SerperAPI, LanguageHandler
from scene_selection import SceneSelectionTool, SRTFileParser


class NarrationAdditionTool:
    def __init__(self, srt_file_path: str, gemini_api_key: str, serper_api_key: str):
        self.gemini_api = GeminiAPI(gemini_api_key)
        self.serper_api = SerperAPI(serper_api_key)
        self.language_handler = LanguageHandler()
        self.scene_selection_tool = SceneSelectionTool(srt_file_path)


    def add_narration(self, scenario: str, language_name: str, narration_prompt: str) -> list[Scene]:
        """
        Generates and adds narration to selected scenes.

        Args:
            scenario: The scenario for scene selection (e.g., "introduction").
            language_name: The name of the language (e.g., "English").
            narration_prompt: The prompt for the narration generation.

        Returns:
            A list of Scene objects with added narration.  Returns an empty list if no scenes are found or if the scenario is invalid.
            Raises TypeError if input types are incorrect.
        """

        if not isinstance(scenario, str) or not isinstance(language_name, str) or not isinstance(narration_prompt, str):
            raise TypeError("Scenario, language_name, and narration_prompt must be strings.")

        language_code = self.language_handler.get_language_code(language_name)
        if language_code is None:
            print(f"Error: Language '{language_name}' not supported.")
            return []

        selected_scenes = self.scene_selection_tool.select_scenes(scenario, language_code)
        if not selected_scenes:
            return []

        for scene in selected_scenes:
            narration = self.gemini_api.generate_narration(scene.text, language_code)
            if narration:
                scene.append_narration(narration)

        return selected_scenes


class Scene:
    def __init__(self, start_time: str, end_time: str, text: str):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.narration = ""

    def append_narration(self, narration: str):
        self.narration += narration + "\n"
        self.text += "\n" + narration

    def __str__(self):
        return f"Start: {self.start_time}, End: {self.end_time}, Text: {self.text}"


class SRTFileParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def parse_srt(self) -> list[Scene]:
        try:
            srt_file = SRTFile(self.file_path)
            scenes = []
            for scene in srt_file:
                scenes.append(Scene(scene.start, scene.end, scene.content))
            return scenes
        except Exception as e:
            print(f"Error parsing SRT file: {e}")
            return []  # Return empty list on error


# Example Usage (replace with your actual API keys and file path)
# Replace with your actual API keys
gemini_api_key = "YOUR_GEMINI_API_KEY"
serper_api_key = "YOUR_SERPER_API_KEY"
srt_file_path = "your_srt_file.srt"  # Replace with your file path
scenario = "introduction"
language_name = "English"
narration_prompt = "Generate a narration for the introduction scene."


try:
    narration_tool = NarrationAdditionTool(srt_file_path, gemini_api_key, serper_api_key)
    narrated_scenes = narration_tool.add_narration(scenario, language_name, narration_prompt)
    for scene in narrated_scenes:
        print(scene)
except TypeError as e:
    print(f"Error: {e}")

