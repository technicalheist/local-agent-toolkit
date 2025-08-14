import asyncio
import json
import subprocess
import logging
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPServer:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


class MCPClient:
    """
    Client for communicating with Model Context Protocol (MCP) servers.
    
    This client manages connections to MCP servers and provides a unified interface
    for accessing tools and resources from various MCP-compatible services.
    """
    
    def __init__(self, servers_config: Dict[str, Dict[str, Any]]):
        """
        Initialize the MCP client with server configurations.
        
        Args:
            servers_config: Dictionary mapping server names to their configurations.
                Expected format:
                {
                    "server_name": {
                        "command": "command_to_run",
                        "args": ["arg1", "arg2"],
                        "env": {"ENV_VAR": "value"}  # optional
                    }
                }
        """
        self.servers = {}
        self.processes = {}
        self.tools = {}
        self.logger = logging.getLogger(__name__)
        
        # Convert config to MCPServer objects
        for name, config in servers_config.items():
            self.servers[name] = MCPServer(
                name=name,
                command=config["command"],
                args=config.get("args", []),
                env=config.get("env")
            )
    
    async def start_server(self, server_name: str) -> bool:
        """
        Start an MCP server process.
        
        Args:
            server_name: Name of the server to start
            
        Returns:
            bool: True if server started successfully, False otherwise
        """
        if server_name not in self.servers:
            self.logger.error(f"Server '{server_name}' not found in configuration")
            return False
            
        server = self.servers[server_name]
        
        try:
            # Prepare environment
            env = dict(os.environ)
            if server.env:
                env.update(server.env)
            
            # Start the process
            process = await asyncio.create_subprocess_exec(
                server.command,
                *server.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            self.processes[server_name] = process
            self.logger.info(f"Started MCP server '{server_name}'")
            
            # Initialize connection and get tools
            await self._initialize_server(server_name)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MCP server '{server_name}': {e}")
            return False
    
    async def _initialize_server(self, server_name: str):
        """Initialize connection with MCP server and get available tools."""
        process = self.processes[server_name]
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": False
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "local-agent-toolkit",
                    "version": "1.0.0"
                }
            }
        }
        
        try:
            # Send request
            request_data = json.dumps(init_request) + "\n"
            process.stdin.write(request_data.encode())
            await process.stdin.drain()
            
            # Read response
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            
            if "error" in response:
                self.logger.error(f"Server initialization error: {response['error']}")
                return
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            notification_data = json.dumps(initialized_notification) + "\n"
            process.stdin.write(notification_data.encode())
            await process.stdin.drain()
            
            # Get available tools
            await self._get_tools(server_name)
            
        except Exception as e:
            self.logger.error(f"Failed to initialize server '{server_name}': {e}")
    
    async def _get_tools(self, server_name: str):
        """Get available tools from the MCP server."""
        process = self.processes[server_name]
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        try:
            request_data = json.dumps(tools_request) + "\n"
            process.stdin.write(request_data.encode())
            await process.stdin.drain()
            
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            
            if "result" in response and "tools" in response["result"]:
                server_tools = {}
                for tool in response["result"]["tools"]:
                    tool_name = f"{server_name}_{tool['name']}"
                    server_tools[tool_name] = {
                        "server": server_name,
                        "original_name": tool["name"],
                        "definition": tool
                    }
                
                self.tools.update(server_tools)
                self.logger.info(f"Loaded {len(server_tools)} tools from server '{server_name}'")
            
        except Exception as e:
            self.logger.error(f"Failed to get tools from server '{server_name}': {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Call a tool on the appropriate MCP server.
        
        Args:
            tool_name: Name of the tool to call (prefixed with server name)
            arguments: Tool arguments
            
        Returns:
            str: Tool execution result
        """
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found"
        
        tool_info = self.tools[tool_name]
        server_name = tool_info["server"]
        original_tool_name = tool_info["original_name"]
        
        if server_name not in self.processes:
            return f"Error: Server '{server_name}' not running"
        
        process = self.processes[server_name]
        
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": original_tool_name,
                "arguments": arguments
            }
        }
        
        try:
            request_data = json.dumps(call_request) + "\n"
            process.stdin.write(request_data.encode())
            await process.stdin.drain()
            
            response_line = await process.stdout.readline()
            response = json.loads(response_line.decode().strip())
            
            if "result" in response:
                if "content" in response["result"]:
                    # Handle content array response
                    content_parts = []
                    for content in response["result"]["content"]:
                        if content["type"] == "text":
                            content_parts.append(content["text"])
                    return "\n".join(content_parts)
                else:
                    return str(response["result"])
            elif "error" in response:
                return f"Tool error: {response['error']['message']}"
            else:
                return "Unknown response format"
                
        except Exception as e:
            self.logger.error(f"Failed to call tool '{tool_name}': {e}")
            return f"Error calling tool: {e}"
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI-compatible tool definitions for all available MCP tools.
        
        Returns:
            List of tool definitions in OpenAI function calling format
        """
        definitions = []
        
        for tool_name, tool_info in self.tools.items():
            tool_def = tool_info["definition"]
            
            # Convert MCP tool definition to OpenAI format
            openai_def = {
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_def.get("description", ""),
                }
            }
            
            if "inputSchema" in tool_def:
                openai_def["function"]["parameters"] = tool_def["inputSchema"]
            
            definitions.append(openai_def)
        
        return definitions
    
    async def stop_server(self, server_name: str):
        """Stop an MCP server."""
        if server_name in self.processes:
            process = self.processes[server_name]
            
            try:
                # First try graceful termination
                process.terminate()
                
                # Wait up to 3 seconds for graceful shutdown
                try:
                    await asyncio.wait_for(process.wait(), timeout=3.0)
                except asyncio.TimeoutError:
                    # If graceful shutdown failed, force kill
                    self.logger.warning(f"Server '{server_name}' didn't terminate gracefully, forcing kill")
                    process.kill()
                    await process.wait()
                    
            except Exception as e:
                self.logger.error(f"Error stopping server '{server_name}': {e}")
                # Try force kill as last resort
                try:
                    process.kill()
                    await process.wait()
                except:
                    pass
            
            del self.processes[server_name]
            
            # Remove tools from this server
            tools_to_remove = [name for name, info in self.tools.items() 
                             if info["server"] == server_name]
            for tool_name in tools_to_remove:
                del self.tools[tool_name]
            
            self.logger.info(f"Stopped MCP server '{server_name}'")
    
    async def stop_all_servers(self):
        """Stop all running MCP servers."""
        for server_name in list(self.processes.keys()):
            await self.stop_server(server_name)


# Synchronous wrapper for easier integration
class MCPManager:
    """
    Synchronous wrapper for MCPClient to integrate with existing OpenAI agent.
    """
    
    def __init__(self, servers_config: Dict[str, Dict[str, Any]]):
        self.client = MCPClient(servers_config)
        self.loop = None
        self._setup_event_loop()
    
    def _setup_event_loop(self):
        """Setup event loop for async operations."""
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
    
    def start_server(self, server_name: str) -> bool:
        """Start an MCP server synchronously."""
        return self.loop.run_until_complete(self.client.start_server(server_name))
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool synchronously."""
        return self.loop.run_until_complete(self.client.call_tool(tool_name, arguments))
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions synchronously."""
        return self.client.get_tool_definitions()
    
    def get_tool_callables(self) -> Dict[str, callable]:
        """Get callable functions for each tool."""
        callables = {}
        for tool_name in self.client.tools:
            def make_tool_callable(tn):
                return lambda **kwargs: self.call_tool(tn, kwargs)
            callables[tool_name] = make_tool_callable(tool_name)
        return callables
    
    def stop_server(self, server_name: str):
        """Stop an MCP server synchronously."""
        self.loop.run_until_complete(self.client.stop_server(server_name))
    
    def stop_all_servers(self):
        """Stop all servers synchronously."""
        if self.loop and not self.loop.is_closed():
            try:
                self.loop.run_until_complete(self.client.stop_all_servers())
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # If we're in an event loop, create a new one
                    import asyncio
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        new_loop.run_until_complete(self.client.stop_all_servers())
                    finally:
                        new_loop.close()
                else:
                    raise
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            self.stop_all_servers()
        except:
            pass
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup."""
        self.stop_all_servers()
        return False
