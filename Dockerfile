# Stage 1: The Builder (Compiles dependencies)
FROM python:3.13-slim as builder

WORKDIR /app

# Install build dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y gcc

# Create a virtual environment inside the container
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: The Production Image (Ultra-lean execution)
FROM python:3.13-slim

WORKDIR /app

# Copy the pre-compiled virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the core application code
COPY src/ /app/src/

# Expose the web server port
EXPOSE 8000

# Run the FastAPI server using Uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
