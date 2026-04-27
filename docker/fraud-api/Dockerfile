FROM python:3.11-slim

WORKDIR /opt/fraud_detection_mlops

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/fraud_detection_mlops

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8000"]
