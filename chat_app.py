import streamlit as st
import asyncio
import os
from dotenv import load_dotenv

# Import the refactored agent function
from main import run_agent_flow # Assuming run_agent_flow is in main.py

# Load environment variables (important for OpenAI API key)
load_dotenv()

# Set Streamlit page configuration
st.set_page_config(page_title="AI Research Assistant", page_icon="🧠")

st.title("🧠 AI Research Assistant")
st.write("Ask a question, provide a math query, or paste a YouTube link to get started!")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What do you want to research?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Run the agent flow asynchronously
            # Streamlit runs synchronously, so we need to use asyncio.run
            # for the agent's async functions.
            # For complex async in Streamlit, consider `nest_asyncio.apply()`
            # if you encounter RuntimeError: Event loop is already running.
            # For this simple case, asyncio.run should be fine.
            try:
                final_store = asyncio.run(run_agent_flow(prompt))

                # Extract results from the store
                output_content = ""
                if final_store.get("math_solution"):
                    output_content = f"**Math Solution:**\n{final_store.get('math_solution')}"
                elif final_store.get("insights"):
                    output_content = f"**Insights:**\n{final_store.get('insights')}"
                elif final_store.get("generated_code"):
                    output_content = f"**Generated Code:**\n```python\n{final_store.get('generated_code')}\n```" # Format code
                elif final_store.get("summary"):
                    output_content = f"**Summary:**\n{final_store.get('summary')}"
                elif final_store.get("final_result"):
                    output_content = final_store.get("final_result")
                elif final_store.get("error"):
                    output_content = f"**An error occurred:** {final_store.get('error')}"
                else:
                    output_content = "I couldn't generate a specific output for that request."

                st.markdown(output_content)
                st.session_state.messages.append({"role": "assistant", "content": output_content})

            except Exception as e:
                error_message = f"An unexpected error occurred during processing: {e}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

