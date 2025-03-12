import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import re
from srt import SRTFile
from api_integration import GeminiAPI, SerperAPI, LanguageHandler
from scene_selection import SceneSelectionTool
from narration_addition import NarrationAdditionTool


def main():
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
        gemini_api = GeminiAPI(DEFAULT_GEMINI_API_KEY)
        serper_api = SerperAPI(DEFAULT_SERPER_API_KEY)
        language_handler = LanguageHandler()
    except Exception as e:
        messagebox.showerror("Error", f"Error initializing APIs: {e}")
        return  # Exit if API initialization fails

    srt_file_path = ""  # Initialize as empty string

    def upload_srt():
        nonlocal srt_file_path  # Use the nonlocal variable
        file_path = filedialog.askopenfilename(filetypes=[("SRT Files", "*.srt")])
        if file_path:
            srt_file_path = file_path
            messagebox.showinfo("Success", "SRT file uploaded successfully.")
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
            narration_tool = NarrationAdditionTool(srt_file_path, DEFAULT_GEMINI_API_KEY, DEFAULT_SERPER_API_KEY)
            narrated_scenes = narration_tool.add_narration(scenario, language_name, narration_prompt)

            if narrated_scenes:
                result_text.delete("1.0", tk.END)
                for scene in narrated_scenes:
                    result_text.insert(tk.END, str(scene) + "\n\n")
            else:
                messagebox.showerror("Error", "No scenes selected or language not supported.")
        except Exception as e:
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
