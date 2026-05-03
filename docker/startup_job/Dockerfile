FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PYTHONPATH=/app
ENV DATA_DIR=/opt/datasets
ENV TEMP_DIR=/tmp/temp_data

CMD ["python", "--version"]

# docker build -f docker/startup_job/Dockerfile -t deathsamsul/startup_job:1.0 .