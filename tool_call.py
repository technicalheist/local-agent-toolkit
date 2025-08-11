import json
from tools import (
    list_files,
    read_file,
    write_file,
    list_files_by_pattern,
    ask_any_question_internet,
)
from typing import Callable, Dict, Any
import ollama
from pydantic import BaseModel


client = ollama.Client(host="http://localhost:11434")
model_name = "qwen3:4b"
messages = []

class Tasks(BaseModel):
    task: list[str]


available_functions: Dict[str, Callable] = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "list_files_by_pattern": list_files_by_pattern,
    "ask_any_question_internet": ask_any_question_internet,
}


# Step 2: Call the LLM with initial user query and tool reference
def query_llm_with_tool(
    client: ollama.Client, model: str, user_prompt: str, tools: list[Callable]
) -> Any:
    response = client.chat(model, messages=messages, tools=tools)
    return messages, response


# Step 3: Execute any tool calls returned by the model
def handle_tool_calls(response: Any, available_functions: Dict[str, Callable]) -> Any:
    output = None
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            if function_to_call := available_functions.get(tool.function.name):
                output = function_to_call(**tool.function.arguments)
    return output


# Step 4: Send the tool output back to the model and get the final response
def get_final_response(
    client: ollama.Client, model: str, messages: list, response: Any, output: Any
) -> str:
    if response.message.tool_calls:
        # messages.append(response.message)
        messages.append(
            {
                "role": "tool",
                "content": "Prepare a detailed final response based on the user questions and received output: "
                + str(output),
                "name": response.message.tool_calls[0].function.name,
            }
        )
        final_response = client.chat(model, messages=messages)
        return final_response.message.content
    return response.message.content


def perform_task(question):
    global messages
    available_tool_functions = list(available_functions.values())
    user_input = question
    messages.append({"role": "user", "content": user_input})
    messages, response = query_llm_with_tool(
        client, model_name, user_input, available_tool_functions
    )
    messages.append({"role": "system", "content": response.message.content})
    output = handle_tool_calls(response, available_functions)
    print("output response:", output)
    final_result = get_final_response(
        client, model_name, messages, response, output)
    messages.append({"role": "system", "content": final_result})
    return final_result


def structured_output(question):
    available_tool_functions = list(available_functions.keys())
    messages = messages = [
        {
            "role": "system",
            "content": f"""
            You are an intelligent task-decomposition agent. Your objective is to break a given user task into multiple, well-defined subtasks. 
            These subtasks will be provided sequentially, and your role is to ensure each subtask is clear, specific, and follows the required format without deviation. 

            When converting a long task into smaller subtasks:
            - Each subtask must represent one complete action or step toward accomplishing the main task.
            - If the task involves repetition (e.g., "create 10 files"), generate a separate subtask for each instance (e.g., 10 individual subtasks, each specifying the exact file name).
            - Ensure that every subtask is actionable and unambiguous.

            You have access to the following tools in subsequent messages: {available_tool_functions}.
            Use these tools as the basis for determining how to split the main task into smaller subtasks.

            Do not answer the user’s question directly.
            Your sole responsibility is to divide the task into precise, actionable subtasks strictly in the required format.
            """,
        },
        {
            "role": "user",
            "content": question,
        },
    ]
    # print(messages)
    response = client.chat(model=model_name, messages=messages, format=Tasks.model_json_schema())
    task = Tasks.model_validate_json(response.message.content)
    return task.model_dump_json()


if __name__ == "__main__":
    question = "Fetch the latest 5 Narendra modi latest news from the internet and save this inside the file with there title as a text file"
    jsn = structured_output(question)
    tasks = json.loads(jsn)
    i = 0
    if 'task' in tasks:
        for task in tasks['task']:
            print(f"Performing task {i}: {task}")
            result = perform_task(task+' Do not provide any description to the task.  /no_think')
            print(f"Result #######################{i}:", result)
            i += 1
        write_file("messages.json", json.dumps(messages, indent=2))
