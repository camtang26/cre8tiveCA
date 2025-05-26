#!/usr/bin/env python3
"""
Robust startup script for bridge server on Render
Handles import path issues
"""
import sys
import os

# Ensure the bridge_server directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add both paths to handle different scenarios
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Debug MCP installation
print("Checking MCP installation...")
try:
    import mcp
    print(f"✓ MCP module found at: {mcp.__file__}")
except ImportError as e:
    print(f"✗ MCP module not found: {e}")
    print("Installed packages:")
    import pkg_resources
    for pkg in pkg_resources.working_set:
        if 'mcp' in pkg.key.lower():
            print(f"  - {pkg.key}: {pkg.version}")

# Now we can import our app
if __name__ == "__main__":
    # Import uvicorn and run the app directly
    import uvicorn
    
    try:
        # Import the FastAPI app
        from main import app
        
        # Get port from environment
        port = int(os.environ.get("PORT", 8000))
        
        # Run the server
        print(f"Starting Bridge Server on port {port}...")
        print(f"Python path: {sys.path}")
        print(f"Current directory: {current_dir}")
        
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ImportError as e:
        print(f"Failed to import app: {e}")
        print("Creating fallback app...")
        
        # Create a minimal fallback app
        from fastapi import FastAPI
        
        fallback_app = FastAPI(title="Bridge Server (Fallback Mode)")
        
        @fallback_app.get("/")
        def root():
            return {
                "status": "running", 
                "mode": "fallback",
                "error": "MCP dependencies not available",
                "message": "Bridge server running without MCP functionality"
            }
        
        @fallback_app.get("/health")
        def health():
            return {"status": "degraded", "service": "bridge_server", "mode": "fallback"}
        
        port = int(os.environ.get("PORT", 8000))
        print(f"Starting fallback Bridge Server on port {port}...")
        uvicorn.run(fallback_app, host="0.0.0.0", port=port)