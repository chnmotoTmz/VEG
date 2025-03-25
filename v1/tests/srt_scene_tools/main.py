import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import re
import srt
import logging
import logging.config
from api_integration import GeminiAPI, SerperAPI, LanguageHandler, Scene
from scene_selection import SceneSelectionTool
from narration_addition import NarrationAdditionTool


def setup_logging():
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'standard',
                'filename': 'srt_scene_tools.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    })

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    # Initialize GUI
    root = tk.Tk()
    root.title("SRT Narration Generator")

    # Default values
    DEFAULT_GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"  # Replace with your key
    DEFAULT_SERPER_API_KEY = "YOUR_SERPER_API_KEY"  # Replace with your key
    DEFAULT_LANGUAGE = "English"
    DEFAULT_NARRATION_PROMPT = "Generate a narration for the selected scene."

    # Initialize API and tools
    try:
        logger.info("Initializing APIs...")
        gemini_api = GeminiAPI(DEFAULT_GEMINI_API_KEY)
        serper_api = SerperAPI(DEFAULT_SERPER_API_KEY)
        language_handler = LanguageHandler()
        logger.info("APIs initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing APIs: {e}")
        messagebox.showerror("Error", f"Error initializing APIs: {e}")
        return  # Exit if API initialization fails

    srt_file_path = ""  # Initialize as empty string

    def upload_srt():
        nonlocal srt_file_path
        file_path = filedialog.askopenfilename(filetypes=[("SRT Files", "*.srt")])
        if file_path:
            try:
                logger.info(f"Uploading SRT file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    srt_content = f.read()
                subtitle_generator = srt.parse(srt_content)
                # Test parsing to ensure file is valid
                list(subtitle_generator)
                srt_file_path = file_path
                logger.info("SRT file uploaded and parsed successfully")
                messagebox.showinfo("Success", "SRT file uploaded successfully.")
            except Exception as e:
                logger.error(f"Error reading SRT file: {e}")
                messagebox.showerror("Error", f"Error reading SRT file: {e}")
        else:
            messagebox.showerror("Error", "No file selected.")

    def generate_narration():
        scenario = scenario_entry.get()
        language_name = language_entry.get()
        narration_prompt = prompt_entry.get()

        if not srt_file_path:
            messagebox.showerror("Error", "Please upload an SRT file first.")
            return

        try:
            logger.info(f"Starting narration generation - Scenario: {scenario}, Language: {language_name}")
            narration_tool = NarrationAdditionTool(srt_file_path, DEFAULT_GEMINI_API_KEY, DEFAULT_SERPER_API_KEY)
            narrated_scenes = narration_tool.add_narration(scenario, language_name, narration_prompt)

            if narrated_scenes:
                logger.info(f"Successfully generated {len(narrated_scenes)} scenes")
                result_text.delete("1.0", tk.END)
                for scene in narrated_scenes:
                    result_text.insert(tk.END, str(scene) + "\n\n")
            else:
                logger.warning("No scenes selected or language not supported")
                messagebox.showerror("Error", "No scenes selected or language not supported.")
        except Exception as e:
            logger.error(f"Error during narration generation: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")


    # GUI elements
    upload_button = tk.Button(root, text="Upload SRT File", command=upload_srt)
    upload_button.pack()

    scenario_label = tk.Label(root, text="Scenario (e.g., 'introduction'):")
    scenario_label.pack()
    scenario_entry = tk.Entry(root)
    scenario_entry.pack()

    language_label = tk.Label(root, text="Language (e.g., 'English'):")
    language_label.pack()
    language_entry = tk.Entry(root)
    language_entry.pack()

    prompt_label = tk.Label(root, text="Narration Prompt:")
    prompt_label.pack()
    prompt_entry = tk.Entry(root)
    prompt_entry.pack()


    generate_button = tk.Button(root, text="Generate Narration", command=generate_narration)
    generate_button.pack()

    result_text = tk.Text(root, wrap=tk.WORD)
    result_text.pack()


    root.mainloop()


if __name__ == "__main__":
    main()
