import asyncio
import os
from dotenv import load_dotenv

from shared_store import SharedStore
from flow import Flow

# Load environment variables from .env file at the very beginning
load_dotenv()

async def run_agent_flow(user_input: str) -> SharedStore:
    """
    Runs the AI Research Assistant Agent's flow with a given user input.
    Returns the populated SharedStore object.
    """
    # Check if OPENAI_API_KEY is loaded (optional, but good for early debugging)
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set. Some nodes may not function correctly.")

    store = SharedStore()
    store.set("input", user_input)

    flow = Flow()
    await flow.run(store)
    return store

async def main():
    """
    Main entry point for the AI Research Assistant Agent when run directly.
    """
    user_input = input("Enter prompt or URL: ")
    final_store = await run_agent_flow(user_input)

    print("\n🧠 Final Output:")
    # --- DEBUGGING LINE START ---
    print(f"DEBUG: Value of 'math_solution' in store: {final_store.get('math_solution')}")
    # --- DEBUGGING LINE END ---

    # Check for specific results and print them in order of preference
    if final_store.get("math_solution"):
        print("Math Solution:")
        print(final_store.get("math_solution"))
    elif final_store.get("insights"):
        print("Insights:")
        print(final_store.get("insights"))
    elif final_store.get("generated_code"):
        print("Generated Code:")
        print(final_store.get("generated_code"))
    elif final_store.get("summary"):
        print("Summary:")
        print(final_store.get("summary"))
    elif final_store.get("final_result"):
        print(final_store.get("final_result"))
    elif final_store.get("error"):
        print(f"An error occurred: {final_store.get('error')}")
    else:
        print("No specific final result, summary, code, insights, or math solution generated yet.")


if __name__ == "__main__":
    asyncio.run(main())

