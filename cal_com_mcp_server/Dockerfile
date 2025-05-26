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
echo "Starting Cal.com MCP Server..."\n\
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
# Try to run the main application with detailed error reporting\n\
echo "Testing main application imports..."\n\
if python -c "import sys; sys.path.insert(0, \"/app\"); from tools.cal_com_tools import cal_com_mcp_instance; print(\"✓ Main app imports successful\")" 2>&1; then\n\
    echo "✓ MCP imports successful, starting main application"\n\
    exec uvicorn main:app --host 0.0.0.0 --port $PORT\n\
else\n\
    echo "⚠ Main app imports failed, checking individual components..."\n\
    python -c "import sys; sys.path.insert(0, \"/app\"); from mcp.types import TextContent; print(\"✓ mcp.types import OK\")" 2>&1 || echo "✗ mcp.types import failed"\n\
    python -c "import sys; sys.path.insert(0, \"/app\"); from core.config import DEFAULT_EVENT_TYPE_ID; print(\"✓ core.config import OK\")" 2>&1 || echo "✗ core.config import failed"\n\
    python -c "import sys; sys.path.insert(0, \"/app\"); from core.cal_api_utils import convert_to_utc; print(\"✓ core.cal_api_utils import OK\")" 2>&1 || echo "✗ core.cal_api_utils import failed"\n\
    python -c "import sys; sys.path.insert(0, \"/app\"); from schemas.cal_com_schemas import CreateCalComBookingInput; print(\"✓ schemas import OK\")" 2>&1 || echo "✗ schemas import failed"\n\
    echo "Starting fallback application due to import failures"\n\
    exec uvicorn fallback_main:app --host 0.0.0.0 --port $PORT\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]