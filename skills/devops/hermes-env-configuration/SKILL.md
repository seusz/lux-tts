---
name: hermes-env-configuration
category: devops
description: Guide for manually configuring API keys and environment variables in Hermes Agent .env file
---

# Hermes .env Configuration Guide

## Overview

This skill provides patterns for adding API keys and environment variables to Hermes Agent's `.env` file when they're not pre-configured in the template.

## Common Issues

### Issue: API Key Not in .env.example

Some tools (like Tavily, Exa, Parallel) may not be pre-configured in `.env.example`. You need to manually add them.

### Issue: Unexpected File Format

Lines in `.env` may not have expected newlines. For example:
```
# FIRECRAWL_API_KEY=*** FAL.ai API Key - Image generation
```
instead of:
```
# FIRECRAWL_API_KEY=***

# FAL.ai API Key - Image generation
```

## Solution: Python Script Approach

### Step 1: Inspect the File

```python
from hermes_tools import read_file

# Read the .env file
env_path = "/opt/hermes/.env"
content = read_file(path=env_path, limit=200)["content"]

# Find the insertion point
lines = content.split('\n')
for i, line in enumerate(lines):
    if 'FIRECRAWL' in line or 'FAL' in line:
        print(f"Line {i+1}: {repr(line)}")
```

### Step 2: Add API Key

```python
from hermes_tools import read_file, write_file

# Read .env file
env_path = "/opt/hermes/.env"
with open(env_path, 'r') as f:
    lines = f.readlines()

# Find insertion point (after FIRECRAWL_API_KEY)
insert_index = None
for i, line in enumerate(lines):
    if '# FIRECRAWL_API_KEY=***' in line:
        insert_index = i + 1  # Insert after this line
        break

if insert_index:
    # Insert Tavily configuration
    tavily_lines = [
        "\n",
        "# Tavily API Key - AI-native web search and extract\n",
        "# Get at: https://tavily.com\n",
        "TAVILY_API_KEY=your_actual_api_key_here\n",
    ]
    
    for i, new_line in enumerate(tavily_lines):
        lines.insert(insert_index + i, new_line)
    
    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print("✓ API key added successfully")
else:
    print("✗ Could not find insertion point")
```

## After Adding API Keys

### 1. Restart Docker Container (if applicable)

```bash
docker restart hermes
```

### 2. Verify Configuration

Use the `hermes doctor` command to check if the tool is properly configured.

### 3. Test the Tool

```bash
# Use the tool in a query
"Search for latest AI news using Tavily"
```

## Common API Keys to Add

| Tool | Env Var | Purpose |
|------|---------|---------|
| Tavily | `TAVILY_API_KEY` | AI web search and extraction |
| Exa | `EXA_API_KEY` | AI-native web search |
| Parallel | `PARALLEL_API_KEY` | AI web search and extract |
| Firecrawl | `FIRECRAWL_API_KEY` | Web crawling and extraction |
| Browserbase | `BROWSERBASE_API_KEY` | Browser automation |

## Security Best Practices

1. **Use environment variables** - Never hardcode keys in scripts
2. **Don't share API keys** - Use secure channels for sharing
3. **Rotate keys regularly** - Update keys periodically
4. **Limit permissions** - Use minimal required permissions
5. **Backup .env** - Keep secure backup of configuration

## Troubleshooting

### Problem: Changes not taking effect

**Solution**: Restart the container or process
```bash
docker restart hermes
# or
hermes gateway restart
```

### Problem: Tool still not available

**Solution**: Enable the toolset
```bash
hermes tools enable web
hermes tools list  # Verify it's enabled
```

## Related Skills

- `hermes-agent` - Complete Hermes Agent guide
- `docker-hermes-path-config` - Docker environment configuration
- `troubleshooting-hermes-installation` - Installation troubleshooting