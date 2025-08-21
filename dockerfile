FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

RUN mkdir -p /app/src /app/data /app/quarantine /app/logs /app/archive

COPY src /app/src

COPY data_splitter.py /app/data_splitter.py

COPY schema.sql /app/schema.sql

CMD ["python", "-m", "src.file_watcher"]