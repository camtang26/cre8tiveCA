#!/usr/bin/env python3
"""
Installation script for cal_com_mcp_server dependencies on Render
"""
import subprocess
import sys

def install_dependencies():
    """Install all dependencies including python-mcp with server extras"""
    
    print("Installing cal_com_mcp_server dependencies...")
    
    # First, upgrade pip
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Install base requirements
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Explicitly install python-mcp with server extras
    # Using subprocess to ensure proper handling of the bracket notation
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", 
        "--force-reinstall", "--no-deps", "python-mcp[server]==1.0.1"
    ])
    
    # Then install python-mcp dependencies
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "python-mcp[server]==1.0.1"
    ])
    
    print("All dependencies installed successfully!")
    
    # Verify the installation
    try:
        import mcp.server.fastmcp
        print("✓ mcp.server.fastmcp module found successfully!")
    except ImportError as e:
        print(f"✗ Error: Could not import mcp.server.fastmcp: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()