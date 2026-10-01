import re
import logging
from typing import Dict, Any, Tuple
from app.utils.vin_generator import is_valid_vin
from app.utils.bloom_filter import BloomFilter

logger = logging.getLogger("vehicure.validator")

# Global Bloom Filter for fast deduplication
bloom_dedup = BloomFilter(expected_elements=1000000, false_positive_rate=0.001)

DTC_PATTERN = re.compile(r"^[PBUC][0-3][0-9A-F]{3}$", re.IGNORECASE)

class ValidationEngine:
    """
    Validates, deduplicates, and re-orders incoming vehicle telemetry payloads.
    Enforces idempotency and structural schema checks.
    """
    @staticmethod
    def validate_and_deduplicate(payload: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Validates payload format and checks for duplicates.
        Returns:
            - is_valid (bool)
            - status_code ('OK', 'DUPLICATE', 'INVALID_VIN', 'INVALID_SCHEMA')
            - error_message (str)
        """
        # 1. Structural schema validation
        vin = payload.get("vin")
        if not vin:
            return False, "INVALID_SCHEMA", "Missing required field 'vin'"
            
        timestamp = payload.get("timestamp")
        if not timestamp:
            return False, "INVALID_SCHEMA", "Missing required field 'timestamp'"

        seq = payload.get("seq")
        if seq is None:
            return False, "INVALID_SCHEMA", "Missing required field 'seq'"

        # 2. VIN Validation (17 chars, valid checksum)
        if not is_valid_vin(str(vin)):
            return False, "INVALID_VIN", f"Invalid VIN format or checksum: {vin}"

        # 3. DTC Format Check
        dtc_codes = payload.get("dtc_codes", [])
        for code in dtc_codes:
            if not DTC_PATTERN.match(str(code)):
                return False, "INVALID_SCHEMA", f"Invalid DTC code format: {code}"

        # 4. Deduplication via Bloom Filter / Deduplication key
        dedup_key = f"{vin}:{seq}:{timestamp}"
        if bloom_dedup.contains(dedup_key):
            # Potential duplicate identified by Bloom Filter
            logger.warning(f"Duplicate event detected for VIN {vin} (Seq: {seq})")
            return False, "DUPLICATE", f"Duplicate event dropped (Seq: {seq})"
            
        # Add to Bloom filter
        bloom_dedup.add(dedup_key)

        return True, "OK", "Payload validated successfully"
