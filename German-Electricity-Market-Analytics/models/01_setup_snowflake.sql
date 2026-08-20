
-- ============================================================
-- 01_setup_snowflake.sql
-- Sets up the RAW landing zone for the German Energy Market project
-- ============================================================
 
-- A warehouse is Snowflake's compute engine (separate from storage).
-- X-Small is the cheapest tier and plenty for a portfolio project.
-- AUTO_SUSPEND = 60 means it shuts off after 60s idle.
CREATE WAREHOUSE IF NOT EXISTS ENERGY_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;
 
-- One database for the whole project.
CREATE DATABASE IF NOT EXISTS GERMAN_ENERGY;
 
USE DATABASE GERMAN_ENERGY;
 
-- RAW schema:
CREATE SCHEMA IF NOT EXISTS RAW;
 
USE SCHEMA RAW;
 
CREATE OR REPLACE TABLE RAW_GENERATION (
    timestamp_utc       TIMESTAMP_NTZ,
    wind_onshore_mw     FLOAT,
    photovoltaik_mw     FLOAT,
    erdgas_mw           FLOAT,
    kernenergie_mw      FLOAT,
    steinkohle_mw       FLOAT,
    braunkohle_mw       FLOAT,
    biomasse_mw         FLOAT,
    wasserkraft_mw      FLOAT
);
 
CREATE OR REPLACE TABLE RAW_CONSUMPTION (
    timestamp_utc       TIMESTAMP_NTZ,
    netzlast_mw         FLOAT
);
 
CREATE OR REPLACE TABLE RAW_PRICE (
    timestamp_utc              TIMESTAMP_NTZ,
    day_ahead_price_eur_mwh    FLOAT
);
 
-- A file format tells Snowflake how to parse the CSVs on load:
-- skip the header row, comma-delimited, treat empty strings as NULL.
CREATE OR REPLACE FILE FORMAT CSV_STANDARD
    TYPE = 'CSV'
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('', 'NULL', 'null');
 
-- An interGERMAN_ENERGY.RAW.RAW_CONSUMPTIONnal stage is a private storage area inside Snowflake
-- where you upload files before COPY INTO loads them into a table.
CREATE OR REPLACE STAGE ENERGY_STAGE
    FILE_FORMAT = CSV_STANDARD;
