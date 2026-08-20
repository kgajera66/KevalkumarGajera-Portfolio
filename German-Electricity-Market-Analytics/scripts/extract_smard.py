
"""
SMARD.de Electricity Market Data Extractor
--------------------------------------------
Downloads German electricity generation, consumption, and price data
from the Bundesnetzagentur's SMARD platform and saves it as clean CSVs
ready to load into Snowflake.

Why this design:
- SMARD splits data into weekly/monthly JSON "chunks" identified by a
  millisecond timestamp. I first fetch the INDEX (list of available
  chunk timestamps), then fetch each chunk's actual data.
- I separate generation / consumption / price into their own files
  (mirrors how you'll model them as separate staging tables in dbt).
- Timestamps come back as Unix milliseconds in UTC — I convert to
  proper datetime early, because getting timezone handling right BEFORE
  loading into the warehouse saves painful debugging later (Germany
  has DST switches, which is a classic gotcha in energy data).
"""

import requests
import pandas as pd
import time
from datetime import datetime

BASE_URL = "https://www.smard.de/app/chart_data"

FILTERS = {
    "generation": {
        4067: "wind_onshore_mw",
        4068: "photovoltaik_mw",
        4071: "erdgas_mw",
        1224: "kernenergie_mw",  
        4069: "steinkohle_mw",
        1223: "braunkohle_mw",
        4066: "biomasse_mw",
        1226: "wasserkraft_mw",
    },
    "consumption": {
        410: "netzlast_mw",       # total grid load
    },
    "price": {
        4169: "day_ahead_price_eur_mwh",   # Germany/Luxembourg bidding zone
    },
}

REGION = "DE"          
RESOLUTION = "hour"     # hour | quarterhour | day | week | month | year


def get_available_timestamps(filter_id: int, region: str, resolution: str) -> list[int]:
    """Ask SMARD which data chunks exist for this filter/region/resolution."""
    url = f"{BASE_URL}/{filter_id}/{region}/index_{resolution}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()["timestamps"]


def get_series(filter_id: int, region: str, resolution: str, chunk_ts: int) -> pd.DataFrame:
    """Fetch one chunk of time-series data and return it as a DataFrame."""
    url = f"{BASE_URL}/{filter_id}/{region}/{filter_id}_{region}_{resolution}_{chunk_ts}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    series = resp.json()["series"]  # list of [timestamp_ms, value]
    df = pd.DataFrame(series, columns=["timestamp_ms", "value"])
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_ms"], unit="ms", utc=True)
    return df[["timestamp_utc", "value"]]


def fetch_filter(filter_id: int, region: str, resolution: str,
                  date_from: datetime, date_to: datetime) -> pd.DataFrame:
    """Fetch all chunks for one filter within a date range and stitch them together."""
    all_ts = get_available_timestamps(filter_id, region, resolution)

    # Only pull the chunks that fall inside our target date range
    relevant_ts = [
        ts for ts in all_ts
        if date_from <= datetime.utcfromtimestamp(ts / 1000) <= date_to
    ]

    frames = []
    for ts in relevant_ts:
        try:
            frames.append(get_series(filter_id, region, resolution, ts))
        except requests.HTTPError as e:
            print(f"  [skip] chunk {ts} for filter {filter_id}: {e}")
        time.sleep(0.3)  # be polite to a free public API

    if not frames:
        return pd.DataFrame(columns=["timestamp_utc", "value"])

    return pd.concat(frames, ignore_index=True).drop_duplicates(subset="timestamp_utc")


def build_dataset(category: str, filter_map: dict[int, str],
                   date_from: datetime, date_to: datetime) -> pd.DataFrame:
    """Fetch every filter in a category and merge them into one wide table
    (one row per timestamp, one column per metric) — this is the shape
    that's easiest to load and model in dbt later."""
    merged = None
    for filter_id, col_name in filter_map.items():
        print(f"Fetching {category}: {col_name} (filter {filter_id})...")
        df = fetch_filter(filter_id, REGION, RESOLUTION, date_from, date_to)
        df = df.rename(columns={"value": col_name})
        merged = df if merged is None else merged.merge(df, on="timestamp_utc", how="outer")
    return merged.sort_values("timestamp_utc") if merged is not None else pd.DataFrame()


if __name__ == "__main__":
    DATE_FROM = datetime(2024, 1, 1)
    DATE_TO = datetime(2025, 12, 31)

    for category, filter_map in FILTERS.items():
        df = build_dataset(category, filter_map, DATE_FROM, DATE_TO)
        out_path = f"smard_{category}_{RESOLUTION}.csv"
        df.to_csv(out_path, index=False)
        print(f"Saved {len(df)} rows -> {out_path}\n")
