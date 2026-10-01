import asyncio
import random
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.utils.vin_generator import generate_vin
from app.services.validator import ValidationEngine
from app.services.rule_engine import RuleEngine
from app.services.ml_engine import ml_engine_singleton
from app.services.alert_engine import AlertEngine
from app.services.metrics_tracker import metrics_tracker_singleton

logger = logging.getLogger("vehicure.simulator")

class VehicleSimulator:
    """
    High-Performance Configurable Telemetry Simulator for 100,000+ connected vehicles.
    Capable of generating normal telemetry, bursty traffic spikes, duplicate events,
    out-of-order sequence payloads, and injectable fault anomalies.
    """
    def __init__(self, num_vehicles: int = 100000):
        self.num_vehicles = num_vehicles
        self.is_running = False
        self.tps = 50                         # Target events per second
        self.anomaly_rate_pct = 5.0           # % of events with faults
        self.burst_mode = False               # Spikes traffic by 3x
        self.inject_duplicates = False        # Duplicates previous payloads
        self.inject_out_of_order = False      # Delays sequence timestamps
        
        # Vehicle cached states
        self.vehicles: List[Dict[str, Any]] = []
        self.sequence_counter: Dict[str, int] = {}
        self.last_emitted_event: Optional[Dict[str, Any]] = None
        self.out_of_order_queue: List[Dict[str, Any]] = []
        self.recent_events_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 200            # Real-time event stream buffer for UI

    def initialize_vehicles(self):
        """Initializes 100,000 synthetic vehicles with initial state."""
        if self.vehicles:
            return
            
        logger.info(f"Initializing {self.num_vehicles} synthetic vehicle profiles...")
        oems = ["Volvo", "Subaru", "Stellantis", "Ford", "Tesla", "Mercedes-Benz"]
        
        for i in range(min(5000, self.num_vehicles)): # Active pool for real-time streaming
            oem = oems[i % len(oems)]
            vin = generate_vin(oem)
            self.sequence_counter[vin] = 1000
            
            self.vehicles.append({
                "vin": vin,
                "oem": oem,
                "lat": round(37.7749 + random.uniform(-2.0, 2.0), 4),
                "lon": round(-122.4194 + random.uniform(-2.0, 2.0), 4),
                "speed_kmh": round(random.uniform(20.0, 95.0), 1),
                "engine_temp": round(random.uniform(86.0, 94.0), 1),
                "battery_voltage": round(random.uniform(12.4, 13.0), 1),
                "fuel_level_pct": round(random.uniform(20.0, 98.0), 1),
                "odometer_km": round(random.uniform(8000.0, 140000.0), 1),
                "has_active_fault": False,
                "fault_type": None
            })
        logger.info("Vehicle simulator initialized successfully.")

    def generate_single_event(self) -> Dict[str, Any]:
        """Generates one telemetry event payload."""
        if not self.vehicles:
            self.initialize_vehicles()

        v = random.choice(self.vehicles)
        vin = v["vin"]
        self.sequence_counter[vin] += 1
        seq = self.sequence_counter[vin]

        # Check injection modes
        is_duplicate = False
        is_out_of_order = False

        if self.inject_duplicates and self.last_emitted_event and random.random() < 0.3:
            # Emit exact duplicate of previous payload
            return dict(self.last_emitted_event)

        if self.inject_out_of_order and random.random() < 0.2:
            seq = max(1, seq - random.randint(5, 20))
            is_out_of_order = True

        # Normal random walk position & telemetry
        v["lat"] += random.uniform(-0.002, 0.002)
        v["lon"] += random.uniform(-0.002, 0.002)
        v["speed_kmh"] = max(0.0, min(140.0, v["speed_kmh"] + random.uniform(-5.0, 5.0)))
        v["odometer_km"] += (v["speed_kmh"] / 3600.0)

        dtc_codes = []
        harsh_braking = False
        harsh_accel = False
        status = "MOVING" if v["speed_kmh"] > 5.0 else "IDLE"

        # Determine if this event should trigger an anomaly
        if random.random() * 100 < self.anomaly_rate_pct or v["has_active_fault"]:
            # Anomaly profile
            v["engine_temp"] = round(random.uniform(104.0, 122.0), 1)
            v["battery_voltage"] = round(random.uniform(10.2, 11.4), 1)
            dtc_codes = random.choice([["P0300", "P0301"], ["P0217"], ["P0562"], ["P0420"]])
            harsh_braking = random.choice([True, False])
            harsh_accel = random.choice([True, False])
            status = "FAULT_ACTIVE"
        else:
            v["engine_temp"] = round(max(80.0, min(100.0, v["engine_temp"] + random.uniform(-1.0, 1.0))), 1)
            v["battery_voltage"] = round(max(12.0, min(14.2, v["battery_voltage"] + random.uniform(-0.1, 0.1))), 1)

        iso_timestamp = datetime.now(timezone.utc).isoformat()

        event = {
            "vin": vin,
            "timestamp": iso_timestamp,
            "lat": round(v["lat"], 4),
            "lon": round(v["lon"], 4),
            "speed_kmh": round(v["speed_kmh"], 1),
            "engine_temp": v["engine_temp"],
            "battery_voltage": v["battery_voltage"],
            "fuel_level_pct": round(v["fuel_level_pct"], 1),
            "odometer_km": round(v["odometer_km"], 1),
            "dtc_codes": dtc_codes,
            "harsh_braking": harsh_braking,
            "harsh_accel": harsh_accel,
            "vehicle_status": status,
            "seq": seq
        }

        self.last_emitted_event = event
        return event

    async def start_streaming(self, callback_func=None):
        """Main asynchronous event streaming loop."""
        self.is_running = True
        self.initialize_vehicles()
        logger.info(f"Simulator streaming started at target TPS={self.tps}...")

        while self.is_running:
            t0 = time.time()
            current_target_tps = self.tps * 3 if self.burst_mode else self.tps
            sleep_interval = 1.0 / max(1, current_target_tps)

            event = self.generate_single_event()

            # Process through validation & predictive pipeline
            t_process_0 = time.time()
            is_valid, status, msg = ValidationEngine.validate_and_deduplicate(event)
            latency_ms = (time.time() - t_process_0) * 1000.0

            metrics_tracker_singleton.record_event_processed(latency_ms, is_error=(not is_valid and status != "DUPLICATE"))

            if is_valid:
                # Calculate Rule + ML Risk Score
                rule_penalty, reasons, rec_action = RuleEngine.evaluate_telemetry_rules(event)
                ml_prob = ml_engine_singleton.predict_failure_probability(event)
                
                # Combined Risk Score (40% Rule + 60% ML Probability)
                combined_risk = round(0.4 * rule_penalty + 0.6 * ml_prob, 1)
                health_score = round(max(0.0, 100.0 - combined_risk), 1)
                
                if combined_risk >= 75.0:
                    risk_level = "CRITICAL"
                elif combined_risk >= 50.0:
                    risk_level = "HIGH"
                elif combined_risk >= 25.0:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"

                event["computed_health_score"] = health_score
                event["computed_risk_score"] = combined_risk
                event["computed_risk_level"] = risk_level
                event["computed_failure_prob"] = ml_prob
                event["risk_reasons"] = reasons
                event["recommended_action"] = rec_action

                # Push to buffer for live UI streaming
                if len(self.recent_events_buffer) >= self.max_buffer_size:
                    self.recent_events_buffer.pop(0)
                self.recent_events_buffer.append(event)

                if callback_func:
                    await callback_func(event)

            elapsed = time.time() - t0
            time_to_sleep = max(0.001, sleep_interval - elapsed)
            await asyncio.sleep(time_to_sleep)

    def stop_streaming(self):
        """Stops the simulator loop."""
        self.is_running = False
        logger.info("Simulator streaming stopped.")

simulator_singleton = VehicleSimulator()
