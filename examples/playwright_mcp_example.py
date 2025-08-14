#!/usr/bin/env python3
"""
Example script demonstrating OpenAI Agent with Playwright MCP integration.

This script shows how to create an AI agent that can:
1. Use regular file system tools
2. Use Playwright tools for web automation via MCP
3. Combine both types of tools in a single conversation

Make sure you have:
1. OpenAI API key set in environment or .env file
2. Playwright MCP server running (npx @playwright/mcp@latest)
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.OpenAIAgentWithMCP import OpenAIAgentWithMCP
from helper.tools_definition import tools
from helper.tools import (
    list_files, read_file, write_file, list_files_by_pattern,
    ask_any_question_internet, mkdir, execute_shell_command
)
from mcp_server.config_loader import create_agent_with_config

# Load environment variables
load_dotenv()

def main():
    """Main example function."""
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it in your environment or .env file")
        return
    
    # Define regular tool callables (from your existing tools)
    tool_callables = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
        "list_files_by_pattern": list_files_by_pattern,
        # "ask_any_question_internet": ask_any_question_internet,
        "mkdir": mkdir,
        "execute_shell_command": execute_shell_command,
    }
    
    # System prompt that explains available capabilities
    system_prompt = """
    You are an AI assistant with access to both file system operations and web automation capabilities.
    
    Available capabilities:
    1. File Operations: list_files, read_file, write_file, list_files_by_pattern, mkdir
    2. System Operations: execute_shell_command
    3. Internet: ask_any_question_internet
    4. Web Automation: Playwright tools for browser automation (navigate, click, type, screenshot, etc.)
    
    You can combine these tools to help users with various tasks including:
    - File and directory management
    - Web scraping and automation
    - Taking screenshots of websites
    - Testing web applications
    - Data extraction from web pages
    - Searching the internet for information
    
    Always be helpful and explain what you're doing step by step.
    """
    
    # Create the agent with MCP integration using config file
    print("Initializing OpenAI Agent with MCP integration...")
    agent = create_agent_with_config(
        OpenAIAgentWithMCP,
        tool_definitions=tools,
        tool_callables=tool_callables,
        system_prompt=system_prompt
    )
    
    # List available tools
    available_tools = agent.list_available_tools()
    print(f"\nAvailable regular tools: {len(available_tools['regular'])}")
    for tool in available_tools['regular']:
        print(f"  - {tool}")
    
    print(f"\nAvailable MCP tools: {len(available_tools['mcp'])}")
    for tool in available_tools['mcp']:
        print(f"  - {tool}")
    
    # Interactive loop
    print("\n" + "="*60)
    print("OpenAI Agent with Playwright MCP Integration")
    print("="*60)
    print("You can now ask the agent to:")
    print("- Navigate to websites and take screenshots")
    print("- Interact with web pages (click, type, etc.)")
    print("- Manage files and directories")
    print("- Execute system commands")
    print("- Combine multiple operations")
    print("\nType 'quit' to exit")
    print("="*60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\nAgent:")
            response = agent.run(user_input)
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    main()
