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

# Now we can import our app
if __name__ == "__main__":
    # Import uvicorn and run the app directly
    import uvicorn
    
    # Import the FastAPI app
    from main import app
    
    # Get port from environment
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    print(f"Starting Bridge Server on port {port}...")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {current_dir}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)