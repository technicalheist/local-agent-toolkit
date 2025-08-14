#!/usr/bin/env python3
"""
Demonstration script showing OpenAI Agent with Playwright MCP integration.

This script demonstrates how the agent can use Playwright tools to:
1. Navigate to a website
2. Take a screenshot
3. Save information to a file

No user interaction required - runs automatically.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path
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

def demo_playwright_integration():
    """Demonstrate Playwright MCP integration with automated tasks."""
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return False
    
    # Define tool callables
    tool_callables = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
        "list_files_by_pattern": list_files_by_pattern,
        "ask_any_question_internet": ask_any_question_internet,
        "mkdir": mkdir,
        "execute_shell_command": execute_shell_command,
    }
    
    # System prompt
    system_prompt = """
    You are a helpful AI assistant with web automation capabilities.
    You can navigate websites, take screenshots, and manage files.
    Always explain what you're doing step by step.
    """
    
    try:
        print("=== Playwright MCP Integration Demo ===\n")
        
        # Create agent with MCP integration
        print("Initializing agent with Playwright MCP integration...")
        agent = create_agent_with_config(
            OpenAIAgentWithMCP,
            tool_definitions=tools,
            tool_callables=tool_callables,
            system_prompt=system_prompt
        )
        
        # Show available tools
        tools_available = agent.list_available_tools()
        print(f"✓ Loaded {len(tools_available['regular'])} regular tools")
        print(f"✓ Loaded {len(tools_available['mcp'])} Playwright MCP tools")
        
        # Demo 1: Take a screenshot of a website
        print("\n--- Demo 1: Taking a screenshot ---")
        response1 = agent.run(
            "Please navigate to https://example.com and take a screenshot. "
            "Save the screenshot with a descriptive filename."
        )
        print(f"Response: {response1}")
        
        # Demo 2: Create a simple report
        print("\n--- Demo 2: Creating a report ---")
        response2 = agent.run(
            "Create a text file called 'demo_report.txt' that contains:\n"
            "1. Today's date\n"
            "2. A summary of what we accomplished\n"
            "3. List of available Playwright tools (just mention there are browser automation tools)"
        )
        print(f"Response: {response2}")
        
        print("\n=== Demo completed successfully! ===")
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = demo_playwright_integration()
    sys.exit(0 if success else 1)
