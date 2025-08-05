# Adding R Language Server Support to Serena

This document provides a comprehensive guide for implementing R Language Server Protocol (LSP) support in Serena using a Docker-based approach.

## Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Docker Integration Strategy](#docker-integration-strategy)
3. [Implementation Steps](#implementation-steps)
4. [File Structure & Code Examples](#file-structure--code-examples)
5. [Testing Strategy](#testing-strategy)
6. [Configuration Details](#configuration-details)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Future Considerations](#future-considerations)

## Overview & Architecture

### R Language Server Background

The R Language Server is implemented via the `languageserver` R package, which provides:
- Auto-completion
- Go to definition
- Find all references
- Code formatting (using styler)
- Code linting (with lintr integration)
- Documentation on hover
- Symbol navigation

### Integration Points in Serena

R LSP integration requires modifications to several core components:

1. **Language Enum** (`src/solidlsp/ls_config.py`) - Add R as supported language
2. **Language Server Factory** (`src/solidlsp/ls.py`) - Create R language server instances
3. **R Language Server Class** (`src/solidlsp/language_servers/r_language_server.py`) - Main implementation
4. **Test Infrastructure** - Test repositories and test suites
5. **Docker Environment** - Container with R dependencies

## Docker Integration Strategy

### Why Docker for R?

Unlike other language servers that distribute pre-built binaries, R's languageserver requires:
- R runtime installation
- R package dependencies (languageserver + its 75+ recursive dependencies)
- Potential version conflicts with user's R environment

**Docker Benefits:**
- **Dependency Isolation**: R + languageserver in controlled environment
- **Version Consistency**: Pin specific R and package versions
- **Zero User Setup**: No "install R" requirements
- **Cross-Platform**: Identical behavior across OS
- **Enterprise Ready**: Containerized deployment

### Docker Architecture

```
┌─────────────────────┐
│   Serena Container  │
├─────────────────────┤
│ Python + Serena     │
│ R + languageserver  │
│ Other LSP servers   │
└─────────────────────┘
         │
    LSP Protocol
    (stdio/pipes)
         │
┌─────────────────────┐
│ R Language Server   │
│ languageserver::run()│
└─────────────────────┘
```

## Implementation Steps

### Step 1: Update Dockerfile

Modify the existing `Dockerfile` to include R dependencies:

```dockerfile
# In base stage, after existing system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    git \
    ssh \
    # Add R dependencies
    r-base \
    r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# After uv installation, add R package installation
RUN R -e "install.packages('languageserver', repos='https://cran.rstudio.com/', dependencies=TRUE)"
```

### Step 2: Add R to Language Enum

File: `src/solidlsp/ls_config.py`

```python
class Language(str, Enum):
    # ... existing languages ...
    R = "r"
    
    def get_source_fn_matcher(self) -> FilenameMatcher:
        match self:
            # ... existing cases ...
            case self.R:
                return FilenameMatcher("*.R", "*.r", "*.Rmd", "*.Rnw")
```

### Step 3: Update Language Server Factory

File: `src/solidlsp/ls.py`

Add R case to the factory method:

```python
elif config.code_language == Language.R:
    from solidlsp.language_servers.r_language_server import RLanguageServer
    ls = RLanguageServer(config, logger, repository_root_path, solidlsp_settings=solidlsp_settings)
```

### Step 4: Create R Language Server Class

Create `src/solidlsp/language_servers/r_language_server.py`:

```python
import logging
import os
import pathlib
import subprocess
import threading
from overrides import override

from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_config import LanguageServerConfig
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.lsp_protocol_handler.lsp_types import InitializeParams
from solidlsp.lsp_protocol_handler.server import ProcessLaunchInfo
from solidlsp.settings import SolidLSPSettings


class RLanguageServer(SolidLanguageServer):
    """R Language Server implementation using the languageserver R package."""

    @override
    def is_ignored_dirname(self, dirname: str) -> bool:
        # For R projects, ignore common directories
        return super().is_ignored_dirname(dirname) or dirname in [
            "renv",        # R environment management
            "packrat",     # Legacy R package management
            ".Rproj.user", # RStudio project files
            "vignettes",   # Package vignettes (often large)
        ]

    @staticmethod
    def _check_r_installation():
        """Check if R and languageserver are available."""
        try:
            # Check R installation
            result = subprocess.run(
                ["R", "--version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if result.returncode != 0:
                raise RuntimeError("R is not installed or not in PATH")
            
            # Check languageserver package
            result = subprocess.run([
                "R", "--slave", "-e", 
                "if (!require('languageserver', quietly=TRUE)) quit(status=1)"
            ], capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                raise RuntimeError(
                    "R languageserver package is not installed.\n"
                    "Install it with: R -e \"install.packages('languageserver')\""
                )
                
        except FileNotFoundError:
            raise RuntimeError(
                "R is not installed. Please install R from https://www.r-project.org/"
            )

    def __init__(
        self, 
        config: LanguageServerConfig, 
        logger: LanguageServerLogger, 
        repository_root_path: str, 
        solidlsp_settings: SolidLSPSettings
    ):
        # Skip dependency check in Docker environment
        if not os.getenv("SERENA_DOCKER"):
            self._check_r_installation()

        # R command to start language server
        r_cmd = [
            "R", "--slave", "-e", 
            "languageserver::run()"
        ]

        super().__init__(
            config,
            logger,
            repository_root_path,
            ProcessLaunchInfo(cmd=r_cmd, cwd=repository_root_path),
            "r",
            solidlsp_settings,
        )
        self.server_ready = threading.Event()

    @staticmethod
    def _get_initialize_params(repository_absolute_path: str) -> InitializeParams:
        """Initialize params for R Language Server."""
        root_uri = pathlib.Path(repository_absolute_path).as_uri()
        initialize_params = {
            "locale": "en",
            "capabilities": {
                "textDocument": {
                    "synchronization": {
                        "didSave": True,
                        "dynamicRegistration": True
                    },
                    "completion": {
                        "dynamicRegistration": True,
                        "completionItem": {
                            "snippetSupport": True,
                            "commitCharactersSupport": True,
                            "documentationFormat": ["markdown", "plaintext"],
                            "deprecatedSupport": True,
                            "preselectSupport": True,
                        }
                    },
                    "hover": {
                        "dynamicRegistration": True,
                        "contentFormat": ["markdown", "plaintext"]
                    },
                    "definition": {"dynamicRegistration": True},
                    "references": {"dynamicRegistration": True},
                    "documentSymbol": {
                        "dynamicRegistration": True,
                        "hierarchicalDocumentSymbolSupport": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    },
                    "formatting": {"dynamicRegistration": True},
                    "rangeFormatting": {"dynamicRegistration": True},
                },
                "workspace": {
                    "workspaceFolders": True,
                    "didChangeConfiguration": {"dynamicRegistration": True},
                    "symbol": {
                        "dynamicRegistration": True,
                        "symbolKind": {"valueSet": list(range(1, 27))},
                    }
                },
            },
            "processId": os.getpid(),
            "rootPath": repository_absolute_path,
            "rootUri": root_uri,
            "workspaceFolders": [
                {
                    "uri": root_uri,
                    "name": os.path.basename(repository_absolute_path),
                }
            ],
        }
        return initialize_params

    def _start_server(self):
        """Start R Language Server process."""
        
        def window_log_message(msg):
            self.logger.log(f"R LSP: window/logMessage: {msg}", logging.INFO)

        def do_nothing(params):
            return

        def register_capability_handler(params):
            return

        # Register LSP message handlers
        self.server.on_request("client/registerCapability", register_capability_handler)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_notification("$/progress", do_nothing)
        self.server.on_notification("textDocument/publishDiagnostics", do_nothing)

        self.logger.log("Starting R Language Server process", logging.INFO)
        self.server.start()
        
        initialize_params = self._get_initialize_params(self.repository_root_path)
        self.logger.log(
            "Sending initialize request to R Language Server",
            logging.INFO,
        )
        
        init_response = self.server.send.initialize(initialize_params)
        
        # Verify server capabilities
        capabilities = init_response.get("capabilities", {})
        assert "textDocumentSync" in capabilities
        if "completionProvider" in capabilities:
            self.logger.log("R LSP completion provider available", logging.INFO)
        if "definitionProvider" in capabilities:
            self.logger.log("R LSP definition provider available", logging.INFO)

        self.server.notify.initialized({})
        self.completions_available.set()
        
        # R Language Server is ready after initialization
        self.server_ready.set()
```

### Step 5: Create Test Repository

Create `test/resources/repos/r/test_repo/` with sample R files:

**DESCRIPTION**:
```
Package: TestRepo
Title: Test R Package for Serena
Version: 0.1.0
Authors@R: person("Test", "User", email = "test@example.com", role = c("aut", "cre"))
Description: Test package for R language server functionality.
License: MIT
Encoding: UTF-8
LazyData: true
```

**R/utils.R**:
```r
#' Calculate mean of numeric vector
#' @param x numeric vector
#' @return mean value
calculate_mean <- function(x) {
  if (!is.numeric(x)) {
    stop("Input must be numeric")
  }
  mean(x, na.rm = TRUE)
}

#' Create data summary
#' @param data data.frame
#' @return summary statistics
summarize_data <- function(data) {
  list(
    rows = nrow(data),
    cols = ncol(data),
    numeric_cols = sum(sapply(data, is.numeric))
  )
}
```

**R/models.R**:
```r
#' S3 class constructor for LinearModel
#' @param formula model formula
#' @param data data frame
#' @return LinearModel object
create_linear_model <- function(formula, data) {
  model <- lm(formula, data)
  structure(
    list(
      model = model,
      formula = formula,
      data = deparse(substitute(data))
    ),
    class = "LinearModel"
  )
}

#' Print method for LinearModel
print.LinearModel <- function(x, ...) {
  cat("Linear Model:", deparse(x$formula), "\n")
  cat("Data:", x$data, "\n")
  print(summary(x$model))
}
```

**examples/analysis.R**:
```r
# Load required libraries
library(stats)

# Sample data analysis
data <- data.frame(
  x = rnorm(100),
  y = rnorm(100),
  group = sample(c("A", "B"), 100, replace = TRUE)
)

# Use utility functions
mean_x <- calculate_mean(data$x)
summary_stats <- summarize_data(data)

# Create model
model <- create_linear_model(y ~ x + group, data)
print(model)
```

### Step 6: Create Test Suite

Create `test/solidlsp/r/test_r_basic.py`:

```python
import pytest
from solidlsp.ls_config import Language, LanguageServerConfig
from solidlsp.ls import SolidLanguageServer
from solidlsp.ls_logger import LanguageServerLogger
from solidlsp.settings import SolidLSPSettings


@pytest.mark.r
class TestRLanguageServer:
    @pytest.fixture
    def r_repo_path(self):
        """Path to R test repository."""
        import os
        return os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "resources", "repos", "r", "test_repo"
        )

    @pytest.fixture
    def r_language_server(self, r_repo_path):
        """Create R language server instance."""
        config = LanguageServerConfig(code_language=Language.R)
        logger = LanguageServerLogger()
        settings = SolidLSPSettings()
        
        ls = SolidLanguageServer.create(
            config, logger, r_repo_path, settings=settings
        )
        ls.start_server()
        yield ls
        ls.shutdown_server()

    def test_server_initialization(self, r_language_server):
        """Test that R language server initializes correctly."""
        assert r_language_server is not None
        assert r_language_server.server_ready.is_set()

    def test_file_matching(self):
        """Test R file pattern matching."""
        lang = Language.R
        matcher = lang.get_source_fn_matcher()
        
        assert matcher.is_relevant_filename("script.R")
        assert matcher.is_relevant_filename("analysis.r")
        assert matcher.is_relevant_filename("report.Rmd")
        assert matcher.is_relevant_filename("document.Rnw")
        assert not matcher.is_relevant_filename("script.py")

    def test_symbol_retrieval(self, r_language_server, r_repo_path):
        """Test symbol retrieval from R files."""
        import os
        utils_file = os.path.join(r_repo_path, "R", "utils.R")
        
        symbols = r_language_server.get_symbols_from_file(utils_file)
        symbol_names = [s.name for s in symbols]
        
        assert "calculate_mean" in symbol_names
        assert "summarize_data" in symbol_names

    def test_go_to_definition(self, r_language_server, r_repo_path):
        """Test go-to-definition functionality."""
        import os
        example_file = os.path.join(r_repo_path, "examples", "analysis.R")
        
        # Test definition lookup for calculate_mean function call
        definitions = r_language_server.get_definition(
            example_file, line=10, character=15  # approximate position
        )
        
        assert len(definitions) > 0
        assert "utils.R" in definitions[0].file_path

    def test_completions(self, r_language_server, r_repo_path):
        """Test auto-completion functionality."""
        import os
        example_file = os.path.join(r_repo_path, "examples", "analysis.R")
        
        completions = r_language_server.get_completions(
            example_file, line=10, character=5
        )
        
        # Should have some completions available
        assert len(completions) > 0
```

### Step 7: Update Pytest Configuration

Add to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
  # ... existing markers ...
  "r: language server running for R",
]
```

## Configuration Details

### Environment Variables

- `SERENA_DOCKER=1`: Indicates Docker environment (skips local R checks)
- `R_HOME`: R installation directory (auto-detected in most cases)
- `R_LIBS`: Additional R library paths if needed

### LSP Capabilities

The R Language Server supports:

- **Text Synchronization**: File change notifications
- **Completion**: Context-aware auto-completion
- **Hover**: Documentation on hover
- **Definition**: Go to function/variable definitions
- **References**: Find all references
- **Document Symbols**: Navigate symbols within file
- **Workspace Symbols**: Search symbols across project
- **Formatting**: Code formatting using styler package
- **Diagnostics**: Linting using lintr package

### R Project Detection

The language server will detect R projects by looking for:
- `DESCRIPTION` file (R package)
- `.Rproj` file (RStudio project)
- `R/` directory with R source files
- `.Rprofile` or `.Renviron` files

## Testing Strategy

### Unit Tests

1. **Basic Functionality**:
   - Server initialization
   - File pattern matching
   - Symbol retrieval
   - Go-to-definition
   - Auto-completion

2. **R-Specific Features**:
   - S3/S4 class detection
   - Function parameter completion
   - Package namespace resolution
   - Roxygen documentation parsing

3. **Project Structure**:
   - R package detection
   - NAMESPACE file handling
   - Multi-file symbol resolution

### Integration Tests

1. **Docker Environment**:
   - R installation verification
   - languageserver package availability
   - Container startup/shutdown

2. **LSP Protocol**:
   - Message serialization/deserialization
   - Request/response handling
   - Notification processing

### Running Tests

```bash
# Run all R tests
uv run poe test -m "r"

# Run R tests in Docker
docker-compose run serena-dev uv run poe test -m "r"

# Run with verbose output
uv run poe test -m "r" -v
```

## Troubleshooting Guide

### Common Issues

1. **R Not Found in Container**:
   ```
   Error: R is not installed or not in PATH
   ```
   **Solution**: Verify Dockerfile includes R installation and container rebuilds correctly.

2. **languageserver Package Missing**:
   ```
   Error: R languageserver package is not installed
   ```
   **Solution**: Check Dockerfile R package installation step.

3. **LSP Communication Timeout**:
   ```
   Error: Language server did not respond within timeout
   ```
   **Solution**: Increase timeout or check R script syntax in launch command.

4. **Symbol Resolution Issues**:
   - Ensure R project structure is properly detected
   - Check working directory matches R project root
   - Verify R files have valid syntax

### Debugging Tips

1. **Enable LSP Tracing**:
   ```python
   config = LanguageServerConfig(
       code_language=Language.R,
       trace_lsp_communication=True
   )
   ```

2. **Check R Language Server Logs**:
   Look for window/logMessage notifications in LSP communication.

3. **Test R Installation**:
   ```bash
   docker exec -it <container> R --version
   docker exec -it <container> R -e "library(languageserver)"
   ```

4. **Manual LSP Testing**:
   ```bash
   docker exec -it <container> R --slave -e "languageserver::run()"
   ```

## Future Considerations

### Enhancements

1. **R-Specific Features**:
   - Rmarkdown/Quarto support
   - Shiny application detection
   - Package development tools
   - roxygen2 documentation generation

2. **Performance Optimizations**:
   - Lazy loading of R packages
   - Symbol indexing caching
   - Incremental parsing

3. **Advanced LSP Features**:
   - Code actions (refactoring)
   - Semantic highlighting
   - Call hierarchy
   - Type hierarchy

### Maintenance Notes

1. **R Version Updates**:
   - Pin R version in Dockerfile for stability
   - Test with new R releases before updating
   - Monitor languageserver package updates

2. **Dependency Management**:
   - Consider using renv for package management
   - Monitor security updates for R packages
   - Test with minimal vs full R installations

3. **Docker Optimization**:
   - Multi-stage builds to reduce image size
   - Cache R package installations
   - Consider alpine-based R images

### Extension Points

1. **Custom R Configurations**:
   - Support for .Rprofile settings
   - Custom package repositories
   - Environment-specific configurations

2. **IDE Integration**:
   - RStudio project file parsing
   - VSCode R extension compatibility
   - Jupyter R kernel integration

3. **Package Management**:
   - renv project support
   - packrat legacy support
   - Conda R environment detection

## Implementation Checklist

- [ ] Update Dockerfile with R dependencies
- [ ] Add R to Language enum
- [ ] Create RLanguageServer class
- [ ] Update language server factory
- [ ] Create test repository structure
- [ ] Implement test suite
- [ ] Update pytest configuration
- [ ] Test Docker integration
- [ ] Verify LSP communication
- [ ] Document R-specific features
- [ ] Add troubleshooting guide
- [ ] Test cross-platform compatibility

## References

- [R Language Server GitHub](https://github.com/REditorSupport/languageserver)
- [Language Server Protocol Specification](https://microsoft.github.io/language-server-protocol/)
- [R Project Official Site](https://www.r-project.org/)
- [Serena Architecture Documentation](./src/README.md)