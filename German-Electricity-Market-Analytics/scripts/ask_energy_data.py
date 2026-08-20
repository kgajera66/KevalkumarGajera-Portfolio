"""
ask_energy_data.py
--------------------
A small "ask your data" tool: type a question in plain English about the
German energy market, and it:
  1. Sends your question + a description of the mart tables to Claude
  2. Claude generates a SQL query against those tables
  3. The script runs that SQL against Snowflake
  4. Prints the result back to you

WHY this counts as "agentic": the LLM isn't just chatting -- it is
choosing which table and columns to use, writing a real SQL query, and
that query gets EXECUTED against a live system with a real result coming
back. That loop (reason -> act -> observe result) is the core pattern
behind agentic AI systems, just at the smallest possible scale. You can
say this explicitly in an interview -- this is a minimal but genuine
example of the pattern, not the marketing-buzzword version.

WHY we don't just let the LLM query the RAW schema: giving an LLM broad,
ungoverned access to a warehouse is a real production risk (it could
generate an expensive full-table scan, or a query against a table you
didn't intend to expose). We deliberately scope it to only the 3 mart
tables and give it their exact column definitions -- this is the same
principle as least-privilege access control applied to an AI agent, and
it's worth mentioning as a design decision, not an accident.
"""

import os
import re
import snowflake.connector
import anthropic

# ============================================================
# 1. CONFIG -- fill in your own values or set as environment variables
# ============================================================

SNOWFLAKE_CONFIG = {
    "account": os.environ.get("SNOWFLAKE_ACCOUNT", "<your_account_locator>"),
    "user": os.environ.get("SNOWFLAKE_USER", "<your_username>"),
    "password": os.environ.get("SNOWFLAKE_PASSWORD", "<your_password>"),
    "warehouse": "ENERGY_WH",
    "database": "GERMAN_ENERGY",
    "schema": "DBT_STAGING", 
}

# Never hardcode this -- set it as an environment variable instead:
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# This schema description IS the "least privilege" boundary --
# the LLM literally cannot reference a table or column it doesn't
# know exists, because we control exactly what we tell it about.
SCHEMA_DESCRIPTION = """
You have access to these Snowflake tables in GERMAN_ENERGY.DBT_STAGING:

TABLE: daily_energy_mix (one row per calendar day)
  - report_date DATE
  - avg_wind_onshore_mw, avg_photovoltaik_mw, avg_erdgas_mw,
    avg_kernenergie_mw, avg_steinkohle_mw, avg_braunkohle_mw,
    avg_biomasse_mw, avg_wasserkraft_mw  FLOAT (avg MW generated that day)
  - avg_total_generation_mw, avg_total_load_mw, avg_residual_load_mw FLOAT
  - renewable_share FLOAT (0 to 1, share of generation from renewables)
  - avg_price_eur_mwh, min_price_eur_mwh, max_price_eur_mwh FLOAT
  - negative_price_hours INT (count of hours that day with negative price)

TABLE: price_by_hour_of_day (one row per hour 0-23, averaged across all days)
  - hour_of_day INT (0-23)
  - avg_price_eur_mwh, price_stddev FLOAT
  - avg_renewable_share FLOAT
  - avg_load_mw FLOAT
  - negative_price_hour_count INT

TABLE: negative_price_events (one row per hour where price went negative)
  - timestamp_local TIMESTAMP
  - day_ahead_price_eur_mwh FLOAT (always negative in this table)
  - total_load_mw, total_generation_mw, renewable_share, residual_load_mw FLOAT
"""


def generate_sql(question: str) -> str:
    """Ask Claude to turn a plain-English question into a SQL query."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    system_prompt = f"""You are a SQL generator for a Snowflake database about
the German electricity market. {SCHEMA_DESCRIPTION}

Rules:
- Output ONLY the SQL query, no explanation, no markdown code fences.
- Only SELECT statements -- never generate INSERT, UPDATE, DELETE, or DDL.
- Use only the tables and columns listed above.
- Always add a LIMIT if the question doesn't imply an aggregate result."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": question}],
    )

    sql = response.content[0].text.strip()
    # Strip markdown fences if the model adds them anyway -- LLMs are not
    # 100% reliable at following formatting instructions, so I defensively
    # clean the output rather than trusting it blindly.
    sql = re.sub(r"^```sql\s*|\s*```$", "", sql, flags=re.MULTILINE).strip()
    return sql


def is_safe_select(sql: str) -> bool:
    """A basic guardrail: only allow SELECT statements through to Snowflake."""
    normalized = sql.strip().lower()
    forbidden = ["insert", "update", "delete", "drop", "alter", "create", "truncate", "merge"]
    return normalized.startswith("select") and not any(word in normalized for word in forbidden)


def run_query(sql: str):
    """Execute the generated SQL against Snowflake and return results."""
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return columns, rows
    finally:
        conn.close()


def ask(question: str):
    print(f"\nQuestion: {question}")

    sql = generate_sql(question)
    print(f"\nGenerated SQL:\n{sql}")

    if not is_safe_select(sql):
        print("\n[BLOCKED] Generated query was not a safe SELECT statement. Not executing.")
        return

    columns, rows = run_query(sql)

    print(f"\nResult:")
    print(" | ".join(columns))
    for row in rows[:20]:  # cap printed rows for readability
        print(" | ".join(str(v) for v in row))


if __name__ == "__main__":
    # A few example questions to try.
    example_questions = [
        "What was the average renewable share in December 2024?",
        "Which 5 days had the highest renewable share?",
        "What hour of the day has the most volatile electricity prices?",
        "How many hours had negative prices in total?",
    ]

    for q in example_questions:
        ask(q)

