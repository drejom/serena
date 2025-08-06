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

### Direct Installation (Recommended)

No cloning needed! Use `uvx` to run Serena with R support directly from this repository:

**Add this to your `claude_desktop_config.json` or MCP configuration:**

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

That's it! `uvx` will automatically:
- Fetch Serena from this repository
- Use the `r-language-support` branch
- Install dependencies in an isolated environment
- Run the MCP server with R support

### Alternative: Install Locally

If you prefer a local installation:

```bash
pip install git+https://github.com/drejom/serena.git@r-language-support
```

Then use in your MCP config:
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

**In Claude Code/Desktop**, you can now:
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