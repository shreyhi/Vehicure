import random
import string

# WMI (World Manufacturer Identifier) map for realistic OEM representation
OEM_WMIS = {
    "Volvo": ["YV1", "YV4"],
    "Subaru": ["JF1", "JF2"],
    "Stellantis": ["1C3", "1C4", "3C6"],
    "Ford": ["1FA", "1FT", "1FM"],
    "Tesla": ["5YJ", "7SA"],
    "Mercedes-Benz": ["WDD", "W1K"]
}

# Transliteration table for ISO 3779 checksum calculation
VIN_TRANSLITERATION = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
    'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6, 'X': 7, 'Y': 8, 'Z': 9,
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
}

VIN_WEIGHTS = [8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2]

def calculate_vin_checksum(vin_17_chars: str) -> str:
    """Calculates ISO 3779 VIN check digit (9th position)."""
    total = 0
    for idx, char in enumerate(vin_17_chars):
        if idx == 8: # 9th position is check digit itself
            continue
        val = VIN_TRANSLITERATION.get(char, 0)
        total += val * VIN_WEIGHTS[idx]
    remainder = total % 11
    return 'X' if remainder == 10 else str(remainder)

def generate_vin(oem: str = None) -> str:
    """Generates a valid 17-character ISO 3779 compliant VIN."""
    if not oem or oem not in OEM_WMIS:
        oem = random.choice(list(OEM_WMIS.keys()))
    
    wmi = random.choice(OEM_WMIS[oem])
    vds = "".join(random.choices(string.ascii_uppercase.replace('I', '').replace('O', '').replace('Q', '') + string.digits, k=5))
    year_code = random.choice("ABCDEFGHJKLMNPRSTVWXY123456789")
    plant_code = random.choice("A1B2C3D4")
    vis = "".join(random.choices(string.digits, k=6))
    
    # Form 17 chars with dummy check digit
    raw_vin = f"{wmi}{vds}0{year_code}{plant_code}{vis}"
    check_digit = calculate_vin_checksum(raw_vin)
    final_vin = f"{wmi}{vds}{check_digit}{year_code}{plant_code}{vis}"
    return final_vin

def is_valid_vin(vin: str) -> bool:
    """Validates 17-character VIN length, disallowed characters (I, O, Q), and checksum."""
    if len(vin) != 17:
        return False
    if any(c in vin for c in ['I', 'O', 'Q', 'i', 'o', 'q']):
        return False
    # Verify checksum
    expected_check = calculate_vin_checksum(vin)
    return vin[8].upper() == expected_check
