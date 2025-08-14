# Environment Management Guide

This guide explains how to manage environment variables for the Local Agent Toolkit in different scenarios.

## 🎯 Overview

The Local Agent Toolkit supports multiple ways to manage environment variables, allowing you to use it flexibly across different projects and deployment scenarios.

## 🔧 Configuration Methods

### Method 1: Project-Level .env File (Recommended)

Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env  # or your preferred editor
```

**Benefits:**
- Project-specific configuration
- Version control friendly (add `.env` to `.gitignore`)
- Easy to share configuration templates

**Example .env:**
```bash
CURRENT_AGENT=OLLAMA
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-your-key-here
```

### Method 2: System Environment Variables

Set environment variables at the system level:

```bash
# Linux/Mac
export CURRENT_AGENT=OPENAI
export OPENAI_API_KEY=sk-your-key-here

# Windows Command Prompt
set CURRENT_AGENT=OPENAI
set OPENAI_API_KEY=sk-your-key-here

# Windows PowerShell
$env:CURRENT_AGENT="OPENAI"
$env:OPENAI_API_KEY="sk-your-key-here"
```

**Benefits:**
- Global configuration
- Works across all projects
- No files to manage

### Method 3: Programmatic Configuration

Set variables in your Python code:

```python
import os
from dotenv import load_dotenv

# Load from specific .env file
load_dotenv('/path/to/specific/.env')

# Or set directly
os.environ['CURRENT_AGENT'] = 'OPENAI'
os.environ['OPENAI_API_KEY'] = 'your-key-here'

# Then use the toolkit
from local_agent_toolkit import run_agent_with_question
result, messages = run_agent_with_question("Hello!")
```

**Benefits:**
- Dynamic configuration
- Multiple environment support
- Programmatic control

## 🐳 Deployment Scenarios

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install the toolkit
RUN pip install local-agent-toolkit

# Set environment variables
ENV CURRENT_AGENT=OLLAMA
ENV OLLAMA_BASE_URL=http://ollama-container:11434
ENV OLLAMA_MODEL=llama3.1

# Copy your application
COPY . .

CMD ["local-agent"]
```

Or using environment file:

```bash
# docker-compose.yml
version: '3.8'
services:
  agent:
    image: your-app
    env_file:
      - .env.production
    environment:
      - CURRENT_AGENT=OLLAMA
```

### Cloud Deployment (AWS, GCP, Azure)

#### AWS Lambda
```python
import os

# Environment variables set in Lambda console
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
CURRENT_AGENT = os.environ.get('CURRENT_AGENT', 'OPENAI')

def lambda_handler(event, context):
    from local_agent_toolkit import run_agent_with_question
    question = event.get('question', 'Hello!')
    result, _ = run_agent_with_question(question)
    return {'statusCode': 200, 'body': result}
```

#### Google Cloud Functions
```python
import functions_framework
import os

@functions_framework.http
def agent_endpoint(request):
    # Environment variables set in GCP console
    from local_agent_toolkit import run_agent_with_question
    
    question = request.json.get('question', 'Hello!')
    result, _ = run_agent_with_question(question)
    return {'result': result}
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-app
spec:
  template:
    spec:
      containers:
      - name: agent
        image: your-agent-app
        env:
        - name: CURRENT_AGENT
          value: "OLLAMA"
        - name: OLLAMA_BASE_URL
          value: "http://ollama-service:11434"
        envFrom:
        - secretRef:
            name: agent-secrets  # Contains OPENAI_API_KEY
```

## 🔐 Security Best Practices

### 1. Never Commit Secrets

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
echo ".env.local" >> .gitignore
```

### 2. Use Environment-Specific Files

```bash
.env.example        # Template (commit this)
.env                # Local development (don't commit)
.env.production     # Production (don't commit)
.env.staging        # Staging (don't commit)
.env.test           # Testing (commit if no secrets)
```

### 3. Secret Management Services

#### AWS Secrets Manager
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Use in your application
secrets = get_secret('agent-toolkit-secrets')
os.environ['OPENAI_API_KEY'] = secrets['openai_api_key']
```

#### Azure Key Vault
```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://vault.vault.azure.net/", credential=credential)

# Retrieve secret
openai_key = client.get_secret("openai-api-key").value
os.environ['OPENAI_API_KEY'] = openai_key
```

## 📋 Environment Variables Reference

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `CURRENT_AGENT` | Which agent to use | `OLLAMA` or `OPENAI` |

### Ollama Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OLLAMA_MODEL` | Model name | `llama3.1` | `codellama` |
| `OLLAMA_BASE_URL` | Server URL | `http://localhost:11434` | `http://ollama:11434` |
| `OLLAMA_HOST` | Legacy host variable | - | `http://localhost:11434` |

### OpenAI Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENAI_API_KEY` | API key | - | `sk-proj-...` |
| `OPENAI_MODEL` | Model name | `gpt-4` | `gpt-3.5-turbo` |
| `OPENAI_API_BASE` | Custom API base | - | `https://api.openai.com/v1` |

### Optional Settings

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MAX_ITERATIONS` | Tool call limit | `25` | `50` |
| `WORK_DIRECTORY` | Working directory | `./` | `/app/workspace` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `LOG_FILE` | Log file path | - | `/var/log/agent.log` |
| `MAX_TOOL_CALLS` | Tool call depth | `10` | `15` |
| `REQUEST_TIMEOUT` | Request timeout (seconds) | `30` | `60` |

## 🧪 Testing Different Configurations

### Local Testing Script

```python
#!/usr/bin/env python3
"""Test script for different environment configurations."""

import os
import tempfile
from pathlib import Path

def test_configuration(config_name, env_vars):
    """Test a specific configuration."""
    print(f"\n🧪 Testing {config_name}...")
    
    # Save current environment
    original_env = {key: os.environ.get(key) for key in env_vars.keys()}
    
    try:
        # Set test environment
        for key, value in env_vars.items():
            os.environ[key] = value
        
        # Test the toolkit
        from local_agent_toolkit import run_agent_with_question
        result, _ = run_agent_with_question(
            "Hello! Can you confirm the current configuration?",
            save_messages=False
        )
        print(f"✅ {config_name}: Success")
        print(f"   Result: {result[:100]}...")
        
    except Exception as e:
        print(f"❌ {config_name}: Failed - {e}")
    
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value

# Test configurations
configurations = {
    "Ollama Local": {
        "CURRENT_AGENT": "OLLAMA",
        "OLLAMA_MODEL": "llama3.1",
        "OLLAMA_BASE_URL": "http://localhost:11434"
    },
    "OpenAI": {
        "CURRENT_AGENT": "OPENAI",
        "OPENAI_API_KEY": "your-key-here",  # Replace with real key
        "OPENAI_MODEL": "gpt-3.5-turbo"
    }
}

if __name__ == "__main__":
    for name, config in configurations.items():
        test_configuration(name, config)
```

## 🆘 Troubleshooting

### Common Issues

1. **Environment not loading:**
   ```python
   # Check if .env exists
   from pathlib import Path
   print(f".env exists: {Path('.env').exists()}")
   
   # Force load specific file
   from dotenv import load_dotenv
   load_dotenv('.env', override=True)
   ```

2. **Variables not set:**
   ```python
   import os
   print("Current environment:")
   for key in ['CURRENT_AGENT', 'OLLAMA_MODEL', 'OPENAI_API_KEY']:
       print(f"  {key}: {os.environ.get(key, 'NOT SET')}")
   ```

3. **Path issues:**
   ```python
   # Check working directory
   import os
   print(f"Current directory: {os.getcwd()}")
   print(f"Environment file: {os.path.abspath('.env')}")
   ```

### Debug Mode

Enable debug logging to see configuration loading:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from local_agent_toolkit import run_agent_with_question
# Now you'll see detailed logs
```

## 📚 Additional Resources

- [python-dotenv documentation](https://python-dotenv.readthedocs.io/)
- [Environment variable best practices](https://12factor.net/config)
- [Docker environment variables](https://docs.docker.com/compose/environment-variables/)
- [Kubernetes ConfigMaps and Secrets](https://kubernetes.io/docs/concepts/configuration/)
