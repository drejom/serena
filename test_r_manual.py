#!/usr/bin/env python3
"""Manual test of R language server with data_analysis.R script."""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_mcp_call(method, params=None):
    """Make a call to the MCP server."""
    if params is None:
        params = {}
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    try:
        # Use the MCP protocol to call the server
        result = subprocess.run([
            "uv", "run", "python", "-c",
            f"""
import json
import sys
from serena.agent import SerenaAgent
from serena.config.serena_config import SerenaConfig

# Load config
config = SerenaConfig.from_config_file()
agent = SerenaAgent(config)

# Call the tool
try:
    result = agent.call_tool("{method}", {json.dumps(params)})
    print(json.dumps({{"result": result}}))
except Exception as e:
    print(json.dumps({{"error": str(e)}}))
"""
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            return {"error": f"Command failed: {result.stderr}"}
            
    except Exception as e:
        return {"error": str(e)}

def main():
    print("🧪 Testing R Language Server with data_analysis.R")
    print("=" * 50)
    
    # Test 1: Activate the test_r_project
    print("\n1. Activating test_r_project...")
    result = test_mcp_call("activate_project", {"project": "test_r_project"})
    if "error" in result:
        print(f"❌ Error activating project: {result['error']}")
        return
    print("✅ Project activated successfully")
    
    # Test 2: List directory contents
    print("\n2. Listing project directory...")
    result = test_mcp_call("list_dir", {"relative_path": "."})
    if "error" in result:
        print(f"❌ Error listing directory: {result['error']}")
        return
    print(f"✅ Directory contents: {result.get('result', 'N/A')}")
    
    # Test 3: Get symbols overview of data_analysis.R
    print("\n3. Getting symbols overview of data_analysis.R...")
    result = test_mcp_call("get_symbols_overview", {"relative_path": "data_analysis.R"})
    if "error" in result:
        print(f"❌ Error getting symbols: {result['error']}")
        print("This might indicate R language server initialization issues")
        return
    print("✅ Symbols found!")
    symbols = result.get('result', [])
    print(f"   Found {len(symbols)} symbols:")
    for symbol in symbols[:10]:  # Show first 10
        name = symbol.get('name', 'unnamed')
        kind = symbol.get('kind', 'unknown')
        print(f"   - {name} (kind: {kind})")
    
    # Test 4: Find a specific symbol
    print("\n4. Finding calculate_descriptive_stats function...")
    result = test_mcp_call("find_symbol", {
        "relative_path": "data_analysis.R",
        "name_path": "calculate_descriptive_stats",
        "include_body": True
    })
    if "error" in result:
        print(f"❌ Error finding symbol: {result['error']}")
        return
    print("✅ Found calculate_descriptive_stats function!")
    
    # Test 5: Search for patterns in the R file
    print("\n5. Searching for function definitions...")
    result = test_mcp_call("search_for_pattern", {
        "relative_path": "data_analysis.R", 
        "substring_pattern": "function"
    })
    if "error" in result:
        print(f"❌ Error searching patterns: {result['error']}")
        return
    print("✅ Pattern search successful!")
    
    print("\n🎉 All tests completed successfully!")
    print("R Language Server is working with data_analysis.R")

if __name__ == "__main__":
    main()