#!/bin/bash
# Build script for outlook_mcp_server on Render

echo "Installing dependencies for outlook_mcp_server..."

# First install the requirements without the extras
pip install --no-cache-dir -r requirements.txt

# Then explicitly install python-mcp with server extras
pip install --no-cache-dir "python-mcp[server]==1.0.1"

echo "Build complete!"