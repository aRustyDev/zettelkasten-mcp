FROM python:3.12-slim as app

SHELL ["/bin/bash", "-c"]

# Build arguments
ARG ZETTELKASTEN_LOG_LEVEL=INFO

# Environment variables for storage paths
ENV ZETTELKASTEN_NOTES_DIR=/var/data/notes
ENV ZETTELKASTEN_DATABASE_DIR=/var/data/db
ENV ZETTELKASTEN_DATABASE_PATH=$ZETTELKASTEN_DATABASE_DIR/zettelkasten.db

# HTTP transport configuration
ENV ZETTELKASTEN_HTTP_HOST=0.0.0.0
ENV ZETTELKASTEN_HTTP_PORT=8000
ENV ZETTELKASTEN_HTTP_CORS=false
ENV ZETTELKASTEN_HTTP_CORS_ORIGINS=*
ENV ZETTELKASTEN_JSON_RESPONSE=true

# Logging
ENV ZETTELKASTEN_LOG_LEVEL=${ZETTELKASTEN_LOG_LEVEL}

# Define volumes for persistent data
VOLUME ["${ZETTELKASTEN_NOTES_DIR}", "${ZETTELKASTEN_DATABASE_DIR}"]

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git=1:2.47.* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install --no-cache-dir uv==0.5.15

# Set working directory
WORKDIR /app

# Copy project files from local build context
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Create virtual environment and install dependencies
RUN uv venv && \
    source .venv/bin/activate && \
    uv sync --no-dev

# Create data directories
RUN mkdir -p ${ZETTELKASTEN_NOTES_DIR} ${ZETTELKASTEN_DATABASE_DIR}

# Expose HTTP port
EXPOSE $ZETTELKASTEN_HTTP_PORT

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run the server with HTTP transport
ENTRYPOINT ["/app/.venv/bin/python", "-m", "zettelkasten_mcp.main"]
CMD ["--transport", "http"]
