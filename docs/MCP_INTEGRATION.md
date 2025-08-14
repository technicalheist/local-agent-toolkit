# MCP Integration with OpenAI Agent

This document explains how to integrate Model Context Protocol (MCP) servers with your OpenAI agent, specifically focusing on the Playwright MCP server for web automation.

## What is MCP?

Model Context Protocol (MCP) is a protocol that allows AI assistants to securely connect to external tools and data sources. It provides a standardized way to integrate various services like web browsers, databases, file systems, and APIs.

## Setup

### 1. Install Prerequisites

Make sure you have Node.js installed, then install the Playwright MCP server:

```bash
npm install -g @playwright/mcp@latest
```

### 2. Configure MCP Servers

Edit the `mcp_config.json` file to enable/disable MCP servers:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "description": "Playwright MCP server for web automation"
    }
  }
}
```

### 3. Use the Enhanced Agent

```python
from agents.OpenAIAgentWithMCP import OpenAIAgentWithMCP
from mcp_server.config_loader import create_agent_with_config

# Create agent with MCP integration
agent = create_agent_with_config(
    OpenAIAgentWithMCP,
    model="gpt-4o-mini",
    system_prompt="You are a helpful assistant with web automation capabilities."
)

# Use the agent
response = agent.run("Take a screenshot of https://example.com")
```

## Available Playwright Tools

Once the Playwright MCP server is running, your agent will have access to tools like:

- `playwright_navigate` - Navigate to a URL
- `playwright_screenshot` - Take screenshots
- `playwright_click` - Click on elements
- `playwright_type` - Type text into forms
- `playwright_wait_for` - Wait for elements or events
- And many more...

## Example Usage

### Taking a Screenshot

```python
response = agent.run("Please take a screenshot of https://github.com and save it")
```

### Web Automation

```python
response = agent.run("""
Go to https://example.com, 
click on the 'About' link, 
and tell me what the page title is
""")
```

### Combining Tools

```python
response = agent.run("""
1. Take a screenshot of https://news.ycombinator.com
2. Save the screenshot to a file called 'hn_screenshot.png'
3. Create a text file with the current date and time
""")
```

## Configuration Options

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_MODEL` - Model to use (default: gpt-4o-mini)
- `MAX_ITERATIONS` - Maximum tool calling iterations (default: 25)

### MCP Server Configuration

Each MCP server in `mcp_config.json` can have:

- `command` - Command to start the server
- `args` - Arguments for the command
- `env` - Environment variables for the server
- `disabled` - Set to true to disable the server

## Troubleshooting

### MCP Server Not Starting

1. Ensure Node.js is installed
2. Install the MCP server: `npm install -g @playwright/mcp@latest`
3. Check that the command and args in config are correct

### Tools Not Available

1. Check that the MCP server started successfully (look for startup messages)
2. Verify the server is responding to initialization requests
3. Make sure your OpenAI API key is set correctly

### Playwright Browser Issues

The Playwright MCP server automatically handles browser installation, but you may need to:

```bash
npx playwright install
```

## Adding More MCP Servers

You can add other MCP servers to extend functionality:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/allowed/path"]
    },
    "sqlite": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-sqlite", "/path/to/db.sqlite"]
    }
  }
}
```

## API Reference

### OpenAIAgentWithMCP

The enhanced agent class that supports MCP integration.

#### Constructor Parameters

- `model` - OpenAI model name
- `tool_definitions` - Regular tool definitions
- `tool_callables` - Regular tool callable functions
- `system_prompt` - System message
- `api_base` - Custom OpenAI API base URL
- `api_key` - OpenAI API key
- `mcp_servers_config` - MCP server configuration dict

#### Methods

- `run(user_prompt, max_iterations)` - Execute with regular completion
- `run_with_streaming(user_prompt, max_iterations)` - Execute with streaming
- `list_available_tools()` - List all available tools
- `add_mcp_server(name, command, args, env)` - Add MCP server dynamically

### MCPManager

Lower-level class for managing MCP server connections.

#### Methods

- `start_server(server_name)` - Start an MCP server
- `call_tool(tool_name, arguments)` - Call an MCP tool
- `get_tool_definitions()` - Get OpenAI-compatible tool definitions
- `stop_server(server_name)` - Stop an MCP server

## Examples

See the `examples/` directory for complete working examples:

- `playwright_mcp_example.py` - Interactive example with Playwright
- `__test__/test_mcp_integration.py` - Integration test
