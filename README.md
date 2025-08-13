# AI Agent Application

A sophisticated AI agent that can use various tools to answer questions and perform tasks.

## Project Structure

```
agent/
├── app.py                    # Main application entry point
├── helper/                   # Helper modules directory
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Core agent logic
│   ├── tools.py             # Tool implementations
│   ├── tools_definition.py  # Tool definitions
│   └── tool_call.py         # Function for running the agent
├── requirements.txt          # Python dependencies
├── .env                     # Environment variables
└── README.md               # This file
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Linux/Mac
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your `.env` file with required environment variables:
   ```
   MODEL_NAME=gpt-oss
   OLLAMA_HOST=your_ollama_host_url
   ```

## Usage

### 1. Direct Execution (Interactive Mode)

Run the app without any arguments to enter interactive mode:

```bash
python app.py
```

This will start an interactive session where you can ask questions one by one. Type `quit`, `exit`, or `q` to end the session.

### 2. CLI with Question

Pass your question directly as an argument:

```bash
python app.py "List all files in the current directory"
```

### 3. CLI with Flags

Use command-line flags for more control:

```bash
# Ask a question using the --question flag
python app.py --question "What files are in the helper directory?"

# Don't save the conversation history
python app.py --question "Get current time" --no-save

# Save to a custom file
python app.py --question "Create a test directory" --messages-file "my_conversation.json"
```

## Command-Line Options

- `question` (positional): The question to ask the agent
- `-q, --question`: Alternative way to specify the question
- `--no-save`: Don't save the conversation history to a file
- `--messages-file`: Custom filename for saving conversation history (default: `messages.json`)
- `-h, --help`: Show help message

## Examples

```bash
# Interactive mode
python app.py

# Simple question
python app.py "What's the weather like?"

# With custom options
python app.py -q "List directory contents" --messages-file "dir_check.json"

# Without saving conversation
python app.py "Quick calculation: 2+2" --no-save
```

## Available Tools

The agent has access to various tools including:

- **File Operations**: `list_files`, `read_file`, `write_file`, `mkdir`
- **Pattern Matching**: `list_files_by_pattern`
- **Internet Search**: `ask_any_question_internet`
- **Shell Commands**: `execute_shell_command`

## Conversation History

By default, all conversations are saved to `messages.json`. You can:
- Use `--no-save` to skip saving
- Use `--messages-file` to specify a custom filename
- View the conversation history in JSON format

## Notes

- The agent can handle complex multi-step tasks
- Conversations include tool calls and responses for full transparency
- The JSON conversation files can be used for debugging or analysis
- The agent will continue working until it completes the task or reaches the maximum iteration limit
