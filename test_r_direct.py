import sys
import os
sys.path.insert(0, 'src')

from solidlsp.ls import create_default_ls
from solidlsp.ls_config import Language

# Create R language server
print("Creating R language server...")
server = create_default_ls(Language.R)
server.repository_root_path = os.path.join(os.getcwd(), 'test_r_project')

try:
    print("Starting R language server...")
    server.start()
    print("✅ R language server started successfully\!")
    
    print("Getting symbols overview...")
    symbols, _ = server.request_document_symbols('data_analysis.R')
    print(f"✅ Found {len(symbols)} symbols in data_analysis.R")
    
    for i, symbol in enumerate(symbols[:10]):  # Show first 10
        name = symbol.get('name', 'unnamed')
        kind = symbol.get('kind', 'unknown')
        print(f"  {i+1}. {name} (kind: {kind})")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    try:
        server.stop()
        print("✅ R language server stopped")
    except:
        pass
