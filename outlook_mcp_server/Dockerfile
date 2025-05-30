FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install all dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || \
    (echo "Fallback: Installing dependencies individually..." && \
     pip install --no-cache-dir fastapi uvicorn httpx pytz python-dotenv pydantic email-validator sse-starlette typer rich)

# Install MCP dependencies with multiple strategies
RUN echo "Attempting to install MCP SDK..." && \
    (pip install --no-cache-dir "mcp[server]" || \
     pip install --no-cache-dir git+https://github.com/modelcontextprotocol/python-sdk.git || \
     pip install --no-cache-dir git+https://github.com/anthropics/mcp-python.git || \
     (echo "Installing individual MCP components..." && \
      pip install --no-cache-dir mcp fastmcp)) && \
    echo "MCP installation completed" || echo "⚠ All MCP installation methods failed"

# Copy application code
COPY . .

# Create an __init__.py to make the directory a proper Python package
RUN touch __init__.py

# Expose port
EXPOSE 8000

# Set environment variable for port
ENV PORT=8000
ENV PYTHONPATH=/app

# Create a startup script that handles imports properly
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Outlook MCP Server..."\n\
echo "Checking MCP dependencies..."\n\
\n\
# Detailed diagnostic\n\
python -c "import sys; print(f\"Python version: {sys.version}\")"\n\
python -c "import pkg_resources; [print(f\"{pkg.key}: {pkg.version}\") for pkg in pkg_resources.working_set if \"mcp\" in pkg.key.lower()]" || echo "No MCP packages found"\n\
\n\
# Check specific imports\n\
if python -c "import mcp; print(\"✓ mcp module available\")" 2>/dev/null; then\n\
    echo "✓ Base mcp module imported successfully"\n\
else\n\
    echo "✗ Base mcp module import failed"\n\
fi\n\
\n\
if python -c "from mcp.server.fastmcp import FastMCP; print(\"✓ FastMCP available\")" 2>/dev/null; then\n\
    echo "✓ FastMCP imported successfully"\n\
else\n\
    echo "✗ FastMCP import failed"\n\
fi\n\
\n\
# Try to run the main application\n\
if python -c "import sys; sys.path.insert(0, \"/app\"); from tools.outlook_tools import outlook_mcp_instance; print(\"✓ Main app imports successful\")" 2>/dev/null; then\n\
    echo "✓ MCP imports successful, starting main application"\n\
    exec uvicorn main:app --host 0.0.0.0 --port $PORT\n\
else\n\
    echo "⚠ MCP imports failed, starting fallback application"\n\
    exec uvicorn fallback_main:app --host 0.0.0.0 --port $PORT\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]