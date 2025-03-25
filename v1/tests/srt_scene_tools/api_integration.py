import re
import openai
import logging
from serpapi import GoogleSearch
import srt

class GeminiAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        openai.api_key = self.api_key  # Set API key for OpenAI
        self.logger.info("GeminiAPI initialized")

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
        self.logger = logging.getLogger(__name__)
        self.logger.info("SerperAPI initialized")

    def search(self, query: str, language: str) -> list:
        """Performs a web search using the SerpAPI."""
        try:
            params = {
                "q": query,
                "hl": language,
                "api_key": self.api_key
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            return results.get("organic_results", [])  # Return results or empty list
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
        self.logger = logging.getLogger(__name__)
        self.logger.info("LanguageHandler initialized")

    def get_language_code(self, language_name: str) -> str:
        language_name = language_name.strip().title()
        return self.language_map.get(language_name)


class Scene:
    def __init__(self, start_time: str, end_time: str, text: str):
        self.logger = logging.getLogger(__name__)
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.narration = ""
        self.logger.debug(f"Created new Scene: {self}")

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
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            subtitle_generator = srt.parse(srt_content)
            scenes = []
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
# Replace with your actual API keys
gemini_api_key = "YOUR_GEMINI_API_KEY"
serper_api_key = "YOUR_SERPER_API_KEY"

gemini_api = GeminiAPI(gemini_api_key)
serper_api = SerperAPI(serper_api_key)
language_handler = LanguageHandler()
srt_file_path = "your_srt_file.srt"  # Replace with your file path


# Example usage (assuming you have a SceneSelectionTool and NarrationAdditionTool)
# ... (your code to use these classes)
