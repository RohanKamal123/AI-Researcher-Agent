import re
from nodes.base import BaseNode

class InputDetector(BaseNode):
        """
        Node to detect the type of user input (e.g., YouTube URL, text prompt).
        It sets 'input_type' and 'processed_input' in the shared store.
        """
        def __init__(self):
            super().__init__("InputDetector")

        async def execute(self, store):
            """
            Executes the input detection logic.
            Checks if the input is a YouTube URL or a general text prompt.
            Updates the shared store with 'input_type' and 'processed_input'.
            """
            user_input = store.get("input")
            if not user_input:
                print("Error: No input found in store for InputDetector.")
                store.set("error", "No input provided.")
                store.set("input_type", "error")
                return "error"

            # Regex to detect YouTube video URLs
            youtube_regex = (
                r"(?:https?://)?(?:www\.)?"
                r"(?:youtube\.com|youtu\.be)/"
                r"(?:watch\?v=|embed/|v/|)([\w-]{11})(?:[?&].*)?"
            )
            match = re.match(youtube_regex, user_input)

            if match:
                video_id = match.group(1)
                store.set("input_type", "youtube_url")
                store.set("processed_input", video_id) # Store just the video ID
                print(f"Detected YouTube URL: {user_input} (Video ID: {video_id})")
                return "youtube_url"
            else:
                store.set("input_type", "text_prompt")
                store.set("processed_input", user_input) # Store the original text
                print(f"Detected Text Prompt: {user_input}")
                return "text_prompt"

    