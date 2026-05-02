# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (better caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Create mount point (optional but good practice)
RUN mkdir -p /opt/datasets

# Default env (can be overridden in Docker/K8s)
ENV DATA_DIR=/opt/datasets

# Run script
CMD ["python", "store_train_data.py"]