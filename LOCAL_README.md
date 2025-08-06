# Local Installation Guide for Serena with R LSP Support

This fork of Serena includes full R Language Server Protocol (LSP) support. This guide covers installation options for Claude Code and Claude Desktop.

## Prerequisites

### For All Installation Methods
- Python 3.11 (required)
- Git

### For Local R LSP Support (Non-Docker)
- **R** (version 4.0 or later) - Install from https://www.r-project.org/
- **R languageserver package**:
  ```r
  install.packages("languageserver")
  ```
- **uv** (Python package manager) - Install from https://docs.astral.sh/uv/getting-started/installation/

### For Docker Installation
- Docker Desktop or Docker Engine

## Installation Options

### Option 1: Local Installation with uv (Recommended)

1. **Clone this fork:**
   ```bash
   git clone https://github.com/drejom/serena.git
   cd serena
   ```

2. **Install dependencies with uv:**
   ```bash
   uv sync
   ```

3. **Verify R and languageserver are installed:**
   ```bash
   R --version
   R -e "library(languageserver); packageVersion('languageserver')"
   ```

4. **Test the installation:**
   ```bash
   uv run serena-mcp-server --help
   ```

### Option 2: Docker Installation (Self-Contained)

1. **Pull the pre-built container:**
   ```bash
   docker pull ghcr.io/drejom/serena:latest
   ```

2. **Test the container:**
   ```bash
   docker run --rm -i ghcr.io/drejom/serena:latest python --version
   docker run --rm -i ghcr.io/drejom/serena:latest R --version
   ```

## Integration with Claude Code

### Local Installation
```bash
# Navigate to the serena directory
cd /path/to/serena

# Add to Claude Code
claude mcp add serena-r-lsp uv run serena-mcp-server
```

### Docker Installation  
```bash
# Add Docker-based server to Claude Code
claude mcp add serena-r-lsp-docker docker run --rm -i --network host -e SERENA_DOCKER=1 ghcr.io/drejom/serena:latest python -m serena.cli start_mcp_server
```

### Verify Installation
```bash
claude mcp list
```

## Integration with Claude Desktop

### Local Installation

Add to your Claude Desktop `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "serena-r-lsp": {
      "command": "uv",
      "args": ["run", "serena-mcp-server"],
      "cwd": "/absolute/path/to/serena",
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"
      }
    }
  }
}
```

**Important:** Replace `/absolute/path/to/serena` with the actual path to your cloned repository.

### Docker Installation

```json
{
  "mcpServers": {
    "serena-r-lsp": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i", "--network", "host",
        "-e", "SERENA_DOCKER=1",
        "ghcr.io/drejom/serena:latest",
        "python", "-m", "serena.cli", "start_mcp_server"
      ]
    }
  }
}
```

## Configuration Locations

### Claude Desktop Config Files

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

## R Language Server Features

Once installed, Serena provides full R LSP support:

- ✅ **Code Completion**: Function names, arguments, object names
- ✅ **Hover Documentation**: Function signatures and help text
- ✅ **Go to Definition**: Navigate to function/variable definitions
- ✅ **Find References**: Find all usages of symbols
- ✅ **Document Symbols**: Outline view of functions and variables
- ✅ **Syntax Highlighting**: Error detection and warnings
- ✅ **Code Formatting**: Automatic code formatting

## R Project Structure

For optimal R LSP performance, structure your R projects as:

```
my-r-project/
├── DESCRIPTION          # Package metadata
├── NAMESPACE           # Package namespace  
├── R/                 # R source files
│   ├── functions.R
│   ├── utils.R
│   └── models.R
├── tests/             # Test files
│   └── testthat/
├── examples/          # Example scripts
└── data/             # Data files
```

## Troubleshooting

### R Not Found
```bash
# Check R installation
which R
R --version

# Add R to PATH (macOS with Homebrew)
export PATH="/opt/homebrew/bin:$PATH"

# Add R to PATH (macOS with official installer)
export PATH="/usr/local/bin:$PATH"
```

### languageserver Package Issues
```bash
# Install/reinstall languageserver
R -e "install.packages('languageserver', dependencies=TRUE)"

# Check installation
R -e "library(languageserver); packageVersion('languageserver')"
```

### uv Installation Issues
```bash
# Install uv (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install uv (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### Docker Issues
```bash
# Verify Docker is running
docker --version
docker ps

# Test container access
docker run --rm -i ghcr.io/drejom/serena:latest echo "Docker works"
```

### Claude Code Connection Issues
```bash
# Check MCP server status
claude mcp list

# Remove and re-add server
claude mcp remove serena-r-lsp
claude mcp add serena-r-lsp uv run serena-mcp-server
```

### Performance Tips

- **R LSP Startup**: First connection may take 10-15 seconds
- **Large Projects**: Consider using `.Rbuildignore` to exclude large data files
- **Memory Usage**: R LSP may use significant memory for large codebases

## Getting Help

1. **Check logs:** Serena provides detailed logging in `~/.serena/logs/`
2. **Test R LSP directly:** Use `uv run serena-mcp-server` to see startup messages
3. **Verify R setup:** Ensure `R` and `languageserver` work independently
4. **Docker logs:** Use `docker logs <container-id>` for container issues

## Features Beyond R LSP

This Serena installation also includes support for:
- Python, TypeScript/JavaScript, PHP, Go, Rust, C#, Java, Elixir, Clojure, C/C++
- Semantic code editing and symbol manipulation
- Project memory and context management
- Shell command execution
- Git integration

Happy coding with R and Serena! 🎉