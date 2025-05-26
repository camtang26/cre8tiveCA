#!/usr/bin/env python3
"""
Troubleshooting script for Render deployment issues
"""
import subprocess
import sys
import os
import platform

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    print("=== Render Deployment Troubleshooting ===\n")
    
    # System info
    print("1. System Information:")
    print(f"   Platform: {platform.platform()}")
    print(f"   Python: {sys.version}")
    print(f"   Working Directory: {os.getcwd()}")
    
    # Check pip version
    print("\n2. Package Manager:")
    stdout, stderr, code = run_command(f"{sys.executable} -m pip --version")
    print(f"   Pip: {stdout.strip()}")
    
    # Check if python-mcp is installed
    print("\n3. Checking python-mcp installation:")
    stdout, stderr, code = run_command(f"{sys.executable} -m pip show python-mcp")
    if code == 0:
        for line in stdout.strip().split('\n'):
            if line.startswith('Version:') or line.startswith('Location:'):
                print(f"   {line}")
    else:
        print("   ✗ python-mcp not installed")
    
    # Try importing mcp.server.fastmcp
    print("\n4. Testing imports:")
    stdout, stderr, code = run_command(f'{sys.executable} -c "import mcp.server.fastmcp; print(\'✓ Import successful\')"')
    if code == 0:
        print(f"   {stdout.strip()}")
    else:
        print(f"   ✗ Import failed: {stderr.strip()}")
    
    # Check for server extras
    print("\n5. Checking server extras:")
    stdout, stderr, code = run_command(f"{sys.executable} -m pip show click pydantic-settings")
    if "click" in stdout and "pydantic-settings" in stdout:
        print("   ✓ Server extras dependencies found")
    else:
        print("   ✗ Server extras dependencies missing")
    
    # Suggest fixes
    print("\n6. Suggested fixes:")
    if code != 0:
        print("   Try running one of these commands:")
        print("   - ./render_build.sh")
        print("   - python render_install.py")
        print("   - pip install --force-reinstall 'python-mcp[server]==1.0.1'")
        print("\n   Or use Docker deployment with the provided Dockerfile")
    else:
        print("   ✓ Everything looks good!")
    
    print("\n=== End of troubleshooting ===")

if __name__ == "__main__":
    main()