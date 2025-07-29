import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from nodes.base import BaseNode

# Load environment variables
load_dotenv()

class IntentClassifier(BaseNode):
    """
    Node to classify the user's intent from a text prompt using the OpenAI API.
    It expects 'processed_input' in the store.
    It sets 'user_intent' in the store: one of ['summarize', 'code_generation', 'insights', 'math_query', 'general_query', 'unknown'].
    """

    def __init__(self):
        super().__init__("IntentClassifier")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        if not self.client.api_key:
            print("❌ Error: OPENAI_API_KEY not found in environment variables.")

        # Define supported intents
        self.valid_intents = [
            "summarize",
            "code_generation",
            "insights",
            "math_query",
            "general_query"
        ]

    async def execute(self, store):
        user_prompt = store.get("processed_input")
        if not user_prompt:
            print("❌ Error: No 'processed_input' found in store.")
            store.set("error", "No input text to classify.")
            store.set("user_intent", "error")
            return "error"

        print(f"🔍 Classifying intent for prompt: '{user_prompt}'")

        # Prompt for classification
        prompt = (
            f"Classify the following user prompt into one of these categories: {', '.join(self.valid_intents)}. "
            "Respond ONLY with the category name. If it doesn't fit, reply 'unknown'.\n\n"
            f"User Prompt: {user_prompt}"
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant that classifies user intent."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0.0
            )

            classified = response.choices[0].message.content.strip().lower()

            if classified not in self.valid_intents:
                print(f"⚠️ Unrecognized intent '{classified}', defaulting to 'unknown'.")
                classified = "unknown"

            store.set("user_intent", classified)
            print(f"✅ User intent classified as: {classified}")
            return classified

        except Exception as e:
            print(f"❌ Error during intent classification: {e}")
            store.set("error", f"Intent classification failed: {e}")
            store.set("user_intent", "error")
            return "error"
