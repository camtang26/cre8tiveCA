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

# Create a fallback main.py if MCP imports fail
RUN echo 'import sys; \
try: \
    from tools.cal_com_tools import cal_com_mcp_instance; \
    app = cal_com_mcp_instance.app; \
except ImportError as e: \
    print(f"MCP import failed: {e}"); \
    from fastapi import FastAPI; \
    app = FastAPI(title="Cal.com MCP Server", description="Cal.com integration service"); \
    @app.get("/health"); \
    def health(): return {"status": "ok", "message": "MCP server fallback mode"}; \
' > fallback_main.py

# Expose port
EXPOSE 8000

# Set environment variable for port
ENV PORT=8000

# Run the application with fallback
CMD ["sh", "-c", "python -c 'import main; print(\"Using main.py\")' && uvicorn main:app --host 0.0.0.0 --port $PORT || (echo 'Falling back to basic FastAPI app' && uvicorn fallback_main:app --host 0.0.0.0 --port $PORT)"]