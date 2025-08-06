# R Language Support for Serena

This branch adds comprehensive R language support to Serena, enabling R code analysis, symbol navigation, and intelligent editing through the Language Server Protocol (LSP).

## Features

- **R Language Server Integration**: Full LSP support for R code analysis
- **Symbol Recognition**: Automatic detection of R functions, classes, variables, and S3 methods
- **File Pattern Matching**: Supports `.R`, `.r`, `.Rmd`, and `.Rnw` files
- **No Docker Dependencies**: Clean implementation without provisional Docker requirements

## Prerequisites

- R installed on your system (with `languageserver` package)
- Install the R languageserver package: `install.packages("languageserver")`

## Installation for Claude Code & Claude Desktop

### Claude Code Installation (Recommended)

Install directly using the Claude CLI - no cloning needed!

```bash
claude mcp add serena-r -s user -- uvx --from git+https://github.com/drejom/serena.git@r-language-support serena-mcp-server --project /path/to/your/r/project
```

That's it! This command:
- Installs Serena with R support as an MCP server in Claude Code
- Uses `uvx` to fetch directly from this repository's `r-language-support` branch
- Sets it up with user scope (available across all your projects)
- Automatically manages dependencies in an isolated environment

**Verify installation:**
```bash
claude mcp list
```

You should see `serena-r` listed as an available MCP server.

### Claude Desktop Installation

For Claude Desktop, add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "serena-r": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/drejom/serena.git@r-language-support",
        "serena-mcp-server",
        "--project", "/path/to/your/r/project"
      ]
    }
  }
}
```

### Alternative: Local Installation

If you prefer a local installation:

```bash
pip install git+https://github.com/drejom/serena.git@r-language-support
```

Then for Claude Code:
```bash
claude mcp add serena-r -s user -- serena-mcp-server --project /path/to/your/r/project
```

Or for Claude Desktop config:
```json
{
  "mcpServers": {
    "serena-r": {
      "command": "serena-mcp-server",
      "args": ["--project", "/path/to/your/r/project"]
    }
  }
}

## Usage

### In Claude Code

Once installed, you can access R analysis features:

- **View available MCP servers:** Type `/mcp` to see all connected servers
- **Access R project resources:** Type `@` to see R files and symbols from your project
- **Symbol analysis:** "Show me the functions in data_analysis.R"
- **Code navigation:** "Find the definition of calculate_stats function"
- **Intelligent editing:** "Refactor this R function to use dplyr"

### In Claude Desktop

**Direct commands you can use:**
- Get R symbol overviews: "Show me the functions in this R file"
- Navigate R code: "Find the definition of calculate_stats function"  
- Analyze R scripts: "Explain what this R code does"
- Edit R code intelligently with symbol-aware modifications

## Supported R Features

- **Functions**: Standard R functions and closures
- **S3 Methods**: Object-oriented programming with S3 classes
- **Variables**: Global and local variable detection
- **Data Processing**: Data frame operations and statistical functions
- **R Markdown**: Support for `.Rmd` files
- **R Sweave**: Support for `.Rnw` files

## Example

```r
# This R code will be fully analyzed by Serena
calculate_descriptive_stats <- function(data) {
  if (!is.numeric(data)) {
    stop("Input must be numeric")
  }
  
  stats_list <- list(
    mean = mean(data, na.rm = TRUE),
    median = median(data, na.rm = TRUE),
    sd = sd(data, na.rm = TRUE)
  )
  
  return(stats_list)
}
```

## Testing

Verify R support is working:

```bash
cd serena
uv run poe test -m "r"
```

All 4 R language tests should pass:
- Server initialization ✅
- Symbol retrieval ✅  
- File matching ✅
- Language enum ✅

## Troubleshooting

**R languageserver not found:**
```bash
R -e "install.packages('languageserver')"
```

**Permission issues:**
```bash
R --vanilla --quiet --slave -e 'languageserver::run()'
```

## Contributing

This R language support is ready for production use. To contribute improvements:

1. Fork this repository
2. Create a feature branch from `r-language-support`
3. Make your changes
4. Submit a pull request

## Implementation Details

- **R Language Server**: Uses `R --vanilla --quiet --slave -e 'languageserver::run()'`
- **LSP Communication**: Full Language Server Protocol implementation
- **Symbol Kinds**: Functions (kind 12), Variables (kind 13), etc.
- **File Extensions**: `.R`, `.r`, `.Rmd`, `.Rnw`

---

**Ready to use with Claude Code and Claude Desktop!** 🎉