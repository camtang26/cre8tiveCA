FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install dependencies in stages to handle python-mcp[server]
# First, install all dependencies except python-mcp
RUN grep -v "python-mcp" requirements.txt > requirements-base.txt || true && \
    if [ -s requirements-base.txt ]; then pip install --no-cache-dir -r requirements-base.txt; fi && \
    rm -f requirements-base.txt

# Install python-mcp with server extras using multiple strategies
RUN pip install --no-cache-dir python-mcp==1.0.1 && \
    pip install --no-cache-dir "python-mcp[server]==1.0.1" || \
    (pip install --no-cache-dir click pydantic-settings && \
     pip install --no-cache-dir --force-reinstall "python-mcp[server]==1.0.1")

# Copy application code
COPY . .

# Verify installation
RUN python -c "import mcp.server.fastmcp; print('✓ mcp.server.fastmcp imported successfully!')"

# Expose port
EXPOSE 8000

# Set environment variable for port
ENV PORT=8000

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]