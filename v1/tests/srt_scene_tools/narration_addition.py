import re
import logging
import srt
from api_integration import GeminiAPI, SerperAPI, LanguageHandler, Scene
from scene_selection import SceneSelectionTool, SRTFileParser


class NarrationAdditionTool:
    def __init__(self, srt_file_path: str, gemini_api_key: str, serper_api_key: str):
        self.logger = logging.getLogger(__name__)
        self.gemini_api = GeminiAPI(gemini_api_key)
        self.serper_api = SerperAPI(serper_api_key)
        self.language_handler = LanguageHandler()
        self.scene_selection_tool = SceneSelectionTool(srt_file_path)
        self.logger.info(f"Initialized NarrationAdditionTool for file: {srt_file_path}")

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
        if not language_code:
            self.logger.warning(f"Unsupported language '{language_name}'")
            return []

        selected_scenes = self.scene_selection_tool.select_scenes(scenario, language_code)
        if not selected_scenes:
            self.logger.warning(f"No scenes found for scenario '{scenario}'")
            return []

        for scene in selected_scenes:
            try:
                # Generate narration using the Gemini API
                narration = self.gemini_api.generate_narration(
                    text=scene.text,
                    language=language_name
                )
                
                if narration:
                    scene.append_narration(narration)
                else:
                    self.logger.warning(f"Failed to generate narration for scene: {scene}")
            except Exception as e:
                self.logger.error(f"Error generating narration: {e}")
                continue

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
        self.logger = logging.getLogger(__name__)
        self.file_path = file_path
        self.logger.info(f"Initialized SRTFileParser for file: {file_path}")

    def parse_srt(self) -> list[Scene]:
        """
        Parses an SRT file and returns a list of Scene objects.
        
        Returns:
            list[Scene]: A list of Scene objects containing subtitle information.
            Returns an empty list if there's an error reading or parsing the file.
        """
        try:
            # Read the SRT file content
            with open(self.file_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()

            # Parse the SRT content
            subtitle_generator = srt.parse(srt_content)
            scenes = []
            
            # Convert each subtitle to a Scene object
            for subtitle in subtitle_generator:
                scenes.append(Scene(
                    start_time=str(subtitle.start),
                    end_time=str(subtitle.end),
                    text=subtitle.content
                ))
            return scenes
        except Exception as e:
            self.logger.error(f"Error parsing SRT file: {e}")
            return []  # Return empty list on error


# Example Usage (replace with your actual API keys and file path)
if __name__ == "__main__":
    # Replace with your actual API keys and file path
    gemini_api_key = "YOUR_GEMINI_API_KEY"
    serper_api_key = "YOUR_SERPER_API_KEY"
    srt_file_path = "your_srt_file.srt"

    try:
        narration_tool = NarrationAdditionTool(srt_file_path, gemini_api_key, serper_api_key)
        narrated_scenes = narration_tool.add_narration(
            scenario="introduction",
            language_name="English",
            narration_prompt="Generate a narration for the selected scene."
        )

        for scene in narrated_scenes:
            print(scene)
    except Exception as e:
        print(f"Error: {e}")
