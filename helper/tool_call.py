import json
import os
from dotenv import load_dotenv
from .tools import (
    list_files,
    read_file,
    write_file,
    list_files_by_pattern,
    ask_any_question_internet,
    execute_shell_command,
    mkdir
)
from .agent import OllamaAgent
from .tools_definition import tools as tool_definitions

load_dotenv()

def run_agent_with_question(question: str, save_messages: bool = True, messages_file: str = "messages.json"):
    """
    Run the agent with a given question and optionally save the conversation history.
    
    Args:
        question (str): The question to ask the agent
        save_messages (bool): Whether to save the conversation to a JSON file
        messages_file (str): The filename to save messages to
    
    Returns:
        tuple: (result, messages) - The agent's response and conversation history
    """
    model_name = os.getenv("MODEL_NAME", "gpt-oss")
    
    available_functions = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
        "list_files_by_pattern": list_files_by_pattern,
        "ask_any_question_internet": ask_any_question_internet,
        "mkdir": mkdir,
        "execute_shell_command": execute_shell_command,
    }

    agent = OllamaAgent(
        model=model_name,
        tool_definitions=tool_definitions,
        tool_callables=available_functions,
        system_prompt="You are a helpful assistant that can call tools to answer questions."
    )

    result = agent.run(question)

    serializable_messages = []
    for message in agent.messages:
        if hasattr(message, '__dict__'):
            message_dict = {
                'role': message.role,
                'content': message.content
            }
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls_list = []
                for tool_call in message.tool_calls:
                    if hasattr(tool_call, '__dict__'):
                        tool_call_dict = {
                            'function': {
                                'name': tool_call.function.name if hasattr(tool_call.function, 'name') else str(tool_call.function),
                                'arguments': tool_call.function.arguments if hasattr(tool_call.function, 'arguments') else {}
                            }
                        }
                        tool_calls_list.append(tool_call_dict)
                    else:
                        tool_calls_list.append(tool_call)
                message_dict['tool_calls'] = tool_calls_list
            if hasattr(message, 'tool_name') and message.tool_name:
                message_dict['name'] = message.tool_name
            serializable_messages.append(message_dict)
        else:
            serializable_messages.append(message)

    if save_messages:
        with open(messages_file, "w") as f:
            json.dump(serializable_messages, f, indent=2)

    return result, serializable_messages
