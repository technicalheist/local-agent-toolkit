"""
Helper module for the AI Agent application.

This module provides the core functionality for running an AI agent
with tool calling capabilities, including the agent implementation,
tool definitions, and utility functions.

Exports:
    run_agent_with_question: Main function to execute the agent with a question
    OllamaAgent: Core agent class for handling AI interactions
    tools: Tool definitions for function calling
"""

from .tool_call import run_agent_with_question
from .agent import OllamaAgent
from .tools import *
from .tools_definition import tools

__all__ = ['run_agent_with_question', 'OllamaAgent', 'tools']
