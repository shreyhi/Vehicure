import pytest
from app.utils.vin_generator import generate_vin, is_valid_vin
from app.utils.bloom_filter import BloomFilter
from app.services.validator import ValidationEngine
from app.services.rule_engine import RuleEngine
from app.services.ml_engine import MLEngine
from app.services.simulator import VehicleSimulator

def test_vin_generation_and_validation():
    vin = generate_vin("Volvo")
    assert len(vin) == 17
    assert is_valid_vin(vin) is True

def test_bloom_filter_deduplication():
    bf = BloomFilter(expected_elements=1000, false_positive_rate=0.01)
    key = "TEST_VIN:1001:2026-09-30T10:00:00Z"
    assert bf.contains(key) is False
    bf.add(key)
    assert bf.contains(key) is True

def test_validation_engine():
    valid_vin = generate_vin("Ford")
    valid_payload = {
        "vin": valid_vin,
        "timestamp": "2026-09-30T10:00:00Z",
        "seq": 100,
        "dtc_codes": ["P0301"]
    }
    is_valid, status, msg = ValidationEngine.validate_and_deduplicate(valid_payload)
    assert is_valid is True
    assert status == "OK"

    # Test invalid VIN payload
    invalid_payload = {
        "vin": "INVALID123",
        "timestamp": "2026-09-30T10:00:00Z",
        "seq": 101
    }
    is_valid_inv, status_inv, msg_inv = ValidationEngine.validate_and_deduplicate(invalid_payload)
    assert is_valid_inv is False
    assert status_inv == "INVALID_VIN"

def test_rule_engine_overheating():
    telemetry = {
        "engine_temp": 118.0,
        "battery_voltage": 12.4,
        "dtc_codes": ["P0217"],
        "odometer_km": 60000
    }
    risk_penalty, reasons, rec_action = RuleEngine.evaluate_telemetry_rules(telemetry)
    assert risk_penalty >= 40.0
    assert any("engine temperature" in r.lower() for r in reasons)

def test_ml_engine_evaluation():
    ml = MLEngine()
    metrics = ml.train_and_evaluate()
    assert "primary_model" in metrics
    assert "baseline_model" in metrics
    assert metrics["primary_model"]["precision"] > 0.7
    assert metrics["primary_model"]["f1_score"] > 0.7
    assert metrics["primary_model"]["roc_auc"] > 0.7

    # Test single prediction
    sample = {
        "engine_temp": 115.0,
        "battery_voltage": 10.5,
        "odometer_km": 140000,
        "speed_kmh": 65.0,
        "dtc_codes": ["P0300", "P0301"],
        "harsh_braking": True
    }
    prob = ml.predict_failure_probability(sample)
    assert 0.0 <= prob <= 100.0
    assert prob > 50.0  # High probability expected for multiple severe anomalies

def test_simulator_event_generation():
    sim = VehicleSimulator(num_vehicles=100)
    event = sim.generate_single_event()
    assert "vin" in event
    assert "timestamp" in event
    assert "seq" in event
    assert "engine_temp" in event
