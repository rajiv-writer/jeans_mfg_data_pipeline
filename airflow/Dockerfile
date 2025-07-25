# Dockerfile for airflow_scheduler and airflow_webserver
FROM apache/airflow:2.8.1-python3.10

# Install build dependencies for psycopg2 and other potential C extensions
# Use apt-get for Debian/Ubuntu based images (which Airflow's official images usually are)
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt