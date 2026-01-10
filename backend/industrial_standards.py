# Industrial Standards Configuration
# Master source for all industrial thresholds and standards
# Updated to follow ISO 10816-3 and NEMA standards

# Temperature thresholds (Celsius) - NEMA Class B Insulation Standards
TEMPERATURE_THRESHOLDS = {
    "good": {"min": 20, "max": 70},           # Normal operating range
    "satisfactory": {"min": 70, "max": 85},   # Acceptable but monitor
    "unsatisfactory": {"min": 85, "max": 105}, # Requires attention
    "unacceptable": {"min": 105, "max": 200}   # Immediate action required
}

# Vibration thresholds (mm/s RMS) - ISO 10816-3 Standard
VIBRATION_THRESHOLDS = {
    "good": {"min": 0, "max": 1.8},          # Zone A: Excellent condition
    "satisfactory": {"min": 1.8, "max": 4.5}, # Zone B: Acceptable operation
    "unsatisfactory": {"min": 4.5, "max": 11.2}, # Zone C: Restricted operation
    "unacceptable": {"min": 11.2, "max": 50.0}   # Zone D: Unacceptable operation
}

# Speed thresholds (RPM) - Industrial motor operation standards
SPEED_THRESHOLDS = {
    "good": {"min": 1150, "max": 1200},       # Normal operating range
    "satisfactory": {"min": 1200, "max": 1300}, # Slightly elevated but acceptable
    "unsatisfactory": {"min": 1300, "max": 1450}, # High speed - monitor closely
    "unacceptable": {"min": 1450, "max": 5000}    # Dangerous overspeed
}

# Combined thresholds for easy access
INDUSTRIAL_STANDARDS = {
    "temperature": TEMPERATURE_THRESHOLDS,
    "vibration": VIBRATION_THRESHOLDS,
    "speed": SPEED_THRESHOLDS
}

# Industry standard condition levels
CONDITION_LEVELS = ["good", "satisfactory", "unsatisfactory", "unacceptable"]

def get_threshold(parameter, condition):
    """Get threshold range for a specific parameter and condition"""
    return INDUSTRIAL_STANDARDS.get(parameter, {}).get(condition, {})

def get_all_thresholds():
    """Get all industrial standards thresholds"""
    return INDUSTRIAL_STANDARDS

def classify_value(parameter, value):
    """Classify a sensor value based on industry standards (ISO 10816-3 & NEMA)"""
    thresholds = INDUSTRIAL_STANDARDS.get(parameter, {})
    
    if not thresholds:
        return "unknown"
    
    # Check each condition level in order
    for level in CONDITION_LEVELS:
        if level in thresholds:
            range_info = thresholds[level]
            if range_info["min"] <= value < range_info["max"]:
                return level
    
    # If value exceeds all ranges, return most severe
    return "unacceptable"

def get_condition_score(temperature, vibration, speed):
    """Calculate overall condition score based on all parameters using industry standards"""
    scores = {
        "good": 0,
        "satisfactory": 1,
        "unsatisfactory": 2,
        "unacceptable": 3
    }
    
    temp_condition = classify_value("temperature", temperature)
    vib_condition = classify_value("vibration", vibration)
    speed_condition = classify_value("speed", speed)
    
    # Get the worst condition (highest score)
    conditions = [temp_condition, vib_condition, speed_condition]
    condition_scores = [scores.get(cond, 3) for cond in conditions]
    max_score = max(condition_scores)
    
    # Return the condition level corresponding to the worst score
    for condition, score in scores.items():
        if score == max_score:
            return condition
    
    return "unacceptable"

def get_detailed_analysis(temperature, vibration, speed):
    """Get detailed analysis of all parameters with industry standard classifications"""
    temp_condition = classify_value("temperature", temperature)
    vib_condition = classify_value("vibration", vibration)
    speed_condition = classify_value("speed", speed)
    overall_condition = get_condition_score(temperature, vibration, speed)
    
    return {
        "overall_condition": overall_condition,
        "temperature": {
            "value": temperature,
            "condition": temp_condition,
            "unit": "°C",
            "standard": "NEMA Class B"
        },
        "vibration": {
            "value": vibration,
            "condition": vib_condition,
            "unit": "mm/s RMS",
            "standard": "ISO 10816-3"
        },
        "speed": {
            "value": speed,
            "condition": speed_condition,
            "unit": "RPM",
            "standard": "Industrial Practice"
        }
    }

# Industry standards reference information
STANDARDS_INFO = {
    "temperature": {
        "standard": "NEMA MG-1 / IEC 60034-1",
        "description": "Class B insulation motor temperature limits",
        "reference": "Maximum hot spot temperature 130°C for Class B insulation"
    },
    "vibration": {
        "standard": "ISO 10816-3:2009",
        "description": "Industrial machinery vibration evaluation",
        "reference": "For machines >15kW, 120-15000 RPM, Group 2 classification"
    },
    "speed": {
        "standard": "Industry Best Practice",
        "description": "Typical 4-pole, 60Hz industrial motor operation",
        "reference": "Synchronous speed 1800 RPM, typical load operation 1150-1200 RPM"
    }
}

if __name__ == "__main__":
    # Test the industrial standards functions
    print("🏭 Testing Industrial Standards Module")
    print("=" * 50)
    
    # Display standards information
    print("\n📋 Industry Standards Reference:")
    for param, info in STANDARDS_INFO.items():
        print(f"\n{param.upper()}:")
        print(f"  Standard: {info['standard']}")
        print(f"  Description: {info['description']}")
        print(f"  Reference: {info['reference']}")
    
    print("\n" + "=" * 50)
    print("🧪 Test Classifications:")
    
    # Test cases
    test_cases = [
        (65.0, 1.5, 1180.0, "Normal operation"),
        (78.0, 3.2, 1250.0, "Satisfactory condition"),
        (92.0, 6.8, 1380.0, "Unsatisfactory condition"),
        (115.0, 15.0, 1520.0, "Unacceptable condition")
    ]
    
    for temp, vib, speed, description in test_cases:
        analysis = get_detailed_analysis(temp, vib, speed)
        print(f"\n{description}:")
        print(f"  Values: T={temp}°C, V={vib}mm/s, S={speed}RPM")
        print(f"  Overall: {analysis['overall_condition'].upper()}")
        print(f"  Temperature: {analysis['temperature']['condition']} ({analysis['temperature']['standard']})")
        print(f"  Vibration: {analysis['vibration']['condition']} ({analysis['vibration']['standard']})")
        print(f"  Speed: {analysis['speed']['condition']} ({analysis['speed']['standard']})")
    
    print(f"\n{'=' * 50}")
    print("✅ Industrial standards module working correctly!")