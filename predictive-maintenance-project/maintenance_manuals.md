# Maintenance Manual: Tool Wear Failure (TWF)

## Symptoms
Tool wear failure occurs when a cutting tool has exceeded its safe operating
life, typically between 200-240 minutes of accumulated use in this equipment
class. Machines approaching or exceeding this threshold show elevated torque
readings as the degraded tool edge struggles to cut efficiently, often paired
with a measurable drop in rotational speed as the machine compensates for
increased cutting resistance.

## Diagnostic steps
1. Check the tool wear counter on the machine's control panel or SCADA readout.
2. If wear exceeds 200 minutes, visually inspect the cutting edge for chipping,
   dulling, or built-up material.
3. Cross-check torque readings against the machine's baseline — a sustained
   increase of 30% or more above normal, combined with high tool wear, strongly
   indicates the tool itself is the root cause rather than a separate mechanical
   issue.

## Recommended action
Replace the cutting tool immediately if wear exceeds 220 minutes, regardless
of current torque readings — this is a preventive threshold, not a reactive one.
For machines between 180-220 minutes showing elevated torque, schedule
replacement within the current shift rather than waiting for the next planned
maintenance window.

## Prevention
Track tool wear proactively rather than relying solely on failure alerts.
Consider reducing the replacement threshold if failure rates remain high
despite following current guidelines.

---

# Maintenance Manual: Heat Dissipation Failure (HDF)

## Symptoms
Heat dissipation failure occurs when a machine cannot adequately dissipate
heat generated during operation, typically when the difference between air
temperature and process temperature falls below 8.6K while rotational speed
is simultaneously below 1380 rpm. Under these conditions, heat builds up
faster than the cooling system can remove it.

## Diagnostic steps
1. Calculate the temperature differential: process temperature minus air
   temperature. A differential under 8.6K combined with low rotational speed
   is the specific signature of this failure mode.
2. Inspect cooling fans, air vents, and heat sinks for dust buildup or
   obstruction — this is the most common root cause.
3. Check whether the machine has been running at reduced speed for an extended
   period (e.g., due to a partial load or a control system fault), since low
   speed reduces airflow-based cooling in many machine designs.

## Recommended action
Clean or replace obstructed cooling components immediately. If the machine
must continue operating before cooling can be addressed, temporarily
increasing rotational speed (if process conditions allow) can improve airflow
and reduce heat buildup as a short-term mitigation.

## Prevention
Schedule regular cooling system cleaning as part of routine maintenance,
particularly in dusty or high-particulate factory environments.

---

# Maintenance Manual: Power Failure (PWF)

## Symptoms
Power failure occurs when the power required by the process (torque
multiplied by rotational speed) falls outside the machine's safe operating
band — either too low (under approximately 3500W, indicating insufficient
power delivery) or too high (over approximately 9000W, indicating the
machine is being overdriven).

## Diagnostic steps
1. Calculate power draw: Torque [Nm] x Rotational speed [rad/s].
2. If power is too low, check for a slipping drive belt, an underpowered
   motor fault, or a control system limiting output incorrectly.
3. If power is too high, check whether the machine is processing a workload
   heavier than its rated capacity, or whether a control system fault is
   commanding excessive speed under high load.

## Recommended action
For low-power conditions, inspect the drive train and motor controller
before assuming a process issue. For high-power conditions, reduce load or
verify the control system's speed/torque limits are configured correctly —
running consistently above 9000W can accelerate wear on multiple components
simultaneously, not just the one currently flagged.

## Prevention
Configure control system alarms for power draw outside the safe band, rather
than relying solely on downstream failure detection.

---

# Maintenance Manual: Overstrain Failure (OSF)

## Symptoms
Overstrain failure occurs when the combination of tool wear and torque
exceeds a strain threshold specific to each product quality variant — Low
quality variants fail at a lower combined threshold (11,000 minNm) than
Medium (12,000 minNm) or High (13,000 minNm) variants, reflecting
differences in tooling quality across product tiers.

## Diagnostic steps
1. Calculate the strain product: Tool wear [min] x Torque [Nm].
2. Compare against the threshold for the machine's product Type (L/M/H).
3. This failure mode typically appears as a combination of moderately
   elevated torque AND moderately elevated tool wear together — neither
   individually extreme, but their product crossing the threshold.

## Recommended action
Because this is a compound condition, addressing only one factor (e.g.
replacing the tool but not addressing torque) may not fully resolve the
risk. Replace the tool AND verify torque has returned to baseline before
returning the machine to full production load.

## Prevention
For Low-quality-variant machines specifically, monitor the strain product
more frequently, since their failure threshold is lowest and they cross it
sooner under equivalent operating conditions.

---

# Maintenance Manual: Random Failure (RNF)

## Symptoms
A small proportion of failures occur with no identifiable sensor signature
— all readings within normal operating ranges. This reflects genuine
real-world unpredictability (component-level manufacturing defects, rare
electrical faults) rather than a detectable operating condition.

## Diagnostic steps
Standard sensor-based diagnostics will not identify a cause for this failure
type. If a machine fails with no elevated torque, tool wear, or temperature
readings, do not spend extended time searching for a sensor-detectable root
cause — proceed directly to physical inspection and component-level testing.

## Recommended action
Treat as a standard unplanned failure: isolate the machine, perform a full
physical inspection, and replace or repair the failed component based on
direct inspection findings rather than sensor data.

## Prevention
This failure mode is inherently difficult to prevent through predictive
monitoring alone. Maintaining adequate spare parts inventory and a fast
response process is the most effective mitigation, since prediction cannot
meaningfully reduce this category's occurrence rate.

