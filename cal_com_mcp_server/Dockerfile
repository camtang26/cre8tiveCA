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

# Install MCP dependencies directly from source if needed
RUN pip install --no-cache-dir git+https://github.com/modelcontextprotocol/python-sdk.git || \
    echo "⚠ MCP SDK installation failed, continuing with basic FastAPI setup..."

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
\n\
# Try to run the main application\n\
if python -c "import sys; sys.path.insert(0, \"/app\"); from tools.cal_com_tools import cal_com_mcp_instance" 2>/dev/null; then\n\
    echo "✓ MCP imports successful, starting main application"\n\
    exec uvicorn main:app --host 0.0.0.0 --port $PORT\n\
else\n\
    echo "⚠ MCP imports failed, starting fallback application"\n\
    exec uvicorn fallback_main:app --host 0.0.0.0 --port $PORT\n\
fi\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]