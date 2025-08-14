import json
import os
from typing import Dict, Any


def load_mcp_config(config_path: str = None) -> Dict[str, Dict[str, Any]]:
    """
    Load MCP server configuration from JSON file.
    
    Args:
        config_path: Path to the configuration file. If None, looks for mcp_config.json
                    in the same directory as this script.
    
    Returns:
        Dictionary of enabled MCP server configurations
    """
    if config_path is None:
        # Default to mcp_config.json in the project root
        current_dir = os.path.dirname(os.path.dirname(__file__))
        config_path = os.path.join(current_dir, "mcp_config.json")
    
    if not os.path.exists(config_path):
        print(f"Warning: MCP config file not found at {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Filter out disabled servers
        enabled_servers = {}
        for name, server_config in config.get("mcpServers", {}).items():
            if not server_config.get("disabled", False):
                # Remove non-MCP fields for compatibility
                clean_config = {
                    "command": server_config["command"],
                    "args": server_config["args"]
                }
                if "env" in server_config:
                    clean_config["env"] = server_config["env"]
                
                enabled_servers[name] = clean_config
        
        return enabled_servers
        
    except Exception as e:
        print(f"Error loading MCP config: {e}")
        return {}


def create_agent_with_config(agent_class, config_path: str = None, **agent_kwargs):
    """
    Create an agent with MCP configuration loaded from file.
    
    Args:
        agent_class: The agent class to instantiate
        config_path: Path to the MCP configuration file
        **agent_kwargs: Additional arguments for the agent
    
    Returns:
        Initialized agent instance
    """
    mcp_config = load_mcp_config(config_path)
    
    if mcp_config:
        print(f"Loaded MCP configuration for servers: {list(mcp_config.keys())}")
        agent_kwargs['mcp_servers_config'] = mcp_config
    else:
        print("No MCP servers configured")
    
    return agent_class(**agent_kwargs)
