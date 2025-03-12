import re
import openai
import serper_python
from srt import SRTFile

class GeminiAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = self.api_key  # Set API key for OpenAI

    def generate_narration(self, text: str, language: str) -> str:
        """Generates narration using the Gemini API."""
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",  # Or other appropriate engine
                prompt=f"Translate the following text into {language}:\n{text}\n\nGenerate a concise and engaging narration for the above text.",
                max_tokens=150,  # Adjust as needed
                n=1,
                stop=None,
                temperature=0.7,  # Adjust for creativity
            )
            return response.choices[0].text.strip()
        except openai.error.OpenAIError as e:
            print(f"Error generating narration: {e}")
            return ""  # Return empty string on error


class SerperAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.serper = serper_python.SerperAPI(api_key=self.api_key)

    def search(self, query: str, language: str) -> str:
        """Performs a web search using the Serper API."""
        try:
            results = self.serper.search(query=query, language=language)
            return results.get("results", [])  # Return results or empty list
        except Exception as e:
            print(f"Error performing search: {e}")
            return []  # Return empty list on error


class LanguageHandler:
    def __init__(self):
        self.language_map = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
        }

    def get_language_code(self, language_name: str) -> str:
        language_name = language_name.strip().title()
        return self.language_map.get(language_name)


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

gemini_api = GeminiAPI(gemini_api_key)
serper_api = SerperAPI(serper_api_key)
language_handler = LanguageHandler()
srt_file_path = "your_srt_file.srt"  # Replace with your file path


# Example usage (assuming you have a SceneSelectionTool and NarrationAdditionTool)
# ... (your code to use these classes)
