import json
from dotenv import load_dotenv
from tools import (
    list_files,
    read_file,
    write_file,
    list_files_by_pattern,
    ask_any_question_internet,
)
from agent import OllamaAgent
from tools_definition import tools as tool_definitions

# Load environment variables from .env file
load_dotenv()

# Define the model name
model_name = "qwen3:4b"

# Create a dictionary of callable tool functions
available_functions = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "list_files_by_pattern": list_files_by_pattern,
    "ask_any_question_internet": ask_any_question_internet,
}

if __name__ == "__main__":
    # The user's question
    question = "Fetch the latest 5 Narendra modi latest news from the internet and save this inside the file with there title as a text file"

    # Create an instance of the OllamaAgent
    agent = OllamaAgent(
        model=model_name,
        tool_definitions=tool_definitions,
        tool_callables=available_functions,
        system_prompt="You are a helpful assistant that can call tools to answer questions."
    )

    # Run the agent
    result = agent.run(question)

    # Print the final result
    print("Final Result:", result)

    # Optionally, save the conversation history
    with open("messages.json", "w") as f:
        json.dump(agent.messages, f, indent=2)
