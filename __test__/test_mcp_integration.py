#!/usr/bin/env python3
"""
Test script for OpenAI Agent with MCP integration.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.OpenAIAgentWithMCP import OpenAIAgentWithMCP

# Load environment variables
load_dotenv()

def test_mcp_integration():
    """Test MCP integration with a simple example."""
    
    # Configure MCP servers
    mcp_servers_config = {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        }
    }
    
    try:
        print("Testing MCP integration...")
        
        # Create agent with MCP
        agent = OpenAIAgentWithMCP(
            mcp_servers_config=mcp_servers_config
        )
        
        # Check if tools were loaded
        tools = agent.list_available_tools()
        print(f"Loaded {len(tools['mcp'])} MCP tools")
        
        if tools['mcp']:
            print("MCP tools available:")
            for tool in tools['mcp'][:5]:  # Show first 5
                print(f"  - {tool}")
            if len(tools['mcp']) > 5:
                print(f"  ... and {len(tools['mcp']) - 5} more")
        
        print("✅ MCP integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ MCP integration test failed: {e}")
        return False

if __name__ == "__main__":
    test_mcp_integration()
