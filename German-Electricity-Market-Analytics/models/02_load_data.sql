-- ============================================================
-- 02_load_data.sql
-- Run this AFTER uploading the 3 CSVs to the ENERGY_STAGE stage
-- ============================================================

USE DATABASE GERMAN_ENERGY;
USE SCHEMA RAW;

COPY INTO RAW_GENERATION
  FROM @ENERGY_STAGE/smard_generation_hour.csv
  FILE_FORMAT = CSV_STANDARD
  ON_ERROR = 'CONTINUE';   -- skip bad rows instead of failing the whole load,
                            -- but Snowflake logs exactly which rows and why

COPY INTO RAW_CONSUMPTION
  FROM @ENERGY_STAGE/smard_consumption_hour.csv
  FILE_FORMAT = CSV_STANDARD
  ON_ERROR = 'CONTINUE';

COPY INTO RAW_PRICE
  FROM @ENERGY_STAGE/smard_price_hour.csv
  FILE_FORMAT = CSV_STANDARD
  ON_ERROR = 'CONTINUE';

-- Quick sanity check after loading -- always verify row counts
-- match what you saw in the CSVs before moving on.
SELECT 'RAW_GENERATION' AS table_name, COUNT(*) AS row_count FROM RAW_GENERATION
UNION ALL
SELECT 'RAW_CONSUMPTION', COUNT(*) FROM RAW_CONSUMPTION
UNION ALL
SELECT 'RAW_PRICE', COUNT(*) FROM RAW_PRICE;
