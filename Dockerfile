# -------------------------
# BASE IMAGE
# -------------------------
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Make sure uv is in PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy project metadata (pyproject.toml + uv.lock)
COPY pyproject.toml uv.lock ./

# Install Python dependencies (creates .venv in /app)
RUN uv sync --frozen --no-dev

# Copy the full application code
COPY . .

# Expose port
EXPOSE 8000

# Use uv to run the command (ensures proper venv activation)
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]