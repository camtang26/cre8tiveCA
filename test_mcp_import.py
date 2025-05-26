#!/usr/bin/env python3
"""
Test script to verify python-mcp[server] installation
"""
import sys
import importlib.util

def test_import(module_name):
    """Test if a module can be imported"""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        return False, f"Module {module_name} not found"
    try:
        module = importlib.import_module(module_name)
        return True, f"Successfully imported {module_name}"
    except Exception as e:
        return False, f"Error importing {module_name}: {e}"

def main():
    print("Testing python-mcp installation...\n")
    
    # Test modules
    modules_to_test = [
        "mcp",
        "mcp.server",
        "mcp.server.fastmcp",
        "fastapi",
        "uvicorn",
        "httpx",
        "pydantic"
    ]
    
    results = []
    for module in modules_to_test:
        success, message = test_import(module)
        results.append((module, success, message))
        symbol = "✓" if success else "✗"
        print(f"{symbol} {message}")
    
    # Check python-mcp version
    try:
        import mcp
        version = getattr(mcp, '__version__', 'unknown')
        print(f"\npython-mcp version: {version}")
    except:
        pass
    
    # Summary
    failed = [r for r in results if not r[1]]
    if failed:
        print(f"\n❌ {len(failed)} modules failed to import:")
        for module, _, message in failed:
            print(f"   - {module}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} modules imported successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()