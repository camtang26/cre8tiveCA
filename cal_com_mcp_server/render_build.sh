#!/bin/bash
set -e

echo "Starting Render build for cal_com_mcp_server..."

# Upgrade pip first
echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Create a temporary requirements file without python-mcp
echo "Creating temporary requirements file..."
grep -v "python-mcp" requirements.txt > requirements-temp.txt || true

# Install all other dependencies first
echo "Installing base dependencies..."
if [ -s requirements-temp.txt ]; then
    pip install --no-cache-dir -r requirements-temp.txt
fi

# Install python-mcp base package first
echo "Installing python-mcp base package..."
pip install --no-cache-dir --no-deps python-mcp==1.0.1

# Install python-mcp dependencies
echo "Installing python-mcp dependencies..."
pip install --no-cache-dir python-mcp==1.0.1

# Finally install with server extras
echo "Installing python-mcp with server extras..."
pip install --no-cache-dir --force-reinstall "python-mcp[server]==1.0.1"

# Clean up
rm -f requirements-temp.txt

# Verify installation
echo "Verifying installation..."
python -c "import mcp.server.fastmcp; print('✓ mcp.server.fastmcp module imported successfully!')" || {
    echo "✗ Failed to import mcp.server.fastmcp"
    echo "Attempting alternative installation method..."
    pip install --no-cache-dir click pydantic-settings
    pip install --no-cache-dir --force-reinstall "python-mcp[server]==1.0.1"
}

echo "Build complete!"