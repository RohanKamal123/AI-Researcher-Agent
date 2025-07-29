import asyncio
from nodes.input_detector import InputDetector
from nodes.youtube import YouTubeFetcher
from nodes.summarizer import Summarizer
from nodes.intent import IntentClassifier
from nodes.codegen import CodeGenerator
from nodes.insights import InsightsNode
from nodes.math_solver import MathSolver # NEW: Import MathSolver

class Flow:
    """
    Orchestrates the execution of different nodes based on the detected input type.
    """
    def __init__(self):
        self.input_detector = InputDetector()
        self.youtube_fetcher = YouTubeFetcher()
        self.summarizer = Summarizer()
        self.intent_classifier = IntentClassifier()
        self.code_generator = CodeGenerator()
        self.insights_node = InsightsNode()
        self.math_solver = MathSolver() # NEW: Initialize MathSolver

    async def run(self, store):
        """
        Runs the main orchestration logic.
        """
        print("Starting flow execution...")

        # Step 1: Detect input type
        print("Running InputDetector...")
        input_type = await self.input_detector.run(store)
        print(f"InputDetector finished. Detected type: {input_type}")

        # Step 2: Orchestrate based on input type
        if input_type == "youtube_url":
            print("Flow: Handling YouTube URL...")
            fetch_status = await self.youtube_fetcher.run(store)
            if fetch_status == "success":
                print("YouTubeFetcher finished. Attempting summarization...")
                summarize_status = await self.summarizer.run(store)
                if summarize_status == "success":
                    print("Summarizer finished. Attempting insights generation...")
                    insights_status = await self.insights_node.run(store)
                    if insights_status == "success":
                        store.set("final_result", "YouTube transcript fetched, summarized, and insights generated successfully.")
                    else:
                        store.set("final_result", f"YouTube transcript fetched and summarized, but insights generation failed: {store.get('error')}")
                else:
                    store.set("final_result", f"YouTube transcript fetched, but summarization failed: {store.get('error')}")
            else:
                store.set("final_result", f"Failed to fetch YouTube transcript: {store.get('error')}")

        elif input_type == "text_prompt":
            print("Flow: Handling Text Prompt...")
            intent_return_status = await self.intent_classifier.run(store)
            user_intent = store.get("user_intent")
            print(f"IntentClassifier finished. Detected intent: {user_intent}")

            if intent_return_status != "error":
                if user_intent == "summarize":
                    print("Flow: Intent is 'summarize'. Running Summarizer...")
                    summarize_status = await self.summarizer.run(store)
                    if summarize_status == "success":
                        store.set("final_result", "Text prompt summarized successfully.")
                        insights_status = await self.insights_node.run(store)
                        if insights_status == "success":
                            store.set("final_result", store.get("final_result") + " Insights also generated.")
                        else:
                            store.set("final_result", store.get("final_result") + f" But insights generation failed: {store.get('error')}")
                    else:
                        store.set("final_result", f"Text prompt summarization failed: {store.get('error')}")

                elif user_intent == "code_generation":
                    print("Flow: Intent is 'code_generation'. Running CodeGenerator...")
                    codegen_status = await self.code_generator.run(store)
                    if codegen_status == "success":
                        store.set("final_result", "Code generated successfully.")
                    else:
                        store.set("final_result", f"Code generation failed: {store.get('error')}")

                elif user_intent == "insights" or user_intent == "general_query":
                    print(f"Flow: Intent is '{user_intent}'. Running InsightsNode...")
                    insights_status = await self.insights_node.run(store)
                    if insights_status == "success":
                        store.set("final_result", "Insights generated successfully.")
                    else:
                        store.set("final_result", f"Insights generation failed: {store.get('error')}")

                elif user_intent == "math_query": # Handle math_query intent
                    print("Flow: Intent is 'math_query'. Running MathSolver node.")
                    math_solver_status = await self.math_solver.run(store) # Call MathSolver
                    if math_solver_status == "success":
                        store.set("final_result", "Math query solved successfully.")
                    else:
                        store.set("final_result", f"Math query failed: {store.get('error')}")

                else: # Unknown intent from classifier
                    print("Flow: Unknown intent detected. Defaulting to general response.")
                    store.set("final_result", "Unknown intent. Please rephrase your request.")
            else: # Intent classification itself failed
                store.set("final_result", f"Intent classification failed: {store.get('error')}")

        elif input_type == "error":
            print("Flow: An error occurred during input detection.")
            store.set("final_result", "Error: Could not process input.")
        else:
            print(f"Flow: Unknown input type: {input_type}")
            store.set("final_result", "Unknown input type detected.")

        print("Flow execution finished.")
