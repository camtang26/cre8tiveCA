#!/usr/bin/env python3
"""
Robust installation script for MCP servers on Render.com
Handles the python-mcp[server] installation issues
"""
import subprocess
import sys
import os
import json

def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def install_dependencies():
    """Install all dependencies with multiple fallback strategies"""
    
    print("=== Starting Render installation for outlook_mcp_server ===")
    
    # 1. Upgrade pip, setuptools, and wheel
    print("\n1. Upgrading pip, setuptools, and wheel...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    # 2. Read requirements.txt and separate python-mcp
    print("\n2. Processing requirements.txt...")
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    
    other_deps = [req.strip() for req in requirements if not req.strip().startswith("python-mcp")]
    
    # 3. Install all other dependencies first
    if other_deps:
        print("\n3. Installing base dependencies...")
        with open("requirements-temp.txt", "w") as f:
            f.write("\n".join(other_deps))
        run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r", "requirements-temp.txt"])
        os.remove("requirements-temp.txt")
    
    # 4. Try multiple strategies to install python-mcp[server]
    print("\n4. Installing python-mcp with server extras...")
    
    strategies = [
        # Strategy 1: Direct install with extras
        lambda: run_command([
            sys.executable, "-m", "pip", "install", 
            "--no-cache-dir", "python-mcp[server]==1.0.1"
        ], check=False),
        
        # Strategy 2: Install base then extras
        lambda: (
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "python-mcp==1.0.1"], check=False),
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "python-mcp[server]==1.0.1"], check=False)
        ),
        
        # Strategy 3: Install dependencies manually then python-mcp
        lambda: (
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "click>=8.0.0", "pydantic-settings>=2.0.0"], check=False),
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--force-reinstall", "python-mcp[server]==1.0.1"], check=False)
        ),
        
        # Strategy 4: Use --no-deps then install deps
        lambda: (
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "--no-deps", "python-mcp==1.0.1"], check=False),
            run_command([sys.executable, "-m", "pip", "install", "--no-cache-dir", "python-mcp[server]==1.0.1"], check=False)
        )
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"\n  Trying strategy {i}/{len(strategies)}...")
        result = strategy()
        
        # Test if import works
        test_result = subprocess.run(
            [sys.executable, "-c", "import mcp.server.fastmcp"],
            capture_output=True
        )
        
        if test_result.returncode == 0:
            print(f"  ✓ Strategy {i} succeeded!")
            break
    else:
        print("\n  ✗ All strategies failed!")
        
    # 5. Final verification
    print("\n5. Verifying installation...")
    try:
        import mcp.server.fastmcp
        print("  ✓ mcp.server.fastmcp module imported successfully!")
        
        # Check version
        import mcp
        print(f"  ✓ python-mcp version: {getattr(mcp, '__version__', 'unknown')}")
        
    except ImportError as e:
        print(f"  ✗ Error: Could not import mcp.server.fastmcp: {e}")
        print("\n  Attempting final fallback...")
        
        # Final fallback: manual pip install with specific format
        os.system(f'{sys.executable} -m pip install --no-cache-dir "python-mcp[server]==1.0.1"')
        
        # Test again
        try:
            import mcp.server.fastmcp
            print("  ✓ Final fallback succeeded!")
        except ImportError:
            print("  ✗ Final fallback failed. Manual intervention required.")
            sys.exit(1)
    
    print("\n=== Installation complete! ===")

if __name__ == "__main__":
    install_dependencies()