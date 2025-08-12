import os
import ollama
from typing import Callable, Dict, Any, List

class OllamaAgent:
    def __init__(self, model: str, tool_definitions: List[Dict], tool_callables: Dict[str, Callable], system_prompt: str = None):
        self.model = model
        self.tool_definitions = tool_definitions
        self.tool_callables = tool_callables
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=ollama_host)

    def run(self, user_prompt: str, max_iterations: int = 10):
        self.messages.append({"role": "user", "content": user_prompt})

        for i in range(max_iterations):
            print(f"Iteration {i + 1}")
            response = self.client.chat(
                model=self.model,
                messages=self.messages,
                tools=self.tool_definitions
            )

            if 'message' in response and response['message']:
                self.messages.append(response['message'])

                if not response['message'].get('tool_calls'):
                    return response['message']['content']

                tool_calls = response['message']['tool_calls']
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']

                    if tool_name not in self.tool_callables:
                        print(f"Error: Tool '{tool_name}' not found.")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found.",
                            "name": tool_name
                        })
                        continue

                    try:
                        print(f"Calling tool: {tool_name} with args: {tool_args}")
                        tool_output = self.tool_callables[tool_name](**tool_args)
                        print(f"Tool output: {tool_output}")
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_output),
                            "name": tool_name
                        })
                    except Exception as e:
                        print(f"Error executing tool '{tool_name}': {e}")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error executing tool '{tool_name}': {e}",
                            "name": tool_name
                        })
            else:
                print("Error: Empty response from the model.")
                return "The agent received an empty response from the model."


        return "The agent could not complete the task within the maximum number of iterations."
