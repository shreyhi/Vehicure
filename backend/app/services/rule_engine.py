from typing import Dict, Any, List, Tuple

class RuleEngine:
    """
    Domain Rule Engine for instant anomaly detection, rule-based risk scoring,
    and human-readable risk reason generation.
    """
    @staticmethod
    def evaluate_telemetry_rules(telemetry: Dict[str, Any]) -> Tuple[float, List[str], str]:
        """
        Evaluates a telemetry event payload against expert vehicle health rules.
        Returns:
            - rule_risk_penalty (float: 0.0 to 100.0)
            - reasons (List[str]): List of key anomaly bullet points
            - recommended_action (str): Specific maintenance recommendation
        """
        reasons = []
        risk_penalty = 0.0
        actions = []

        engine_temp = telemetry.get("engine_temp", 90.0)
        battery_volts = telemetry.get("battery_voltage", 12.6)
        dtc_codes = telemetry.get("dtc_codes", [])
        harsh_braking = telemetry.get("harsh_braking", False)
        harsh_accel = telemetry.get("harsh_accel", False)
        odometer_km = telemetry.get("odometer_km", 50000.0)

        # Rule 1: Engine Temperature Anomaly
        if engine_temp >= 115.0:
            risk_penalty += 40.0
            reasons.append(f"Critical engine temperature surge ({engine_temp}°C)")
            actions.append("Pull over immediately and inspect engine cooling system.")
        elif engine_temp >= 102.0:
            risk_penalty += 20.0
            reasons.append(f"Elevated engine temperature detected ({engine_temp}°C)")
            actions.append("Schedule radiator and coolant inspection.")

        # Rule 2: Battery & Electrical Voltage Anomaly
        if battery_volts <= 11.2:
            risk_penalty += 35.0
            reasons.append(f"Severe battery voltage drop ({battery_volts} V)")
            actions.append("Test/replace battery and inspect alternator charging circuit.")
        elif battery_volts <= 11.8:
            risk_penalty += 15.0
            reasons.append(f"Abnormal low battery voltage ({battery_volts} V)")
            actions.append("Check battery charge and terminal contacts.")
        elif battery_volts >= 15.2:
            risk_penalty += 25.0
            reasons.append(f"Overcharging system voltage detected ({battery_volts} V)")
            actions.append("Inspect alternator voltage regulator.")

        # Rule 3: Diagnostic Trouble Codes (DTC)
        if len(dtc_codes) > 0:
            risk_penalty += min(35.0, len(dtc_codes) * 15.0)
            reasons.append(f"{len(dtc_codes)} active diagnostic fault codes ({', '.join(dtc_codes)})")
            if "P0300" in dtc_codes or "P0301" in dtc_codes:
                actions.append("Perform cylinder ignition and misfire diagnostic test.")
            if "P0217" in dtc_codes:
                actions.append("Inspect engine thermostat and coolant pump.")
            if "P0420" in dtc_codes:
                actions.append("Inspect catalytic converter efficiency and O2 sensors.")

        # Rule 4: Harsh Maneuvers & Driving Behavior
        if harsh_braking and harsh_accel:
            risk_penalty += 15.0
            reasons.append("Repeated severe harsh acceleration & braking maneuvers")
        elif harsh_braking or harsh_accel:
            risk_penalty += 8.0
            reasons.append("Harsh driving event detected")

        # Rule 5: High Mileage Degradation Factor
        if odometer_km > 150000.0 and len(dtc_codes) > 0:
            risk_penalty += 10.0
            reasons.append("High mileage component wear threshold exceeded (>150,000 km)")

        # Cap penalty at 100.0
        risk_penalty = min(100.0, risk_penalty)

        if not reasons:
            reasons = ["Normal operating parameters within baseline tolerances"]
            rec_action = "No immediate maintenance required. Standard inspection schedule."
        else:
            rec_action = actions[0] if actions else "Schedule preventive vehicle health inspection."

        return risk_penalty, reasons, rec_action
