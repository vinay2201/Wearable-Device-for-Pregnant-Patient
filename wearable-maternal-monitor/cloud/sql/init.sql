CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(64) PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  ts DATETIME NOT NULL,
  hr DOUBLE,         -- heart rate
  spo2 DOUBLE,       -- oxygen saturation
  temp DOUBLE,       -- body temperature (C)
  env_temp DOUBLE,   -- ambient temp
  motion DOUBLE,     -- accelerometer magnitude
  idx_cluster INT NULL,
  INDEX(user_id, ts)
);

CREATE TABLE IF NOT EXISTS alerts (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  ts DATETIME NOT NULL,
  type VARCHAR(32) NOT NULL,     -- 'zscore' | 'cluster' | 'combined'
  detail JSON,
  INDEX(user_id, ts)
);
