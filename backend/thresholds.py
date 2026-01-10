#!/usr/bin/env python3
"""
Industrial Standards Threshold Configuration
==========================================

This module defines all threshold values based on international industrial standards:
- Temperature: NEMA MG-1 and IEC 60034-1 standards for Class B insulation motors
- Vibration: ISO 10816-3 standard for industrial machinery >15kW, 120-15000 RPM
- Speed: Industry best practices for motor operation monitoring

All components should import and use these values to ensure consistency with industry standards.
"""

# INDUSTRY STANDARD THRESHOLD VALUES
# ==================================

# Temperature Thresholds (°C) - Based on NEMA Class B Insulation Standards
# Class B insulation: Maximum hot spot temperature 130°C
# Typical motor operating temperature: 40°C ambient + 90°C rise = 130°C max
TEMP_THRESHOLDS = {
    'good': {'min': 20.0, 'max': 70.0},        # Normal operating range
    'satisfactory': {'min': 70.0, 'max': 85.0}, # Acceptable but monitor
    'unsatisfactory': {'min': 85.0, 'max': 105.0}, # Requires attention
    'unacceptable': {'min': 105.0, 'max': 200.0}   # Immediate action required
}

# Vibration Thresholds (mm/s RMS) - Based on ISO 10816-3 Standard
# For industrial machines >15kW, rigid foundation, Group 2 (20-402 HP motors)
VIBRATION_THRESHOLDS = {
    'good': {'min': 0.0, 'max': 1.8},          # Zone A: Excellent condition
    'satisfactory': {'min': 1.8, 'max': 4.5},  # Zone B: Acceptable operation
    'unsatisfactory': {'min': 4.5, 'max': 11.2}, # Zone C: Restricted operation
    'unacceptable': {'min': 11.2, 'max': 50.0}   # Zone D: Unacceptable operation
}

# Speed Thresholds (RPM) - Based on typical industrial motor operation
# Standard industrial motors typically operate at 1200-1800 RPM (4-pole, 60Hz)
SPEED_THRESHOLDS = {
    'good': {'min': 1150.0, 'max': 1200.0},      # Normal operating range
    'satisfactory': {'min': 1200.0, 'max': 1300.0}, # Slightly elevated but acceptable
    'unsatisfactory': {'min': 1300.0, 'max': 1450.0}, # High speed - monitor closely
    'unacceptable': {'min': 1450.0, 'max': 5000.0}    # Dangerous overspeed
}

# COMBINED THRESHOLDS FOR EASY ACCESS
# ===================================

ALL_THRESHOLDS = {
    'temperature': TEMP_THRESHOLDS,
    'vibration': VIBRATION_THRESHOLDS,
    'speed': SPEED_THRESHOLDS
}

# INDUSTRY STANDARD CLASSIFICATIONS
# =================================

CONDITION_LEVELS = ['good', 'satisfactory', 'unsatisfactory', 'unacceptable']

# Mapping to user-friendly terms
CONDITION_DESCRIPTIONS = {
    'good': {
        'level': 'good',
        'description': 'Excellent condition - Normal operation',
        'priority': 'low',
        'color': 'green',
        'icon': '✅',
        'action': 'Continue normal operation and routine maintenance'
    },
    'satisfactory': {
        'level': 'satisfactory', 
        'description': 'Satisfactory condition - Monitor closely',
        'priority': 'medium',
        'color': 'yellow',
        'icon': '⚠️',
        'action': 'Increase monitoring frequency, schedule inspection'
    },
    'unsatisfactory': {
        'level': 'unsatisfactory',
        'description': 'Unsatisfactory condition - Restricted operation',
        'priority': 'high',
        'color': 'orange',
        'icon': '🚨',
        'action': 'Reduce load, schedule urgent maintenance within 24-48 hours'
    },
    'unacceptable': {
        'level': 'unacceptable',
        'description': 'Unacceptable condition - Immediate shutdown required',
        'priority': 'critical',
        'color': 'red',
        'icon': '🛑',
        'action': 'Stop machine immediately, perform emergency maintenance'
    }
}

# HELPER FUNCTIONS
# ================

def get_threshold(parameter, level):
    """
    Get threshold range for a specific parameter and level.
    
    Args:
        parameter (str): 'temperature', 'vibration', or 'speed'
        level (str): 'good', 'satisfactory', 'unsatisfactory', or 'unacceptable'
    
    Returns:
        dict: Threshold range with 'min' and 'max' values
    
    Example:
        >>> get_threshold('temperature', 'good')
        {'min': 20.0, 'max': 70.0}
    """
    if parameter not in ALL_THRESHOLDS:
        raise ValueError(f"Unknown parameter: {parameter}. Valid options: {list(ALL_THRESHOLDS.keys())}")
    
    if level not in ALL_THRESHOLDS[parameter]:
        raise ValueError(f"Unknown level: {level}. Valid options: {list(ALL_THRESHOLDS[parameter].keys())}")
    
    return ALL_THRESHOLDS[parameter][level]

def check_threshold_status(parameter, value):
    """
    Check the status of a parameter value against industry standard thresholds.
    
    Args:
        parameter (str): 'temperature', 'vibration', or 'speed'
        value (float): Current value to check
    
    Returns:
        str: 'good', 'satisfactory', 'unsatisfactory', or 'unacceptable'
    
    Example:
        >>> check_threshold_status('temperature', 80.0)
        'satisfactory'
        >>> check_threshold_status('vibration', 6.0)
        'unsatisfactory'
    """
    if parameter not in ALL_THRESHOLDS:
        raise ValueError(f"Unknown parameter: {parameter}")
    
    thresholds = ALL_THRESHOLDS[parameter]
    
    # Check thresholds in order of severity
    for level in CONDITION_LEVELS:
        threshold_range = thresholds[level]
        if threshold_range['min'] <= value < threshold_range['max']:
            return level
    
    # If value exceeds all ranges, return most severe
    return 'unacceptable'

def get_overall_status(temp, vibration, speed):
    """
    Get overall machine status based on all parameters using industry standards.
    
    Args:
        temp (float): Temperature value in °C
        vibration (float): Vibration value in mm/s RMS
        speed (float): Speed value in RPM
    
    Returns:
        dict: Status information with level, description, priority, and details
    
    Example:
        >>> get_overall_status(80.0, 6.0, 1300.0)
        {'level': 'unsatisfactory', 'description': '...', 'priority': 'high', ...}
    """
    temp_status = check_threshold_status('temperature', temp)
    vib_status = check_threshold_status('vibration', vibration)
    speed_status = check_threshold_status('speed', speed)
    
    # Get the highest severity level (worst condition)
    status_priority = {level: i for i, level in enumerate(CONDITION_LEVELS)}
    statuses = [temp_status, vib_status, speed_status]
    highest_status = max(statuses, key=lambda x: status_priority[x])
    
    # Get description for the worst condition
    result = CONDITION_DESCRIPTIONS[highest_status].copy()
    result['details'] = {
        'temperature': {'value': temp, 'status': temp_status, 'unit': '°C'},
        'vibration': {'value': vibration, 'status': vib_status, 'unit': 'mm/s'},
        'speed': {'value': speed, 'status': speed_status, 'unit': 'RPM'}
    }
    
    # Add specific recommendations based on which parameters are problematic
    problem_params = []
    if temp_status in ['unsatisfactory', 'unacceptable']:
        problem_params.append(f"Temperature ({temp:.1f}°C)")
    if vib_status in ['unsatisfactory', 'unacceptable']:
        problem_params.append(f"Vibration ({vibration:.1f} mm/s)")
    if speed_status in ['unsatisfactory', 'unacceptable']:
        problem_params.append(f"Speed ({speed:.0f} RPM)")
    
    if problem_params:
        result['problem_parameters'] = problem_params
        result['detailed_action'] = f"Address issues with: {', '.join(problem_params)}"
    
    return result

# VALIDATION RANGES (for input validation)
# ========================================

VALID_RANGES = {
    'temperature': {'min': -50.0, 'max': 200.0},  # °C - Extended range for industrial applications
    'vibration': {'min': 0.0, 'max': 50.0},       # mm/s RMS - ISO 10816-3 maximum range
    'speed': {'min': 0.0, 'max': 5000.0}          # RPM - Typical industrial motor range
}

def validate_parameter(parameter, value):
    """
    Validate if a parameter value is within acceptable range.
    
    Args:
        parameter (str): 'temperature', 'vibration', or 'speed'
        value (float): Value to validate
    
    Returns:
        bool: True if valid, False otherwise
    
    Example:
        >>> validate_parameter('temperature', 150.0)
        True
        >>> validate_parameter('vibration', 60.0)
        False
    """
    if parameter not in VALID_RANGES:
        return False
    
    range_info = VALID_RANGES[parameter]
    return range_info['min'] <= value <= range_info['max']

# INDUSTRY STANDARD REFERENCES
# ============================

STANDARDS_REFERENCE = {
    'temperature': {
        'standard': 'NEMA MG-1 / IEC 60034-1',
        'description': 'Class B insulation motor temperature limits',
        'notes': 'Based on 40°C ambient + 90°C rise = 130°C maximum hot spot'
    },
    'vibration': {
        'standard': 'ISO 10816-3:2009',
        'description': 'Industrial machinery vibration evaluation',
        'notes': 'For machines >15kW, 120-15000 RPM, rigid foundation, Group 2'
    },
    'speed': {
        'standard': 'Industry Best Practice',
        'description': 'Typical 4-pole, 60Hz industrial motor operation',
        'notes': 'Synchronous speed 1800 RPM, typical load 1150-1200 RPM'
    }
}

def get_standards_info():
    """
    Get information about the industry standards used for thresholds.
    
    Returns:
        dict: Standards reference information
    """
    return STANDARDS_REFERENCE

# EXPORT FOR EASY IMPORTS
# =======================

__all__ = [
    'TEMP_THRESHOLDS',
    'VIBRATION_THRESHOLDS', 
    'SPEED_THRESHOLDS',
    'ALL_THRESHOLDS',
    'CONDITION_LEVELS',
    'CONDITION_DESCRIPTIONS',
    'get_threshold',
    'check_threshold_status',
    'get_overall_status',
    'validate_parameter',
    'get_standards_info',
    'VALID_RANGES',
    'STANDARDS_REFERENCE'
]

if __name__ == "__main__":
    # Test the threshold functions with industry standard values
    print("🧪 Testing Industry Standard Threshold Functions")
    print("=" * 50)
    
    # Display standards information
    print("\n📋 Industry Standards Used:")
    for param, info in STANDARDS_REFERENCE.items():
        print(f"\n{param.upper()}:")
        print(f"  Standard: {info['standard']}")
        print(f"  Description: {info['description']}")
        print(f"  Notes: {info['notes']}")
    
    print("\n" + "=" * 50)
    print("🔍 Threshold Ranges:")
    
    for param in ['temperature', 'vibration', 'speed']:
        print(f"\n{param.upper()} Thresholds:")
        thresholds = ALL_THRESHOLDS[param]
        for level in CONDITION_LEVELS:
            range_info = thresholds[level]
            unit = '°C' if param == 'temperature' else 'mm/s' if param == 'vibration' else 'RPM'
            print(f"  {level.capitalize()}: {range_info['min']}-{range_info['max']} {unit}")
    
    print("\n" + "=" * 50)
    print("🧪 Test Cases:")
    
    # Test cases with realistic industrial values
    test_cases = [
        (65.0, 1.5, 1180.0, "Normal operation"),
        (78.0, 3.2, 1250.0, "Satisfactory - monitor"),
        (92.0, 6.8, 1380.0, "Unsatisfactory - action needed"),
        (115.0, 15.0, 1520.0, "Unacceptable - shutdown")
    ]
    
    for temp, vib, speed, description in test_cases:
        status = get_overall_status(temp, vib, speed)
        print(f"\n{description}:")
        print(f"  Values: T={temp}°C, V={vib}mm/s, S={speed}RPM")
        print(f"  Status: {status['level'].upper()} - {status['description']}")
        print(f"  Priority: {status['priority']}")
        print(f"  Action: {status['action']}")
        if 'problem_parameters' in status:
            print(f"  Issues: {', '.join(status['problem_parameters'])}")
    
    print(f"\n{'=' * 50}")
    print("✅ Industry standard thresholds configured successfully!")