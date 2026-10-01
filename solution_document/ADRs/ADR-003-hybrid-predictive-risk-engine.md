# ADR 003: Hybrid Predictive Engine (Domain Rules + Random Forest ML)

## Status
**Accepted**

## Context
Pure Machine Learning models can act as black boxes, making it difficult for fleet managers to understand *why* a vehicle was flagged as high risk. Conversely, pure rule-based engines miss non-linear feature interactions (e.g. combined high mileage + minor voltage drops + subtle temperature volatility).

## Decision
We implement a **Hybrid Predictive Risk Engine**:
1. **Domain Rule Engine**: Evaluates immediate safety rules (Engine Temp > 105°C, Battery < 11.5V, Critical DTC codes P0300/P0217, harsh maneuvers). Generates deterministic human-readable explanations.
2. **Random Forest Classifier**: Scikit-learn model trained on multi-sensor features (engine temp, battery voltage, odometer, speed, fault counts) outputting failure probability (0-100%).
3. **Combined Vehicle Risk Score**:
   $$\text{Risk Score} = 0.4 \times \text{Rule Penalty} + 0.6 \times \text{ML Probability}$$
4. **Baseline Comparison**: Model evaluated against a Logistic Regression baseline with measured Precision, Recall, F1-Score, and ROC-AUC.

## Consequences
- **Positive**: High accuracy with instant explainability. Fleet managers receive exact bullet points for every high-risk vehicle.
- **Negative**: Requires ongoing model retraining as fleet telemetry profiles evolve.
