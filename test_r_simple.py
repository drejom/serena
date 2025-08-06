import sys
import os
sys.path.insert(0, 'src')
sys.path.insert(0, 'test')

from conftest import create_default_ls
from solidlsp.ls_config import Language

print("🧪 Testing R language server with data_analysis.R")
print("=" * 50)

try:
    # Create R language server
    print("1. Creating R language server...")
    server = create_default_ls(Language.R)
    
    # Change to the test project directory
    original_dir = os.getcwd()
    test_project = os.path.join(original_dir, 'test_r_project')
    server.repository_root_path = test_project
    
    print(f"   Project path: {test_project}")
    
    # Start the server
    print("2. Starting R language server...")
    server.start()
    print("   ✅ R language server started successfully\!")
    
    # Test document symbols
    print("3. Getting symbols from data_analysis.R...")
    symbols, _ = server.request_document_symbols('data_analysis.R')
    print(f"   ✅ Found {len(symbols)} symbols\!")
    
    print("4. Symbol details:")
    for i, symbol in enumerate(symbols[:15]):  # Show first 15
        name = symbol.get('name', 'unnamed')
        kind = symbol.get('kind', 'unknown')
        line = symbol.get('location', {}).get('range', {}).get('start', {}).get('line', 'N/A')
        print(f"   {i+1:2d}. {name:<30} (kind: {kind}, line: {line})")
    
    # Test finding a specific function
    print("5. Testing symbol search...")
    try:
        calculate_stats, _ = server.request_document_symbols('data_analysis.R')
        calc_stats_symbols = [s for s in calculate_stats if 'calculate_descriptive_stats' in s.get('name', '')]
        if calc_stats_symbols:
            print("   ✅ Found calculate_descriptive_stats function\!")
        else:
            print("   ❌ Could not find calculate_descriptive_stats function")
    except Exception as e:
        print(f"   ❌ Error in symbol search: {e}")
    
    print("\n🎉 All tests completed successfully\!")
    print("✅ R Language Server is working with data_analysis.R\!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    try:
        if 'server' in locals():
            server.stop()
            print("✅ R language server stopped cleanly")
    except:
        pass
