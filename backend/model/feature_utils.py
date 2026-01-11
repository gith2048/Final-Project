#!/usr/bin/env python3
"""
Feature Engineering Utilities
============================

This module provides consistent feature engineering functions for all model testing
and prediction scripts to ensure compatibility with the 12-feature trained models.
"""

import numpy as np

def create_engineered_features(temperature, vibration, speed):
    """
    Create 12 engineered features from 3 basic sensor values to match training data.
    
    Args:
        temperature (float): Temperature in Celsius
        vibration (float): Vibration in mm/s
        speed (float): Speed in RPM
    
    Returns:
        list: 12 engineered features in the same order as training:
              [temp, temp_roll_mean, temp_roll_std, temp_trend,
               vib, vib_roll_mean, vib_roll_std, vib_trend,
               speed, speed_roll_mean, speed_roll_std, speed_trend]
    """
    # Basic features
    temp_val = float(temperature)
    vib_val = float(vibration) 
    speed_val = float(speed)
    
    # Engineered features (using current values as approximations)
    # In a real system, these would be calculated from historical data
    temp_roll_mean = temp_val  # Approximate rolling mean as current value
    temp_roll_std = 0.1  # Small std deviation as default
    temp_trend = 0.0  # No trend information available
    
    vib_roll_mean = vib_val
    vib_roll_std = 0.1
    vib_trend = 0.0
    
    speed_roll_mean = speed_val
    speed_roll_std = 1.0  # Slightly higher std for speed
    speed_trend = 0.0
    
    # Return 12 features in the same order as training
    return [
        temp_val, temp_roll_mean, temp_roll_std, temp_trend,
        vib_val, vib_roll_mean, vib_roll_std, vib_trend,
        speed_val, speed_roll_mean, speed_roll_std, speed_trend
    ]

def create_features_array(temperature, vibration, speed):
    """
    Create a numpy array of engineered features ready for model prediction.
    
    Args:
        temperature (float): Temperature in Celsius
        vibration (float): Vibration in mm/s
        speed (float): Speed in RPM
    
    Returns:
        numpy.ndarray: Shape (1, 12) array ready for scaler.transform()
    """
    features = create_engineered_features(temperature, vibration, speed)
    return np.array([features])

def create_batch_features_array(sensor_data):
    """
    Create engineered features for multiple sensor readings.
    
    Args:
        sensor_data (list): List of [temperature, vibration, speed] arrays
    
    Returns:
        numpy.ndarray: Shape (n, 12) array ready for scaler.transform()
    """
    batch_features = []
    for temp, vib, speed in sensor_data:
        features = create_engineered_features(temp, vib, speed)
        batch_features.append(features)
    return np.array(batch_features)

# For backward compatibility
def get_feature_names():
    """
    Get the names of all 12 engineered features.
    
    Returns:
        list: Feature names in order
    """
    return [
        'temperature', 'temperature_roll_mean', 'temperature_roll_std', 'temperature_trend',
        'vibration', 'vibration_roll_mean', 'vibration_roll_std', 'vibration_trend',
        'speed', 'speed_roll_mean', 'speed_roll_std', 'speed_trend'
    ]

if __name__ == "__main__":
    # Test the feature engineering
    print("🧪 Testing Feature Engineering Utilities")
    print("=" * 50)
    
    # Test single feature creation
    temp, vib, speed = 75.0, 5.0, 1200.0
    features = create_engineered_features(temp, vib, speed)
    
    print(f"Input: T={temp}°C, V={vib}mm/s, S={speed}RPM")
    print(f"Output: {len(features)} features")
    print(f"Features: {features}")
    
    # Test array creation
    features_array = create_features_array(temp, vib, speed)
    print(f"Array shape: {features_array.shape}")
    
    # Test batch creation
    batch_data = [[70, 4, 1100], [80, 6, 1300], [90, 8, 1500]]
    batch_features = create_batch_features_array(batch_data)
    print(f"Batch shape: {batch_features.shape}")
    
    print("✅ Feature engineering utilities working correctly!")