#\!/usr/bin/env python
"""Test R language server functionality."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from solidlsp.ls_config import Language

def test_r_lsp():
    """Test basic R language server functionality."""
    print("Testing R Language Server...")
    
    # Test that R language is registered
    print(f"R Language enum: {Language.R}")
    print(f"R file patterns: {Language.R.get_source_fn_matcher()}")
    print(f"R is experimental: {Language.R.is_experimental()}")
    
    # Test importing R language server
    try:
        from solidlsp.language_servers.r_language_server import RLanguageServer
        print("✓ R language server module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import R language server: {e}")
        return 1
    
    # Test that R and languageserver package are available
    import subprocess
    try:
        result = subprocess.run(["R", "--version"], capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("✓ R is installed")
        else:
            print("✗ R is not available")
            return 1
            
        result = subprocess.run(
            ["R", "--quiet", "--slave", "-e", "library(languageserver)"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print("✓ R languageserver package is installed")
        else:
            print("✗ R languageserver package is not installed")
            print("  Install with: R -e \"install.packages('languageserver')\"")
            return 1
    except FileNotFoundError:
        print("✗ R is not installed")
        return 1
    
    print("\n✅ All checks passed\! R language support is ready.")
    return 0

if __name__ == "__main__":
    sys.exit(test_r_lsp())
