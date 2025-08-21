FROM python:3.13.7-slim-bookworm

# Copy uv binary from the official image for fast, reliable dependency installation
COPY --from=ghcr.io/astral-sh/uv:0.8.12 /uv /uvx /bin/

WORKDIR /app

# Copy the application code
COPY . /app/

# Install dependencies with vertexai extra for Vertex AI support
# Also install uvicorn which is needed to run the FastAPI application
RUN uv sync --frozen --all-extras

# Set Python path to use the virtual environment created by uv
ENV PATH="/app/.venv/bin:$PATH"

# Expose the default FastAPI port
EXPOSE 8000

# Run the application using the __main__ module
ENTRYPOINT ["python", "-m", "fastapi_agentrouter"]
