## Table of Contents

- [Run with Docker](#run-with-docker)
- [Setup and Run Locally](#setup-and-run-locally)

## Run with Docker

### Prerequisites

Docker Desktop installed and running.

### Steps:

1.  Clone the repo.
    From the project folder start services:
    `docker compose up --build`

2.  Copy the provided files from test_files/ folder into the data/ folder (both folders present in project root).

    The watcher will detect and process them automatically.

### To follow logs:

`docker compose logs -f pipeline`

### To View results in Postgres

Show first 10 raw rows:

```
docker compose exec postgres psql -U postgres -d sensor_pipeline -c "SELECT \* FROM raw_sensor_data ORDER BY ingested_at DESC LIMIT 10;"
```

Show first 10 aggregates:

`docker compose exec postgres psql -U postgres -d sensor_pipeline -c "SELECT \* FROM sensor_aggregates ORDER BY processed_at DESC LIMIT 10;"`

### Optional: generate more files

`docker compose run --rm pipeline python /app/data_splitter.py`

## Setup and Run Locally

### Prerequisites

- PostgreSQL v17 (or v15+)
- Python v3.12

### Setup and run steps:

1. Clone the repo

   ```
   git clone https://github.com/Shireen527 data_engineering_task.git

   cd <repo-folder>
   ```

2. Create and activate a virtual environment, install dependencies
   `pip install -r requirements.txt`

3. Create a database user if needed (default below assumes postgres).

   Create the database:
   `psql -U postgres -c "CREATE DATABASE sensor_pipeline;"`

   Run the schema:
   `psql -U postgres -d sensors -f schema.sql`

4. Configure environment variables

   Create a `.env` file in the project root (or set env vars in your shell):

   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=sensors
   DB_USER=postgres
   DB_PASSWORD=postgres
   ```

5. To split dataset: `python -m src.data_splitter`

   (Split size an be changed in src/config.py via SPLIT_MINUTES.)

6. Run the file watcher to start the pipeline
   :`python -m src.file_watcher`
