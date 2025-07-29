🧠 AI Research Assistant Agent
This project implements a modular AI Research Assistant agent capable of processing various types of user queries, including YouTube video summarization, general text summarization, code generation, mathematical problem-solving, and extracting insights from text. It is built using a node-based architecture, allowing for flexible and extensible workflows.
The agent can be run via a simple command-line interface or an interactive Streamlit web application.
✨ Features
 * YouTube Video Processing: Fetches transcripts from YouTube URLs, summarizes them, and extracts key insights.
 * Text Summarization: Summarizes arbitrary text inputs.
 * Code Generation: Generates code snippets based on natural language requests.
 * Mathematical Problem Solving: Solves mathematical queries, including differentiation, and provides steps.
 * Insight Generation: Extracts key insights and takeaways from provided text or summaries.
 * Intent Classification: Dynamically routes user requests to the appropriate processing node using an LLM-based intent classifier.
 * Modular Architecture: Built with a "PocketFlow-style" node-based design for easy extension and maintenance.
 * Streamlit Web UI: Provides an interactive chat interface for a user-friendly experience.
📂 Project Structure
Ai_Assistant/
├── .venv/                      # Python virtual environment (ignored by Git)
├── nodes/                      # Contains individual processing units (nodes)
│   ├── __init__.py             # Makes 'nodes' a Python package
│   ├── base.py                 # Base class for all nodes
│   ├── input_detector.py       # Detects input type (YouTube URL, text)
│   ├── youtube.py              # Fetches YouTube transcripts
│   ├── summarizer.py           # Summarizes text using OpenAI
│   ├── intent.py               # Classifies user intent using OpenAI
│   ├── codegen.py              # Generates code using OpenAI
│   ├── insights.py             # Extracts insights using OpenAI
│   └── math_solver.py          # Solves math problems using OpenAI
├── main.py                     # Command-line entry point & agent core logic
├── flow.py                     # Orchestrates node execution based on input/intent
├── shared_store.py             # Central data store for inter-node communication
├── chat_app.py                 # Streamlit web application
├── requirements.txt            # List of Python dependencies
└── .env                        # Environment variables (e.g., API keys - ignored by Git)

⚙️ Setup Instructions
Prerequisites
 * Python 3.8+ installed on your system.
 * A GitHub account (for publishing/cloning).
 * An OpenAI API Key.
1. Clone the Repository (If starting fresh)
If you haven't already, clone this repository to your local machine:
git clone https://github.com/RohanKamal123/AI-Researcher-Agent.git
cd AI-Researcher-Agent

2. Create a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.
python -m venv .venv

3. Activate the Virtual Environment
 * On Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1

 * On macOS/Linux (Bash/Zsh):
   source ./.venv/bin/activate

4. Install Dependencies
Install all required Python packages using pip:
pip install -r requirements.txt

5. Configure API Key
You need an OpenAI API key to use the LLM-powered nodes (Summarizer, IntentClassifier, CodeGenerator, InsightsNode, MathSolver).
 * Create a file named .env in the root directory of your project (the same directory as main.py).
 * Add your OpenAI API key to this file in the following format:
   OPENAI_API_KEY="your_openai_api_key_here"

   Replace "your_openai_api_key_here" with your actual OpenAI API key.
   * Security Note: The .env file is included in .gitignore to prevent it from being accidentally committed to your public GitHub repository. Never share your API keys publicly!
▶️ How to Run
Option 1: Command-Line Interface (CLI)
This runs the agent directly in your terminal.
 * Ensure your virtual environment is active.
 * Run the main.py script:
   python main.py

 * The script will prompt you to "Enter prompt or URL:".
Option 2: Streamlit Web Application
This provides an interactive chat interface in your web browser.
 * Ensure your virtual environment is active.
 * Run the Streamlit application:
   streamlit run chat_app.py

 * Streamlit will provide a local URL (e.g., http://localhost:8501) which you can open in your web browser to interact with the agent.
🚀 How to Use
Once the application is running (either CLI or Streamlit), you can provide various types of inputs:
 * YouTube URL for Summarization & Insights:
   * Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ (Rick Astley - Never Gonna Give You Up)
   * Example: https://youtu.be/cTD6I4nWWIo (a short video for testing)
 * Text Prompt for Summarization:
   * Example: Summarize the main points of quantum computing for a beginner.
 * Text Prompt for Code Generation:
   * Example: Write a Python function to calculate the Fibonacci sequence up to n terms.
   * Example: Generate a JavaScript function to reverse a string.
 * Text Prompt for Mathematical Query:
   * Example: Differentiate 12x^3
   * Example: Solve for x: 2x + 5 = 15
   * Example: What is the integral of x^2 from 0 to 1?
 * Text Prompt for General Insights/Query:
   * Example: What are the key challenges in adopting renewable energy?
   * Example: Tell me something interesting about black holes.
🔮 Future Enhancements
 * Dedicated Math Library Integration: For more robust and precise mathematical problem-solving, integrate libraries like SymPy.
 * Web Search Node: Add a node to perform web searches for more up-to-date or factual information.
 * File Processing Node: Allow uploading text files or PDFs for summarization and insights.
 * Multi-turn Conversations: Enhance the Streamlit app to maintain more complex conversational context.
 * Tool Use/Function Calling: Implement more advanced LLM capabilities to dynamically call external tools (like a calculator API, a code interpreter, or a search engine) based on user intent.
 * Error Handling Refinements: More granular error messages and recovery mechanisms.
 * Customizable Prompts: Allow users to customize the prompts used for LLM interactions.
Author: Rohan Kamal