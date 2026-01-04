# Industrial Standards Configuration
# Master source for all industrial thresholds and standards

# Temperature thresholds (Celsius)
TEMPERATURE_THRESHOLDS = {
    "normal": {"min": 20, "max": 65},
    "warning": {"min": 65, "max": 85},
    "critical": {"min": 85, "max": 120}
}

# Vibration thresholds (mm/s RMS)
VIBRATION_THRESHOLDS = {
    "normal": {"min": 0, "max": 3.0},
    "warning": {"min": 3.0, "max": 7.0},
    "critical": {"min": 7.0, "max": 15.0}
}

# Speed thresholds (RPM)
SPEED_THRESHOLDS = {
    "normal": {"min": 800, "max": 1150},
    "warning": {"min": 1150, "max": 1350},
    "critical": {"min": 1350, "max": 2000}
}

# Combined thresholds for easy access
INDUSTRIAL_STANDARDS = {
    "temperature": TEMPERATURE_THRESHOLDS,
    "vibration": VIBRATION_THRESHOLDS,
    "speed": SPEED_THRESHOLDS
}

def get_threshold(parameter, condition):
    """Get threshold value for a specific parameter and condition"""
    return INDUSTRIAL_STANDARDS.get(parameter, {}).get(condition, {})

def get_all_thresholds():
    """Get all industrial standards thresholds"""
    return INDUSTRIAL_STANDARDS

def classify_value(parameter, value):
    """Classify a sensor value based on industrial standards"""
    thresholds = INDUSTRIAL_STANDARDS.get(parameter, {})
    
    if not thresholds:
        return "unknown"
    
    if value <= thresholds["normal"]["max"]:
        return "normal"
    elif value <= thresholds["warning"]["max"]:
        return "warning"
    else:
        return "critical"

def get_condition_score(temperature, vibration, speed):
    """Calculate overall condition score based on all parameters"""
    scores = {
        "normal": 0,
        "warning": 1,
        "critical": 2
    }
    
    temp_condition = classify_value("temperature", temperature)
    vib_condition = classify_value("vibration", vibration)
    speed_condition = classify_value("speed", speed)
    
    total_score = (scores[temp_condition] + 
                   scores[vib_condition] + 
                   scores[speed_condition])
    
    if total_score >= 4:
        return "critical"
    elif total_score >= 2:
        return "warning"
    else:
        return "normal"