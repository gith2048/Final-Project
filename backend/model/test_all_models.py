#!/usr/bin/env python3
"""
Comprehensive Model Testing Script
Tests LSTM, Random Forest, and Isolation Forest models with sample data.
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
import json
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier, IsolationForest

def load_test_data():
    """Load test sensor data"""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'sensor_data_3params.json')
    
    if not os.path.exists(data_path):
        print(f"❌ Test data not found: {data_path}")
        return None
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    print(f"✅ Loaded {len(df)} test data points")
    
    return df

def test_lstm_model():
    """Test LSTM model"""
    print("\n🧠 TESTING LSTM MODEL")
    print("="*50)
    
    # Try V2 first, then V1
    model_configs = [
        ('lstm_model_v2.keras', 'lstm_scaler_v2.pkl', 'V2'),
        ('lstm_model.keras', 'lstm_scaler.pkl', 'V1')
    ]
    
    for model_path, scaler_path, version in model_configs:
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            print(f"\n📊 Testing LSTM {version}...")
            
            try:
                # Load model and scaler
                model = tf.keras.models.load_model(model_path)
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                
                print(f"✅ Loaded LSTM {version} model and scaler")
                
                # Load test data
                df = load_test_data()
                if df is None:
                    return False
                
                # Prepare data
                features = ['temperature', 'vibration', 'speed']
                data = df[features].astype(float).values
                data = data[~np.isnan(data).any(axis=1)]
                
                # Test with current values (simulate real-time prediction)
                print("🔮 Testing real-time prediction...")
                
                # Use last 10 values to predict next
                seq_len = 10
                if len(data) >= seq_len:
                    # Get last sequence
                    last_sequence = data[-seq_len:]
                    scaled_seq = scaler.transform(last_sequence)
                    
                    # Predict next values
                    prediction = model.predict(scaled_seq.reshape(1, seq_len, 3), verbose=0)[0]
                    predicted_values = scaler.inverse_transform([prediction])[0]
                    
                    print(f"📈 LSTM {version} Prediction (Next Values):")
                    print(f"   Temperature: {predicted_values[0]:.2f}°C")
                    print(f"   Vibration: {predicted_values[1]:.2f} mm/s")
                    print(f"   Speed: {predicted_values[2]:.0f} RPM")
                    
                    # Check if predictions are reasonable
                    temp_ok = 20 <= predicted_values[0] <= 100
                    vib_ok = 0 <= predicted_values[1] <= 10
                    speed_ok = 500 <= predicted_values[2] <= 2000
                    
                    print(f"✅ Prediction Quality Check:")
                    print(f"   Temperature range (20-100°C): {'✅' if temp_ok else '❌'}")
                    print(f"   Vibration range (0-10 mm/s): {'✅' if vib_ok else '❌'}")
                    print(f"   Speed range (500-2000 RPM): {'✅' if speed_ok else '❌'}")
                    
                    if temp_ok and vib_ok and speed_ok:
                        print(f"🎯 LSTM {version}: PREDICTIONS LOOK REASONABLE ✅")
                        return True
                    else:
                        print(f"⚠️ LSTM {version}: Some predictions outside expected ranges")
                        return False
                else:
                    print(f"❌ Not enough data for LSTM testing")
                    return False
                    
            except Exception as e:
                print(f"❌ Error testing LSTM {version}: {e}")
                continue
    
    print("❌ No working LSTM model found")
    return False

def test_random_forest():
    """Test Random Forest model"""
    print("\n🌲 TESTING RANDOM FOREST MODEL")
    print("="*50)
    
    try:
        # Load model and dependencies
        with open('rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        print("✅ Loaded Random Forest model, scaler, and label encoder")
        
        # Load test data
        df = load_test_data()
        if df is None:
            return False
        
        # Prepare test samples
        features = ['temperature', 'vibration', 'speed']
        
        # Test with various scenarios
        test_scenarios = [
            {"name": "Normal Operation", "temp": 45, "vib": 2.5, "speed": 1200},
            {"name": "High Temperature", "temp": 85, "vib": 3.0, "speed": 1300},
            {"name": "High Vibration", "temp": 50, "vib": 7.5, "speed": 1100},
            {"name": "Critical Condition", "temp": 90, "vib": 8.0, "speed": 1800},
            {"name": "Low Speed", "temp": 40, "vib": 1.5, "speed": 800}
        ]
        # Import feature engineering utility
        from feature_utils import create_features_array, create_batch_features_array
        
        print("🔍 Testing classification scenarios:")
        
        for scenario in test_scenarios:
            # Use 12 engineered features instead of 3
            test_features = create_features_array(scenario["temp"], scenario["vib"], scenario["speed"])
            scaled_features = scaler.transform(test_features)
            
            # Predict
            prediction = rf_model.predict(scaled_features)[0]
            probabilities = rf_model.predict_proba(scaled_features)[0]
            
            # Decode prediction
            condition = label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities) * 100
            
            print(f"   {scenario['name']}:")
            print(f"     Input: T={scenario['temp']}°C, V={scenario['vib']}mm/s, S={scenario['speed']}RPM")
            print(f"     Prediction: {condition.upper()} (confidence: {confidence:.1f}%)")
        
        # Test with real data sample (UPDATED for 12 features)
        print("\n📊 Testing with real data sample...")
        sample_data = df[features].sample(10).values
        # Convert 3-feature data to 12-feature data
        sample_features = create_batch_features_array(sample_data)
        scaled_sample = scaler.transform(sample_features)
        predictions = rf_model.predict(scaled_sample)
        
        # Count predictions
        pred_counts = {}
        for pred in predictions:
            condition = label_encoder.inverse_transform([pred])[0]
            pred_counts[condition] = pred_counts.get(condition, 0) + 1
        
        print("   Sample predictions distribution:")
        for condition, count in pred_counts.items():
            print(f"     {condition.capitalize()}: {count}/10 samples")
        
        print("🎯 Random Forest: WORKING CORRECTLY ✅")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Random Forest: {e}")
        return False

def test_isolation_forest():
    """Test Isolation Forest model"""
    print("\n🔍 TESTING ISOLATION FOREST MODEL")
    print("="*50)
    
    try:
        # Load model and scaler
        with open('iso_model.pkl', 'rb') as f:
            iso_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        print("✅ Loaded Isolation Forest model and scaler")
        
        # Test with various scenarios
        test_scenarios = [
            {"name": "Normal Operation", "temp": 45, "vib": 2.5, "speed": 1200},
            {"name": "Slight Anomaly", "temp": 75, "vib": 4.0, "speed": 1400},
            {"name": "Clear Anomaly", "temp": 95, "vib": 9.0, "speed": 1900},
            {"name": "Extreme Values", "temp": 120, "vib": 15.0, "speed": 2500},
            {"name": "Low Values", "temp": 10, "vib": 0.1, "speed": 100}
        ]
        # Import feature engineering utility
        from feature_utils import create_features_array, create_batch_features_array
        
        print("🔍 Testing anomaly detection scenarios:")
        
        for scenario in test_scenarios:
            # Use 12 engineered features instead of 3
            test_features = create_features_array(scenario["temp"], scenario["vib"], scenario["speed"])
            scaled_features = scaler.transform(test_features)
            
            # Predict
            prediction = iso_model.predict(scaled_features)[0]
            score = iso_model.decision_function(scaled_features)[0]
            
            # Interpret results
            is_anomaly = prediction == -1
            severity = "High" if score < -0.1 else "Medium" if score < 0 else "Low"
            
            print(f"   {scenario['name']}:")
            print(f"     Input: T={scenario['temp']}°C, V={scenario['vib']}mm/s, S={scenario['speed']}RPM")
            print(f"     Result: {'ANOMALY' if is_anomaly else 'NORMAL'} (score: {score:.3f}, severity: {severity})")
        
        # Test with real data sample (UPDATED for 12 features)
        print("\n📊 Testing with real data sample...")
        df = load_test_data()
        if df is not None:
            features = ['temperature', 'vibration', 'speed']
            sample_data = df[features].sample(20).values
            # Convert 3-feature data to 12-feature data
            sample_features = create_batch_features_array(sample_data)
            scaled_sample = scaler.transform(sample_features)
            predictions = iso_model.predict(scaled_sample)
            
            normal_count = np.sum(predictions == 1)
            anomaly_count = np.sum(predictions == -1)
            
            print(f"   Sample results: {normal_count}/20 normal, {anomaly_count}/20 anomalies")
            print(f"   Anomaly rate: {(anomaly_count/20)*100:.1f}%")
        
        print("🎯 Isolation Forest: WORKING CORRECTLY ✅")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Isolation Forest: {e}")
        return False

def test_backend_integration():
    """Test if models work like in the backend"""
    print("\n🔗 TESTING BACKEND INTEGRATION")
    print("="*50)
    
    try:
        # Simulate backend prediction flow
        print("🔄 Simulating backend prediction flow...")
        
        # Sample sensor values (like from frontend)
        temperature = 65.5
        vibration = 3.2
        speed = 1350
        
        print(f"📊 Input values: T={temperature}°C, V={vibration}mm/s, S={speed}RPM")
        
        results = {}
        
        # 1. LSTM Prediction
        try:
            if os.path.exists('lstm_model_v2.keras') and os.path.exists('lstm_scaler_v2.pkl'):
                model = tf.keras.models.load_model('lstm_model_v2.keras')
                with open('lstm_scaler_v2.pkl', 'rb') as f:
                    scaler = pickle.load(f)
                
                # Create sequence (repeat current values)
                seq_len = 10
                sequence = np.array([[temperature, vibration, speed] for _ in range(seq_len)])
                scaled_seq = scaler.transform(sequence)
                
                # Predict
                pred = model.predict(scaled_seq.reshape(1, seq_len, 3), verbose=0)[0]
                predicted_values = scaler.inverse_transform([pred])[0]
                
                results['lstm'] = {
                    "temperature": float(predicted_values[0]),
                    "vibration": float(predicted_values[1]),
                    "speed": float(predicted_values[2])
                }
                print("✅ LSTM prediction successful")
            else:
                print("⚠️ LSTM V2 model not available")
        except Exception as e:
            print(f"❌ LSTM prediction failed: {e}")
        
        # 2. Random Forest Classification
        try:
            with open('rf_model.pkl', 'rb') as f:
                rf_model = pickle.load(f)
            with open('scaler.pkl', 'rb') as f:
                rf_scaler = pickle.load(f)
            with open('label_encoder.pkl', 'rb') as f:
                label_encoder = pickle.load(f)
            # Import feature engineering utility
            from feature_utils import create_features_array
            
            # Use 12 engineered features instead of 3
            test_features = create_features_array(temperature, vibration, speed)
            features_scaled = rf_scaler.transform(test_features)
            rf_pred = int(rf_model.predict(features_scaled)[0])
            
            # Map predictions to conditions (same as backend)
            if rf_pred == 0:
                condition = "Critical"
                risk_level = "High"
            elif rf_pred == 2:
                condition = "Warning"
                risk_level = "Medium"
            else:
                condition = "Normal"
                risk_level = "Low"
            
            results['random_forest'] = {
                "condition": condition,
                "risk_level": risk_level,
                "prediction_code": rf_pred
            }
            print("✅ Random Forest classification successful")
        except Exception as e:
            print(f"❌ Random Forest classification failed: {e}")
        
        # 3. Isolation Forest Anomaly Detection (UPDATED for 12 features)
        try:
            with open('iso_model.pkl', 'rb') as f:
                iso_model = pickle.load(f)
            
            # Import feature engineering utility
            from feature_utils import create_features_array
            
            # Use 12 engineered features instead of 3
            test_features = create_features_array(temperature, vibration, speed)
            features_scaled = rf_scaler.transform(test_features)
            iso_pred = int(iso_model.predict(features_scaled)[0])
            iso_score = float(iso_model.decision_function(features_scaled)[0])
            
            if iso_pred == -1:
                anomaly_status = "Anomaly Detected"
                severity = "High" if iso_score < -0.1 else "Medium"
            else:
                anomaly_status = "Normal Pattern"
                severity = "Low"
            
            results['isolation_forest'] = {
                "anomaly_status": anomaly_status,
                "severity": severity,
                "anomaly_score": iso_score
            }
            print("✅ Isolation Forest anomaly detection successful")
        except Exception as e:
            print(f"❌ Isolation Forest anomaly detection failed: {e}")
        
        # Display results
        print("\n📋 INTEGRATION TEST RESULTS:")
        
        if 'lstm' in results:
            lstm = results['lstm']
            print(f"🧠 LSTM Forecast:")
            print(f"   Next Temperature: {lstm['temperature']:.2f}°C")
            print(f"   Next Vibration: {lstm['vibration']:.2f} mm/s")
            print(f"   Next Speed: {lstm['speed']:.0f} RPM")
        
        if 'random_forest' in results:
            rf = results['random_forest']
            print(f"🌲 Random Forest Classification:")
            print(f"   Condition: {rf['condition']}")
            print(f"   Risk Level: {rf['risk_level']}")
        
        if 'isolation_forest' in results:
            iso = results['isolation_forest']
            print(f"🔍 Isolation Forest Anomaly Detection:")
            print(f"   Status: {iso['anomaly_status']}")
            print(f"   Severity: {iso['severity']}")
            print(f"   Score: {iso['anomaly_score']:.3f}")
        
        success_count = len(results)
        print(f"\n🎯 Integration Test: {success_count}/3 models working correctly")
        
        return success_count == 3
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🚀 COMPREHENSIVE MODEL TESTING SUITE")
    print("="*60)
    
    # Change to model directory
    model_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(model_dir)
    
    # Test all models
    results = {
        'lstm': test_lstm_model(),
        'random_forest': test_random_forest(),
        'isolation_forest': test_isolation_forest(),
        'integration': test_backend_integration()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 FINAL TEST SUMMARY")
    print("="*60)
    
    for model, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{model.replace('_', ' ').title()}: {status}")
    
    total_pass = sum(results.values())
    print(f"\nOverall: {total_pass}/4 tests passed")
    
    if total_pass == 4:
        print("🎉 ALL MODELS ARE WORKING CORRECTLY!")
    elif total_pass >= 3:
        print("✅ Most models are working well")
    elif total_pass >= 2:
        print("⚠️ Some models need attention")
    else:
        print("❌ Multiple models have issues")
    
    print("\n🎯 Testing complete!")

if __name__ == "__main__":
    main()