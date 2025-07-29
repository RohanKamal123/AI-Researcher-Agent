import os
from dotenv import load_dotenv
from openai import AsyncOpenAI # Changed to AsyncOpenAI
from nodes.base import BaseNode

# Load environment variables from .env file
load_dotenv()

class InsightsNode(BaseNode):
    """
    Node to generate insights from text (e.g., a summary or transcript) using the OpenAI API.
    It expects 'summary' or 'transcript' (in that order of preference) in the store.
    It sets 'insights' in the shared store.
    """
    def __init__(self):
        super().__init__("InsightsNode")
        # Initialize AsyncOpenAI client for asynchronous calls
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            print("Error: OPENAI_API_KEY not found in environment variables for InsightsNode.")

    async def execute(self, store):
        """
        Generates insights from the available text ('summary' or 'transcript')
        and stores the result in 'insights'.
        """
        text_for_insights = store.get("summary")
        if not text_for_insights:
            text_for_insights = store.get("transcript")
            if not text_for_insights:
                # If no summary or transcript, try to use the original processed_input
                text_for_insights = store.get("processed_input")
                if not text_for_insights:
                    print("Error: No text found in store for InsightsNode (neither 'summary', 'transcript', nor 'processed_input').")
                    store.set("error", "No text available for insights generation.")
                    return "error"
                else:
                    print("InsightsNode: Using 'processed_input' as text for insights.")
            else:
                print("InsightsNode: Using 'transcript' as text for insights.")
        else:
            print("InsightsNode: Using 'summary' as text for insights.")

        print(f"Generating insights from text of length: {len(text_for_insights)} characters...")

        try:
            # Craft a prompt for insights generation
            prompt = (
                "Extract the most important insights, key takeaways, and actionable points "
                "from the following text. Present them as a bulleted list. "
                "Text:\n\n" + text_for_insights
            )

            chat_completion = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Or "gpt-4" for more nuanced insights
                messages=[
                    {"role": "system", "content": "You are an expert analyst. Provide concise and valuable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500, # Adjust as needed for the number/length of insights
                temperature=0.5, # Balance between creativity and factual accuracy
            )

            insights = chat_completion.choices[0].message.content.strip()

            store.set("insights", insights)
            store.set("final_result", insights)  # <-- ADD THIS
            print(f"Successfully generated insights. Length: {len(insights)} characters.")
            return "success"


        except Exception as e:
            print(f"An error occurred during insights generation with OpenAI API: {e}")
            store.set("error", f"Insights generation failed: {e}")
            return "insights_failed"

