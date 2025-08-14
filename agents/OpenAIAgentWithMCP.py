import os
from openai import OpenAI
import json
from typing import Callable, Dict, Any, List, Optional
from mcp_server.mcp_client import MCPManager

MAX_ITERATIONS = os.getenv("MAX_ITERATIONS", "25")


class OpenAIAgentWithMCP:
    """
    An enhanced AI agent that uses OpenAI models and integrates with MCP (Model Context Protocol) servers.
    
    This agent extends the basic OpenAI agent functionality by adding support for MCP tools,
    allowing integration with external services like Playwright, file systems, databases, and more.
    
    Attributes:
        model (str): The OpenAI model to use for completions.
        tool_definitions (List[Dict]): Combined list of regular and MCP tool definitions.
        tool_callables (Dict[str, Callable]): Mapping of tool names to callable functions.
        messages (List[Dict]): Conversation history maintained throughout the session.
        client (OpenAI): Initialized OpenAI client instance.
        mcp_manager (MCPManager): Manager for MCP server connections and tools.
    """
    
    def __init__(self, model: str = None, tool_definitions: List[Dict] = None, 
                 tool_callables: Dict[str, Callable] = None, system_prompt: str = None, 
                 api_base: str = None, api_key: str = None, 
                 mcp_servers_config: Dict[str, Dict[str, Any]] = None):
        """
        Initialize the OpenAI agent with MCP integration.
        
        Args:
            model (str, optional): Model name to use. Defaults to OPENAI_MODEL env var.
            tool_definitions (List[Dict], optional): List of regular tool function definitions.
            tool_callables (Dict[str, Callable], optional): Mapping of regular tool names to functions.
            system_prompt (str, optional): System message to initialize conversation.
            api_base (str, optional): Custom API base URL. Defaults to OPENAI_API_BASE env var.
            api_key (str, optional): API key for authentication. Defaults to OPENAI_API_KEY env var.
            mcp_servers_config (Dict, optional): Configuration for MCP servers.
                Expected format:
                {
                    "playwright": {
                        "command": "npx",
                        "args": ["@playwright/mcp@latest"]
                    }
                }
        """
        self.model = model or os.getenv("OPENAI_MODEL")
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        
        api_base_url = api_base or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1"
        
        self.client = OpenAI(
            base_url=api_base_url,
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize MCP manager if config provided
        self.mcp_manager = None
        if mcp_servers_config:
            self.mcp_manager = MCPManager(mcp_servers_config)
            self._start_mcp_servers()
        
        # Combine regular tools with MCP tools
        self.tool_definitions = tool_definitions or []
        self.tool_callables = tool_callables or {}
        
        if self.mcp_manager:
            # Add MCP tool definitions
            mcp_tools = self.mcp_manager.get_tool_definitions()
            self.tool_definitions.extend(mcp_tools)
            
            # Add MCP tool callables
            mcp_callables = self.mcp_manager.get_tool_callables()
            self.tool_callables.update(mcp_callables)
    
    def _start_mcp_servers(self):
        """Start all configured MCP servers."""
        if not self.mcp_manager:
            return
        
        for server_name in self.mcp_manager.client.servers:
            try:
                success = self.mcp_manager.start_server(server_name)
                if success:
                    print(f"Successfully started MCP server: {server_name}")
                else:
                    print(f"Failed to start MCP server: {server_name}")
            except Exception as e:
                print(f"Error starting MCP server {server_name}: {e}")
    
    def add_mcp_server(self, name: str, command: str, args: List[str], env: Optional[Dict[str, str]] = None):
        """
        Add and start a new MCP server dynamically.
        
        Args:
            name: Name identifier for the server
            command: Command to execute the server
            args: Arguments for the command
            env: Optional environment variables
        """
        if not self.mcp_manager:
            server_config = {name: {"command": command, "args": args}}
            if env:
                server_config[name]["env"] = env
            self.mcp_manager = MCPManager(server_config)
        else:
            # Add to existing manager
            from mcp_server.mcp_client import MCPServer
            self.mcp_manager.client.servers[name] = MCPServer(name, command, args, env)
        
        # Start the new server
        success = self.mcp_manager.start_server(name)
        if success:
            # Update tool definitions and callables
            mcp_tools = self.mcp_manager.get_tool_definitions()
            mcp_callables = self.mcp_manager.get_tool_callables()
            
            # Filter to only new tools from this server
            new_tools = [tool for tool in mcp_tools 
                        if tool["function"]["name"].startswith(f"{name}_")]
            new_callables = {k: v for k, v in mcp_callables.items() 
                           if k.startswith(f"{name}_")}
            
            self.tool_definitions.extend(new_tools)
            self.tool_callables.update(new_callables)
            
            print(f"Added {len(new_tools)} tools from MCP server: {name}")
            return True
        else:
            print(f"Failed to add MCP server: {name}")
            return False
    
    def list_available_tools(self) -> Dict[str, List[str]]:
        """
        List all available tools, categorized by type.
        
        Returns:
            Dict with 'regular' and 'mcp' tool lists
        """
        regular_tools = []
        mcp_tools = []
        
        for tool_def in self.tool_definitions:
            tool_name = tool_def["function"]["name"]
            if "_" in tool_name and any(tool_name.startswith(f"{server}_") 
                                       for server in (self.mcp_manager.client.servers.keys() 
                                                     if self.mcp_manager else [])):
                mcp_tools.append(tool_name)
            else:
                regular_tools.append(tool_name)
        
        return {
            "regular": regular_tools,
            "mcp": mcp_tools
        }

    def run(self, user_prompt: str, max_iterations: int = MAX_ITERATIONS):
        """
        Execute a conversation with the AI agent using non-streaming completion.
        
        This method processes the user's prompt through multiple iterations, handling
        both regular tools and MCP tools, maintaining conversation context until a 
        final response is reached or the maximum iteration limit is exceeded.
        
        Args:
            user_prompt (str): The user's input message to process.
            max_iterations (int, optional): Maximum number of iterations to attempt.
                Defaults to MAX_ITERATIONS environment variable or 25.
        
        Returns:
            str: The final response from the agent or an error message if the task
                could not be completed within the iteration limit.
        
        Raises:
            Exception: Catches and returns API errors as strings.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        for i in range(int(max_iterations)):
            print(f"Iteration {i + 1}")
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    temperature=1,
                    top_p=1,
                    max_tokens=4096
                )
                
                message = completion.choices[0].message
                self.messages.append({
                    "role": message.role,
                    "content": message.content,
                    "tool_calls": [tool_call.model_dump() for tool_call in message.tool_calls] if message.tool_calls else None
                })
                
                if not message.tool_calls:
                    return message.content or ""
                
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if tool_name not in self.tool_callables:
                        print(f"Error: Tool '{tool_name}' not found.")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found.",
                            "tool_call_id": tool_call.id
                        })
                        continue
                    try:
                        print(f"Calling tool: {tool_name} with args: {tool_args}")
                        tool_output = self.tool_callables[tool_name](**tool_args)
                        print(f"Tool output: {tool_output}")
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_output),
                            "tool_call_id": tool_call.id
                        })
                    except Exception as e:
                        print(f"Error executing tool '{tool_name}': {e}")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error executing tool '{tool_name}': {e}",
                            "tool_call_id": tool_call.id
                        })
            except Exception as e:
                print(f"API error: {e}")
                return f"API error: {e}"
                
        return "The agent could not complete the task within the maximum number of iterations."

    def run_with_streaming(self, user_prompt: str, max_iterations: int = MAX_ITERATIONS):
        """
        Execute a conversation with the AI agent using streaming completion.
        
        This method processes the user's prompt with real-time streaming output,
        displaying content as it's generated. It handles reasoning content for
        compatible models and processes both regular and MCP tool calls after streaming completion.
        
        Args:
            user_prompt (str): The user's input message to process.
            max_iterations (int, optional): Maximum number of iterations to attempt.
                Defaults to MAX_ITERATIONS environment variable or 25.
        
        Returns:
            str: The final response from the agent or an error message if the task
                could not be completed within the iteration limit.
        
        Raises:
            Exception: Catches and returns API errors as strings.
        """
        self.messages.append({"role": "user", "content": user_prompt})
        for i in range(int(max_iterations)):
            print(f"Iteration {i + 1}")
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=self.tool_definitions if self.tool_definitions else None,
                    temperature=1,
                    top_p=1,
                    max_tokens=4096,
                    stream=True
                )
                
                full_content = ""
                tool_calls = []
                current_message = {"role": "assistant", "content": ""}
                
                for chunk in completion:
                    reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
                    if reasoning:
                        print(reasoning, end="", flush=True)
                    
                    if chunk.choices[0].delta.content is not None:
                        content_chunk = chunk.choices[0].delta.content
                        full_content += content_chunk
                        print(content_chunk, end='', flush=True)
                    
                    if chunk.choices[0].delta.tool_calls:
                        for tool_call_delta in chunk.choices[0].delta.tool_calls:
                            while len(tool_calls) <= tool_call_delta.index:
                                tool_calls.append({
                                    "id": "",
                                    "type": "function",
                                    "function": {"name": "", "arguments": ""}
                                })
                            
                            if tool_call_delta.id:
                                tool_calls[tool_call_delta.index]["id"] = tool_call_delta.id
                            if tool_call_delta.function:
                                if tool_call_delta.function.name:
                                    tool_calls[tool_call_delta.index]["function"]["name"] = tool_call_delta.function.name
                                if tool_call_delta.function.arguments:
                                    tool_calls[tool_call_delta.index]["function"]["arguments"] += tool_call_delta.function.arguments
                    
                    if chunk.choices[0].delta.role:
                        current_message["role"] = chunk.choices[0].delta.role
                
                print()
                current_message["content"] = full_content
                
                if tool_calls:
                    current_message["tool_calls"] = tool_calls
                
                self.messages.append(current_message)
                
                if not tool_calls:
                    return full_content
                
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    
                    if tool_name not in self.tool_callables:
                        print(f"Error: Tool '{tool_name}' not found.")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found.",
                            "tool_call_id": tool_call["id"]
                        })
                        continue
                    try:
                        print(f"Calling tool: {tool_name} with args: {tool_args}")
                        tool_output = self.tool_callables[tool_name](**tool_args)
                        print(f"Tool output: {tool_output}")
                        self.messages.append({
                            "role": "tool",
                            "content": str(tool_output),
                            "tool_call_id": tool_call["id"]
                        })
                    except Exception as e:
                        print(f"Error executing tool '{tool_name}': {e}")
                        self.messages.append({
                            "role": "tool",
                            "content": f"Error executing tool '{tool_name}': {e}",
                            "tool_call_id": tool_call["id"]
                        })
            except Exception as e:
                print(f"API error: {e}")
                return f"API error: {e}"
                
        return "The agent could not complete the task within the maximum number of iterations."
    
    def __del__(self):
        """Cleanup MCP resources when object is destroyed."""
        if self.mcp_manager:
            try:
                self.mcp_manager.stop_all_servers()
            except:
                pass
