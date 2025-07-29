import os
from dotenv import load_dotenv
from openai import AsyncOpenAI # Changed to AsyncOpenAI
from nodes.base import BaseNode

# Load environment variables from .env file
load_dotenv()

class CodeGenerator(BaseNode):
    """
    Node to generate code based on a text prompt using the OpenAI API.
    It expects 'processed_input' (the user's code generation request) in the store.
    It sets 'generated_code' in the shared store.
    """
    def __init__(self):
        super().__init__("CodeGenerator")
        # Initialize AsyncOpenAI client for asynchronous calls
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            print("Error: OPENAI_API_KEY not found in environment variables for CodeGenerator.")

    async def execute(self, store):
        """
        Generates code based on the 'processed_input' (user's request)
        and stores the result in 'generated_code'.
        """
        code_prompt = store.get("processed_input")
        if not code_prompt:
            print("Error: No 'processed_input' found in store for CodeGenerator.")
            store.set("error", "No code generation prompt provided.")
            return "error"

        print(f"Generating code for prompt: '{code_prompt}'")

        try:
            # Craft a prompt for code generation
            prompt = (
                "Generate code based on the following request. "
                "Provide only the code block, without any additional explanations or conversational text. "
                "If the request is ambiguous, make reasonable assumptions. "
                "Request:\n\n" + code_prompt
            )

            chat_completion = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", # Consider "gpt-4" for more complex code generation
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Generate clean, functional code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000, # Adjust as needed for code length
                temperature=0.7, # Allows for some creativity in code generation
            )

            generated_code = chat_completion.choices[0].message.content.strip()

            store.set("generated_code", generated_code)
            store.set("final_result", generated_code)

            print(f"Successfully generated code. Length: {len(generated_code)} characters.")
            return "success"

        except Exception as e:
            print(f"An error occurred during code generation with OpenAI API: {e}")
            store.set("error", f"Code generation failed: {e}")
            return "code_gen_failed"

