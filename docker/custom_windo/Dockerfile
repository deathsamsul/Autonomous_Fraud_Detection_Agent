FROM python:3.11-slim

WORKDIR /opt/dashboard

ENV PYTHONPATH=/opt/dashboard
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/dashboard/requirements.txt

RUN pip install --upgrade pip \
    && pip install -r /opt/dashboard/requirements.txt

COPY app /opt/dashboard/app

EXPOSE 8501

CMD ["streamlit", "run", "app/monitoring/monitoring_dashbord.py", "--server.address=0.0.0.0", "--server.port=8501"]

# docker build -t deathsamsul/custom_dashboard:1.0 -f docker/custom_windo/Dockerfile .