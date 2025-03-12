import re

class LanguageHandler:
    """Handles language code conversions."""

    def __init__(self):
        # Initialize language mapping (extend as needed)
        self.language_map = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
            # Add more languages as needed
        }

    def get_language_code(self, language_name: str) -> str:
        """Converts a language name to its corresponding ISO 639-1 code.

        Args:
            language_name: The name of the language (e.g., "English").

        Returns:
            The ISO 639-1 code for the language (e.g., "en").
            Returns None if the language is not found.
        """
        language_name = language_name.strip().title()  # Handle variations and case
        return self.language_map.get(language_name)


class Scene:
    """Represents a scene in an SRT file."""

    def __init__(self, start_time: str, end_time: str, text: str):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text
        self.narration = ""  # Store narration for this scene

    def append_narration(self, narration: str):
        """Appends narration to the scene's text."""
        self.narration += narration + "\n"  # Add newline for readability
        self.text += "\n" + narration  # Append to original text

    def __str__(self):
        return f"Start: {self.start_time}, End: {self.end_time}, Text: {self.text}"
