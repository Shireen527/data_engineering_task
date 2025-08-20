CREATE TABLE IF NOT EXISTS raw_sensor_data  (
    id              BIGSERIAL PRIMARY KEY,
    machine_id      INTEGER NOT NULL,
    timestamp       TIMESTAMP NOT NULL,
    temperature     NUMERIC(8,2),
    humidity        NUMERIC(6,2), 
    pressure        NUMERIC(8,2),
    vibration       NUMERIC(8,2),
    energy_consumption NUMERIC(10,2),
    machine_status  INTEGER,
    anomaly_flag    INTEGER,
    predicted_remaining_life NUMERIC(10,2),
    file_source     TEXT NOT NULL,
    ingested_at     TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_machine_time ON raw_sensor_data (machine_id, timestamp);

CREATE TABLE IF NOT EXISTS sensor_aggregates(
    id              BIGSERIAL PRIMARY KEY,
    machine_id      INTEGER NOT NULL,
    window_start    TIMESTAMP NOT NULL,
    window_end      TIMESTAMP NOT NULL,
    metric_name     TEXT NOT NULL,
    min_value       NUMERIC(12,2),
    max_value       NUMERIC(12,2),
    avg_value       NUMERIC(12,2),
    std_dev         NUMERIC(12,2),
    record_count    INTEGER,
    file_source     TEXT NOT NULL,
    processed_at    TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agg_type_time ON sensor_aggregates (machine_id, window_start);
