import os
from dotenv import load_dotenv
from nodes.base import BaseNode
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv()

class Summarizer(BaseNode):
    """
    Node to summarize text using the OpenAI API.
    It expects 'transcript' (or any text to summarize) in the store.
    It sets 'summary' in the shared store.
    """
    def __init__(self):
        super().__init__("Summarizer")
        # Initialize OpenAI client
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            print("Error: OPENAI_API_KEY not found in environment variables.")
            # You might want to raise an exception or handle this more gracefully
            # if the key is absolutely required for the node to function.

    async def execute(self, store):
        """
        Summarizes the text found in 'transcript' (or 'processed_input' if no transcript)
        using the OpenAI API and stores the result in 'summary'.
        """
        text_to_summarize = store.get("transcript")
        if not text_to_summarize:
            # Fallback to processed_input if no transcript is available
            text_to_summarize = store.get("processed_input")
            if not text_to_summarize:
                print("Error: No text found in store for Summarizer (neither 'transcript' nor 'processed_input').")
                store.set("error", "No text available for summarization.")
                return "error"
            else:
                print("Summarizer: Using 'processed_input' as text to summarize.")
        else:
            print("Summarizer: Using 'transcript' as text to summarize.")


        print(f"Summarizing text of length: {len(text_to_summarize)} characters...")

        try:
            # Define the prompt for summarization
            prompt = (
                "Please summarize the following text concisely and accurately. "
                "Focus on the main points and key information. "
                "Text:\n\n" + text_to_summarize
            )

            # Call the OpenAI API for chat completion
            # Using gpt-3.5-turbo for cost-effectiveness and good performance
            chat_completion = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Or "gpt-4" for higher quality
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500, # Adjust as needed for summary length
                temperature=0.7, # Controls randomness, lower for more focused summaries
            )

            summary = chat_completion.choices[0].message.content.strip()

            store.set("summary", summary)
            print(f"Successfully generated summary. Length: {len(summary)} characters.")
            return "success"

        except Exception as e:
            print(f"An error occurred during summarization with OpenAI API: {e}")
            store.set("error", f"Summarization failed: {e}")
            return "summarization_failed"

