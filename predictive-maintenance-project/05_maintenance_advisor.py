"""
05_maintenance_advisor.py
--------------------
Takes a flagged machine (predicted at-risk) and asks Claude to explain,
in plain language, why it was flagged and what a technician should
check first -- grounded in the machine's actual sensor readings and the
model's feature importances, not generic advice.
"""

import os
import pandas as pd
import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# Reference values -- computed earlier from the healthy-machine population..
HEALTHY_AVERAGES = {
    "Torque [Nm]": 39.63,
    "Tool wear [min]": 106.69,
    "Rotational speed [rpm]": 1540.26,
    "Air temperature [K]": 299.97,
    "Process temperature [K]": 309.99,
}

FEATURE_IMPORTANCE = {
    "Torque [Nm]": 0.34,
    "Rotational speed [rpm]": 0.29,
    "Tool wear [min]": 0.22,
    "Air temperature [K]": 0.09,
    "Process temperature [K]": 0.05,
}


def build_context(machine_row: pd.Series) -> str:
    """Turn one machine's raw numbers into a structured comparison against
    the healthy baseline -- this is the 'grounding' step. WHY build this
    ourselves instead of just handing Claude the raw row: computing the
    deltas (how far each sensor is from normal) ourselves means Claude
    reasons from FACTS we've verified, not numbers it has to interpret
    unassisted. This reduces the chance of a wrong or hallucinated
    interpretation of what a given number means."""

    lines = []
    for sensor, healthy_avg in HEALTHY_AVERAGES.items():
        actual = machine_row[sensor]
        pct_diff = ((actual - healthy_avg) / healthy_avg) * 100
        importance = FEATURE_IMPORTANCE[sensor]
        lines.append(
            f"- {sensor}: {actual:.1f} (healthy average: {healthy_avg:.1f}, "
            f"{pct_diff:+.1f}% difference, model importance: {importance:.2f})"
        )
    return "\n".join(lines)


def get_recommendation(machine_row: pd.Series) -> str:
    context = build_context(machine_row)

    system_prompt = """You are a maintenance advisory assistant for factory
technicians. You will be given one machine's sensor readings compared
against healthy-machine baselines, plus how much each sensor matters to
the failure-prediction model.

Write a short, plain-language explanation (max 120 words) covering:
1. Why this machine was flagged as at-risk (reference the specific
   sensors that deviate most, weighted by their model importance --
   don't just list every sensor equally)
2. One concrete, practical thing a technician should check or do first

Write for a technician on the factory floor, not a data scientist.
No jargon like "feature importance" or "model" in your actual answer --
translate that into practical terms."""

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Machine {machine_row['Product ID']} (Type {machine_row['Type']}) "
                       f"was flagged with a {machine_row['predicted_failure_probability']:.0%} "
                       f"failure risk.\n\nSensor comparison:\n{context}"
        }],
    )

    return response.content[0].text


if __name__ == "__main__":
    df = pd.read_csv("predictions_for_powerbi.csv")

    # Grab a few flagged machines to demonstrate on -- both correctly caught failures and false alarms
    flagged = df[df["predicted_failure"] == 1].head(3)

    for _, machine in flagged.iterrows():
        print(f"\n{'=' * 60}")
        print(f"Machine: {machine['Product ID']} | Actual outcome: {machine['prediction_outcome']}")
        print(f"{'=' * 60}")
        recommendation = get_recommendation(machine)
        print(recommendation)
