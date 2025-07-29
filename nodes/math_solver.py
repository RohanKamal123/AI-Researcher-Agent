import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from nodes.base import BaseNode

# Load environment variables from .env file
load_dotenv()

class MathSolver(BaseNode):
    """
    Node to solve mathematical queries using the OpenAI API.
    It expects 'processed_input' (the mathematical query) in the store.
    It sets 'math_solution' and 'math_solver_reasoning' in the shared store.
    """
    def __init__(self):
        super().__init__("MathSolver")
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            print("Error: OPENAI_API_KEY not found in environment variables for MathSolver.")

    async def execute(self, store):
        """
        Attempts to solve the mathematical query found in 'processed_input'
        and stores the solution in 'math_solution' and the reasoning in 'math_solver_reasoning'.
        """
        math_query = store.get("processed_input")
        if not math_query:
            print("Error: No 'processed_input' found in store for MathSolver.")
            store.set("error", "No mathematical query provided.")
            return "error"

        print(f"Attempting to solve math query: '{math_query}'")

        try:
            # Craft a prompt for mathematical problem-solving
            prompt = (
                "Solve the following mathematical problem. "
                "Provide the solution clearly and concisely. "
                "If it's a differentiation or integration, show the steps. "
                "Problem:\n\n" + math_query
            )

            chat_completion = await self.client.chat.completions.create(
                model="gpt-3.5-turbo", # "gpt-4" might be better for complex math
                messages=[
                    {"role": "system", "content": "You are a highly accurate mathematical assistant. Provide solutions and steps where appropriate."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200, # Adjust as needed for solution length
                temperature=0.1, # Keep low for factual accuracy
            )

            math_solution = chat_completion.choices[0].message.content.strip()

            # NEW: Store the reasoning/explanation from the LLM
            # For math, the solution often *is* the reasoning, but you could ask for separate reasoning
            # or extract it if the LLM provides it. For now, we'll use the solution as the reasoning.
            # If you want a separate reasoning, you'd need a different prompt or a second LLM call.
            math_solver_reasoning = math_solution # Or a more specific reasoning if the LLM provides it separately

            store.set("math_solution", math_solution)
            store.set("math_solver_reasoning", math_solver_reasoning) # Store the reasoning
            print(f"Successfully generated math solution. Length: {len(math_solution)} characters.")
            return "success"

        except Exception as e:
            print(f"An error occurred during math solving with OpenAI API: {e}")
            store.set("error", f"Math solving failed: {e}")
            store.set("math_solver_reasoning", f"Error during math solving: {e}") # Store error as reasoning
            return "math_solver_failed"

