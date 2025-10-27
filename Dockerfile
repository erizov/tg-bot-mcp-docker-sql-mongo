FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY notes-mcp-sqlite/setup/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies for CI
RUN pip install --no-cache-dir pymongo neo4j requests flake8 fastapi uvicorn pytest httpx

# Copy application code
COPY . /app

# Expose port for FastAPI monitor
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["python", "-m", "notes-mcp-sqlite.bot"]
