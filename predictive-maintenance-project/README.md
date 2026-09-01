# Predictive Maintenance for Industrial Machinery

A machine learning system that predicts equipment failure from sensor readings, with a Claude-powered advisory layer that translates model predictions into plain-language maintenance recommendations for factory technicians.

Built on the AI4I 2020 Predictive Maintenance dataset (UCI Machine Learning Repository) — 10,000 rows of simulated industrial sensor data modeled after real machine telemetry.

## Why this project

Predictive maintenance — catching equipment failure before it happens using sensor data — is a core use case in industrial AI/data engineering, and one directly relevant to clients running factory or production-line equipment. This project builds the full loop: a classification model that flags at-risk machines, an honest evaluation of its trade-offs, and an AI layer that makes the model's output usable by someone without a data science background.

## Architecture

```
AI4I 2020 dataset --> Python (feature engineering, Random Forest classifier)
                              |
                              v
                    predictions_for_powerbi.csv --> Power BI dashboard
                              |
                              v
                  Claude API (maintenance advisory agent)
```

<img width="1425" height="802" alt="Dashbord-ss" src="https://github.com/user-attachments/assets/41378dd4-a92e-439c-aac5-e11470e6d88e" />

## Tech stack

- **Modeling:** Python (pandas, scikit-learn — RandomForestClassifier)
- **Visualization:** Power BI
- **AI layer:** Claude API — translates flagged machines into plain-language, technician-facing maintenance recommendations

## The modeling problem: severe class imbalance

Only 3.39% of machines in the dataset failed (339 of 10,000). This matters a lot: a model that always predicts "no failure" would already be 97%+ "accurate" while catching zero real failures. The whole project is built around handling this properly rather than being misled by accuracy alone:

- **`class_weight="balanced"`** on the Random Forest, so mistakes on the rare failure class are penalized more heavily
- **Stratified train/test split**, so both sets keep the same 3.39% failure rate — a random split risks putting too few failures in the test set by chance, making evaluation unreliable
- **Precision/recall/F1 instead of accuracy** as the real evaluation metrics
- **Dropped the 5 failure-subtype columns** (TWF, HDF, PWF, OSF, RNF) before training — these were used to construct the failure label itself, so including them would be data leakage (a trivially "perfect" but useless model, since you'd never have those flags known ahead of a real failure)

## Model results

At a 0.40 probability threshold (chosen deliberately over the default 0.5 — see below):

| Metric | Value |
|---|---|
| Recall (failures caught) | 85% (58 of 68 in test set) |
| Precision | 42% |
| False alarms | 79 (out of 1,932 healthy machines, ~4%) |
| ROC-AUC | 0.970 |

**Why 0.40, not the default 0.5:** the classifier outputs a probability, not a hard yes/no — the threshold is a business decision, not a fixed model property. I evaluated precision/recall across 7 thresholds (0.20 to 0.80) and chose 0.40 because a missed failure (unplanned downtime, safety risk) is typically far more costly than a false alarm (a technician spending 20 minutes on an unnecessary inspection). At 0.40, the model catches 85% of real failures at a false-alarm rate of roughly 1.4 unnecessary inspections per real failure caught — a defensible trade-off to bring to a maintenance manager.

**Feature importance:** Torque (34%), Rotational speed (29%), and Tool wear (22%) dominate the model's decisions — together over 85% of its total reasoning — while temperature and product quality tier matter far less. This matches the physical intuition: machines under mechanical strain (high torque, degraded tooling, resistance slowing rotation) are the ones failing, not machines running slightly warm.

## Maintenance advisory agent

`05_maintenance_advisor.py` takes a flagged machine's sensor readings, compares them against healthy-machine baselines (weighted by how much each sensor matters to the model), and asks Claude to generate a short, jargon-free explanation a factory technician can act on — not a data scientist.

This is deliberately more than a single API call: the script computes each sensor's percentage deviation from normal *before* handing it to Claude, so the model reasons from verified facts rather than interpreting raw numbers itself. This reduces the risk of a misleading explanation and is a concrete example of a modest but genuine agentic pattern — grounding an LLM's reasoning in computed, structured context rather than open-ended generation.

Example output:

```                                                              
============================================================
Machine: L50177 | Actual outcome: False Positive (false alarm)
============================================================
## Machine L50177 – Failure Risk Alert (61%)

**Why it was flagged:**
This machine is working much harder than it should be. Torque is running 58% above normal — meaning the machine is straining significantly under load — and rotational speed has dropped 13% below normal at the same time. This combination (high strain, slower speed) is the biggest warning sign here. On top of that, the cutting tool has accumulated 43% more wear time than a typical healthy machine, which compounds the risk.

Temperatures look fine, so heat isn't the concern right now.

**What to check first:**
Inspect the cutting tool immediately — at 153 minutes of wear, it likely needs replacing. A worn tool forces the machine to work harder, which would directly explain both the high torque and sluggish speed.

============================================================
Machine: L51038 | Actual outcome: False Positive (false alarm)
============================================================
## Machine L51038 – Failure Risk Alert (51%)

**Why it was flagged:**
The biggest concern is the tool wear, which is nearly **double** what's typical for a healthy machine (209 minutes vs. ~107 minutes). This is the clearest sign something is wrong. On top of that, torque is running slightly low, which can indicate the tool is struggling to cut efficiently — often a sign of a worn or degraded tool. Rotational speed is normal, and temperatures are barely above average, so those aren't the issue here.

**What to do first:**
**Inspect and likely replace the cutting tool immediately.** A tool at 209 minutes of wear is well past the normal replacement point and is your most probable failure source.

============================================================
Machine: L52031 | Actual outcome: True Positive (caught)
============================================================
## Machine L52031 – Maintenance Advisory

**Why it was flagged:**
The two biggest concerns are torque and rotational speed. Torque is running about 31% higher than normal – meaning the machine is working significantly harder than it should be. At the same time, rotational speed is notably slower than usual. That combination – high resistance, low speed – is the clearest warning sign here and is driving most of the elevated risk. Tool wear is slightly lower than average, so that's less of a concern right now.

**What to check first:**
Inspect the drive system for mechanical resistance – look for lubrication issues, a worn or slipping belt/coupling, or a partial blockage in the drivetrain. Excess load causing high torque while dragging speed down often points there first.
```

Notably, this was a false alarm — the machine didn't actually fail. The explanation is still reasonable: elevated tool wear genuinely is a real risk signal, even in cases where the machine turned out fine. This is an honest distinction worth making explicit: the agent explains *why a machine looks at-risk*, not a guarantee that it will fail — which is the correct framing for an advisory tool, not a replacement for technician judgment.

## Dashboard

Power BI dashboard covering: model performance KPIs, feature importance, a missed-failures table, risk score distribution, sensor comparison by outcome, and a torque-vs-tool-wear scatter colored by prediction outcome.

<img width="1425" height="802" alt="Dashbord-ss" src="https://github.com/user-attachments/assets/a3af47b5-8cc5-47a0-b332-8eb4876ec2b4" />

## Data source

[AI4I 2020 Predictive Maintenance Dataset](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) —
UCI Machine Learning Repository. Public, free, simulates real industrial sensor telemetry.

## Setup

```bash
pip install -r requirements.txt
python 01_explore_data.py
python 02_build_model.py
python 03_threshold_tuning.py
python 04_export_predictions.py
python 05_maintenance_advisor.py
```

Requires an Anthropic API key set as an environment variable (never hardcoded — see script comments).
