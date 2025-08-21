# IOT Sensor Data Pipeline Documentation

## Table of Contents

- [Dataset](#dataset)
- [Techstack](#techstack)
- [Overall Flow](#overall-flow)
- [Architecture](#architecture)
- [Scalability Considerations](#scalability-considerations)

## Dataset-

The dataset contains IoT sensor readings from manufacturing machines, covering sensor readings such as temperature, vibration, humidity, pressure, and energy consumption. It contains 100,000 records from 50 unique machines.

https://www.kaggle.com/datasets/ziya07/smart-manufacturing-iot-cloud-monitoring-dataset/data

## Techstack -

- PostgreSQL v17 (or v15+)
- Python v3.12

## Overall Flow

- Files arrive in the data folder.
- The file watcher detects new CSVs and triggers processing.
- The validator cleans and quarantines bad rows.
- The transformer computes aggregates per source(machine_id) per file.
- The database layer bulk-inserts raw and aggregate data into Postgres.
- Logs and quarantined rows are written to local folders for audit and troubleshooting.

## Architecture

### Components

**1. File watcher (orchestrator):**

- Watches the data folder for new .csv files.
- For each new file:
  - Runs validation.
  - Runs transformation/aggregation.
  - Writes results to the database.
  - Runs continuously with a configurable monitoring interval.

**2. Data validator:**

- Loads the CSV and parses types (timestamp, numerics).
- Ensures required columns exist (machine_id, timestamp, temperature, humidity, pressure, vibration, energy_consumption).
- Drops rows with nulls in required fields.
- Drops duplicates by (machine_id, timestamp).
- Performs range checks for sensor readings.
- Coerces anomaly_flag (default 0) and machine_status (default -1) if missing/invalid.

Outputs:

- valid_df: rows that passed all checks.
- quarantine file: invalid rows saved to the quarantine folder, with counts logged.

**3.Data transformer and aggregator:**

- Adds meta-data -> file_source.
- For each metric:
  - Groups by reading source (machine_id) and computes: min, max, avg, std_dev, record_count.
  - Uses the file’s min/max timestamp as window_start/window_end (per-file window).

Outputs:

- Transformed raw rows (with file_source).
- Aggregated rows for each metric and machine.

**4. Database manager:**

- Handles connection to the database with retries (atmost 3 times) and exponential backoff.
- Health checks to ensure db connectivity.
- Bulk inserts using execute_values.

Tables:

- raw_sensor_data:

  - Raw validated records with file_source and ingested_at.
  - Composite index on (machine_id, timestamp).

- sensor_aggregates:
  - Per-file window aggregates with metric_name and stats.
  - Index on (machine_id, window_start).

**5.Data splitting utility:**

- Splits a large CSV into time-based files.
- Introduces controlled missing values for testing validation.
- Writes chunked files into the data folder.

## Scalability Considerations:

The solution currently works with a single folder, however, it can be designed to handle millions of files per day.

- Instead of storing files locally, an object store like AWS S3 can be used. Each incoming file can trigger an event with metadata (path, size), which makes it easier to track and process files.

**To scale horizontally,**

- multiple instances of validators and transformers can share work from a queue, so the workload is distributed.
- Serverless functions (Lambda or Cloud Functions) could also process files in parallel.

- Using event queues like Kafka, Google Pub/Sub, or AWS Kinesis to allow multiple workers to run at the same time that could handle bottlenecks.

- Would also include stateless validation workers with idempotency to prevent duplicate entries in the database if the same file is reprocessed.

**For high-volume ingestion,**

- Would prefer larger and fewer batch size than the current version.
- Also storing analytics-ready data in compressed Parquet format would improve query performance.
