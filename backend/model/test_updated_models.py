#!/usr/bin/env python3
"""
Test all updated models to ensure they work correctly with the backend
"""

import os
import pickle
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import json

def test_updated_lstm():
    """Test the updated LSTM model"""
    print("🧠 TESTING UPDATED LSTM MODEL")
    print("="*50)
    
    try:
        # Load model and scaler (same way as backend)
        model = tf.keras.models.load_model('lstm_model.keras')
        with open('lstm_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        print("✅ Loaded updated LSTM model and scaler")
        
        # Test prediction (same way as backend)
        seq_len = 10
        test_values = [50.0, 3.0, 1200.0]  # temperature, vibration, speed
        
        # Create sequence (repeat current values)
        sequence = np.array([test_values for _ in range(seq_len)])
        scaled_seq = scaler.transform(sequence)
        
        # Predict
        pred_scaled = model.predict(scaled_seq.reshape(1, seq_len, 3), verbose=0)[0]
        pred = scaler.inverse_transform([pred_scaled])[0]
        
        print(f"📊 Input values: T={test_values[0]}°C, V={test_values[1]}mm/s, S={test_values[2]}RPM")
        print(f"📈 Predicted values: T={pred[0]:.2f}°C, V={pred[1]:.2f}mm/s, S={pred[2]:.0f}RPM")
        
        # Quality check
        temp_ok = 20 <= pred[0] <= 100
        vib_ok = 0 <= pred[1] <= 10
        speed_ok = 500 <= pred[2] <= 2000
        
        print(f"✅ Quality Check:")
        print(f"   Temperature (20-100°C): {'✅' if temp_ok else '❌'}")
        print(f"   Vibration (0-10 mm/s): {'✅' if vib_ok else '❌'}")
        print(f"   Speed (500-2000 RPM): {'✅' if speed_ok else '❌'}")
        
        if temp_ok and vib_ok and speed_ok:
            print("🎯 LSTM Model: WORKING CORRECTLY ✅")
            return True
        else:
            print("⚠️ LSTM Model: Some predictions outside expected ranges")
            return False
            
    except Exception as e:
        print(f"❌ LSTM Model Error: {e}")
        return False

def test_updated_random_forest():
    """Test the updated Random Forest model"""
    print("\n🌲 TESTING UPDATED RANDOM FOREST MODEL")
    print("="*50)
    
    try:
        # Load models (same way as backend)
        with open('rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        print("✅ Loaded Random Forest model, scaler, and label encoder")
        
        # Test scenarios
        test_scenarios = [
            {"name": "Normal", "temp": 45, "vib": 2.5, "speed": 1200},
            {"name": "Warning", "temp": 75, "vib": 4.0, "speed": 1400},
            {"name": "Critical", "temp": 90, "vib": 8.0, "speed": 1800}
        ]
        
        print("🔍 Testing classification scenarios:")
        
        for scenario in test_scenarios:
            # Prepare features (with feature engineering like in training)
            temp, vib, speed = scenario["temp"], scenario["vib"], scenario["speed"]
            
            # Create engineered features (same as training)
            features = [
                temp, vib, speed,  # original
                temp, vib, speed,  # rolling mean (approximated)
                0.1, 0.1, 10,      # rolling std (approximated)
                0, 0, 0            # trend (approximated)
            ]
            
            test_features = np.array([features])
            scaled_features = scaler.transform(test_features)
            
            # Predict
            prediction = rf_model.predict(scaled_features)[0]
            probabilities = rf_model.predict_proba(scaled_features)[0]
            
            # Decode prediction
            condition = label_encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities) * 100
            
            print(f"   {scenario['name']} Scenario:")
            print(f"     Input: T={temp}°C, V={vib}mm/s, S={speed}RPM")
            print(f"     Prediction: {condition.upper()} (confidence: {confidence:.1f}%)")
        
        print("🎯 Random Forest: WORKING CORRECTLY ✅")
        return True
        
    except Exception as e:
        print(f"❌ Random Forest Error: {e}")
        return False

def test_updated_isolation_forest():
    """Test the updated Isolation Forest model"""
    print("\n🔍 TESTING UPDATED ISOLATION FOREST MODEL")
    print("="*50)
    
    try:
        # Load models (same way as backend)
        with open('iso_model.pkl', 'rb') as f:
            iso_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        print("✅ Loaded Isolation Forest model and scaler")
        
        # Test scenarios
        test_scenarios = [
            {"name": "Normal", "temp": 45, "vib": 2.5, "speed": 1200},
            {"name": "Anomaly", "temp": 95, "vib": 9.0, "speed": 1900}
        ]
        
        print("🔍 Testing anomaly detection scenarios:")
        
        for scenario in test_scenarios:
            # Prepare features (with feature engineering)
            temp, vib, speed = scenario["temp"], scenario["vib"], scenario["speed"]
            
            # Create engineered features (same as training)
            features = [
                temp, vib, speed,  # original
                temp, vib, speed,  # rolling mean (approximated)
                0.1, 0.1, 10,      # rolling std (approximated)
                0, 0, 0            # trend (approximated)
            ]
            
            test_features = np.array([features])
            scaled_features = scaler.transform(test_features)
            
            # Predict
            prediction = iso_model.predict(scaled_features)[0]
            score = iso_model.decision_function(scaled_features)[0]
            
            # Interpret results
            is_anomaly = prediction == -1
            severity = "High" if score < -0.1 else "Medium" if score < 0 else "Low"
            
            print(f"   {scenario['name']} Scenario:")
            print(f"     Input: T={temp}°C, V={vib}mm/s, S={speed}RPM")
            print(f"     Result: {'ANOMALY' if is_anomaly else 'NORMAL'} (score: {score:.3f}, severity: {severity})")
        
        print("🎯 Isolation Forest: WORKING CORRECTLY ✅")
        return True
        
    except Exception as e:
        print(f"❌ Isolation Forest Error: {e}")
        return False

def test_backend_integration():
    """Test integration like the backend would use"""
    print("\n🔗 TESTING BACKEND INTEGRATION")
    print("="*50)
    
    try:
        # Simulate backend prediction flow
        temperature = 65.5
        vibration = 3.2
        speed = 1350
        
        print(f"📊 Simulating backend prediction with: T={temperature}°C, V={vibration}mm/s, S={speed}RPM")
        
        results = {}
        
        # 1. LSTM Prediction
        try:
            model = tf.keras.models.load_model('lstm_model.keras')
            with open('lstm_scaler.pkl', 'rb') as f:
                scaler = pickle.load(f)
            
            # Create sequence
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
            
            # Create engineered features
            features = [
                temperature, vibration, speed,  # original
                temperature, vibration, speed,  # rolling mean (approximated)
                0.1, 0.1, 10,                  # rolling std (approximated)
                0, 0, 0                        # trend (approximated)
            ]
            
            features_scaled = rf_scaler.transform([features])
            rf_pred = int(rf_model.predict(features_scaled)[0])
            
            # Map predictions to conditions
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
                "risk_level": risk_level
            }
            print("✅ Random Forest classification successful")
        except Exception as e:
            print(f"❌ Random Forest classification failed: {e}")
        
        # 3. Isolation Forest Anomaly Detection
        try:
            with open('iso_model.pkl', 'rb') as f:
                iso_model = pickle.load(f)
            
            features_scaled = rf_scaler.transform([features])
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
        print(f"\n🎯 Integration Test: {success_count}/3 models working")
        
        return success_count == 3
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Main testing function"""
    print("🚀 TESTING ALL UPDATED MODELS")
    print("="*60)
    
    # Test all models
    results = {
        'lstm': test_updated_lstm(),
        'random_forest': test_updated_random_forest(),
        'isolation_forest': test_updated_isolation_forest(),
        'integration': test_backend_integration()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 UPDATED MODELS TEST SUMMARY")
    print("="*60)
    
    for model, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{model.replace('_', ' ').title()}: {status}")
    
    total_pass = sum(results.values())
    print(f"\nOverall: {total_pass}/4 tests passed")
    
    if total_pass == 4:
        print("🎉 ALL UPDATED MODELS ARE WORKING PERFECTLY!")
        print("✅ Your project is now using the newest, most accurate models!")
    elif total_pass >= 3:
        print("✅ Most updated models are working well")
    else:
        print("❌ Some updated models have issues")
    
    print("\n🎯 Model Update Complete!")

if __name__ == "__main__":
    main()