import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger("vehicure.alert_engine")

class AlertEngine:
    """
    Alert Engine for managing active critical alerts and preventive maintenance triggers.
    Deduplicates repeated alerts for the same VIN and handles lifecycle transitions.
    """
    @staticmethod
    def process_risk_and_generate_alert(
        vin: str,
        risk_score: float,
        risk_level: str,
        failure_prob: float,
        reasons: list[str],
        recommended_action: str,
        dtc_codes: list[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Generates an Alert payload if risk level is HIGH or CRITICAL.
        """
        if risk_level not in ["HIGH", "CRITICAL"]:
            return None

        primary_dtc = dtc_codes[0] if dtc_codes else None
        reason_text = " | ".join(reasons) if reasons else f"Vehicle risk score reached {risk_score}/100"

        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        alert_payload = {
            "id": alert_id,
            "vin": vin,
            "severity": risk_level,
            "reason": f"Predicted Failure Risk {failure_prob}%: {reason_text}",
            "dtc_code": primary_dtc,
            "recommended_action": recommended_action,
            "status": "ACTIVE",
            "created_at": datetime.utcnow().isoformat()
        }
        return alert_payload

    @staticmethod
    def create_preventive_work_order(vin: str, alert_reason: str, recommended_action: str) -> Dict[str, Any]:
        """Creates an automated preventive maintenance work order."""
        order_id = f"WO-{uuid.uuid4().hex[:8].upper()}"
        scheduled = datetime.utcnow() + timedelta(days=2)
        return {
            "id": order_id,
            "vin": vin,
            "priority": "HIGH",
            "title": f"Preventive Maintenance: {vin[:8]}...",
            "description": f"Auto-triggered work order. Reason: {alert_reason}. Action: {recommended_action}",
            "status": "SCHEDULED",
            "scheduled_date": scheduled.strftime("%Y-%m-%d %H:%M:%S"),
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
