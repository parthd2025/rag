FROM python:3.11-slim

# Install system deps required by some packages (faiss, numpy, sentence-transformers)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        ca-certificates \
        libopenblas-dev \
        libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements-dev.txt /app/requirements-dev.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements-dev.txt

# Copy project
COPY . /app

# Expose port for optional API
EXPOSE 8000

# Default entry: run a small smoke test to verify environment
CMD ["python", "test_full_flow.py"]
