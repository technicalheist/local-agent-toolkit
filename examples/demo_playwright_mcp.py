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
import time
import signal
import atexit
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.OpenAIAgentWithMCP import OpenAIAgentWithMCP

# Load environment variables
load_dotenv()

# Global variable to track the agent for cleanup
current_agent = None

def cleanup_handler(signum=None, frame=None):
    """Signal handler for clean shutdown."""
    global current_agent
    if current_agent and hasattr(current_agent, 'cleanup'):
        print(f"\nReceived signal {signum}, cleaning up...")
        try:
            current_agent.cleanup()
        except:
            pass
    sys.exit(0)

# Register signal handlers and cleanup
signal.signal(signal.SIGINT, cleanup_handler)
signal.signal(signal.SIGTERM, cleanup_handler)
atexit.register(lambda: cleanup_handler())

def demo_playwright_integration():
    """Demonstrate Playwright MCP integration with automated tasks."""
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        return False
    
    try:
        print("=== Playwright MCP Integration Demo ===\n")
        
        # Create agent with MCP integration
        print("Initializing agent with Playwright MCP integration...")
        # Option 1: Use defaults and load from mcp_config.json
        with OpenAIAgentWithMCP() as agent:
            
            # Store reference for signal handler cleanup
            global current_agent
            current_agent = agent
            
            # Show available tools
            tools_available = agent.list_available_tools()
            print(f"✓ Loaded {len(tools_available['regular'])} regular tools")
            print(f"✓ Loaded {len(tools_available['mcp'])} Playwright MCP tools")
            
            response1 = agent.run_with_streaming(
                "Find the information about latest launch mobile and save the information inside mobile.txt"
            )
            print(f"Response: {response1}")
            
            time.sleep(2)
            
            print("\n--- Demo 2: Creating a report ---")
            response2 = agent.run_with_streaming(
                "Create a text file called 'demo_report.txt' that contains:\n"
                "1. Today's date\n"
                "2. A summary of what we accomplished\n"
                "3. List of available Playwright tools (just mention there are browser automation tools)"
            )
            print(f"Response: {response2}")
            
            print("\n=== Demo completed successfully! ===")
            current_agent = None  # Clear reference
        
        return True
        
    except Exception as e:
        print(f"Demo failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = demo_playwright_integration()
        exit_code = 0 if success else 1
    except KeyboardInterrupt:
        print("\nScript interrupted by user")
        exit_code = 130
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit_code = 1
    finally:
        # Force cleanup of any remaining global agent reference
        if current_agent:
            try:
                current_agent.cleanup()
            except:
                pass
        # Force exit to ensure script terminates
        print("Exiting...")
        os._exit(exit_code)
