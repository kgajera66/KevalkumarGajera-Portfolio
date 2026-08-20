# German Electricity Market Analytics

An end-to-end data pipeline analyzing Germany's electricity generation, consumption,
and day-ahead pricing — built on real public data from SMARD.de (Bundesnetzagentur),
with a natural-language query agent on top.

## Why this project

Germany's energy transition (Energiewende) is producing genuinely interesting,
messy, real-world data: renewable generation swings hour to hour with weather,
and the day-ahead market occasionally goes negative when supply outpaces demand.
This project pulls that data end to end — from a public, undocumented government
API through to a governed LLM-powered query layer — to explore the relationship
between renewable generation and electricity prices.

## Architecture

```
SMARD.de API  -->  Python extraction  -->  Snowflake (raw)  -->  dbt (staging -> intermediate -> marts)  -->  Power BI
                                                                        |
                                                                        v
                                                          Claude API (LLM-to-SQL agent)
```
<img width="1860" height="873" alt="image" src="https://github.com/user-attachments/assets/a8aa91df-1839-4e6a-ac47-d4cfbba80141" />

## Tech stack

- **Extraction:** Python (requests, pandas)
- **Warehouse:** Snowflake
- **Transformation:** dbt (staging / intermediate / marts layers, with schema tests)
- **Visualization:** Power BI
- **AI layer:** Claude API — natural language to SQL, scoped to the marts layer only

## Key findings

- Electricity prices show a clear inverse relationship with renewable generation
  share (the "merit order effect") — hours/days with higher wind and solar output
  see meaningfully lower average day-ahead prices.
- Price volatility peaks during evening demand ramp hours (roughly 17:00–20:00).
- Germany's day-ahead market goes negative during a non-trivial number of hours —
  typically high-renewable, low-demand periods where generators effectively pay
  the grid to take excess supply.

<img width="1426" height="801" alt="image" src="https://github.com/user-attachments/assets/7ff7cfa4-1622-4cbe-a7a4-637d6a9e42a3" />

## Data modeling approach

Follows a standard layered dbt architecture:

- **staging/** — one model per raw source, renamed/typed/timezone-converted, no
  business logic or joins.
- **intermediate/** — a single join of generation, consumption, and price data
  into one hourly table, so that logic exists in exactly one place.
- **marts/** — three tables shaped around specific business questions:
  `daily_energy_mix` (daily trend), `price_by_hour_of_day` (intraday pattern),
  `negative_price_events` (specific anomaly instances).

All models are tested for null/uniqueness constraints on their primary grain.

## LLM-to-SQL agent

`scripts/ask_energy_data.py` lets you ask questions in plain English
(e.g. *"What was the average renewable share in December 2024?"*). Claude
generates a SQL query scoped only to the three mart tables (not the full
warehouse — a deliberate least-privilege design choice), which is then
executed against Snowflake, with a hard guardrail that blocks any
non-SELECT statement before it can run.

Example:

```
Question: What was the average renewable share in December 2024?

Generated SQL:
SELECT AVG(renewable_share) AS avg_renewable_share
FROM GERMAN_ENERGY.DBT_MARTS.daily_energy_mix
WHERE report_date >= '2024-12-01' AND report_date < '2025-01-01';

Result:
AVG_RENEWABLE_SHARE
0.5229731341196451
```

## Data source

[SMARD.de](https://www.smard.de) — Strommarktdaten, published by the
Bundesnetzagentur (German Federal Network Agency). Public, free, no API key
required.

## Setup

```bash
pip install -r requirements.txt
python scripts/extract_smard.py
# then run 01_setup_snowflake.sql and 02_load_data.sql in Snowsight
dbt run
dbt test
python scripts/ask_energy_data.py
```

Requires Snowflake and Anthropic API credentials set as environment variables
(see script comments — never hardcoded).

