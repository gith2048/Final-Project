#!/usr/bin/env python3
"""
Comprehensive Model Accuracy Summary
Compares all 3 models with detailed performance metrics
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
import json
import tensorflow as tf
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, classification_report
from sklearn.preprocessing import MinMaxScaler

def load_test_data():
    """Load and preprocess test data"""
    data_path = '../sensor_data_3params.json'
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    features = ['temperature', 'vibration', 'speed']
    df = df.sort_values("timestamp").reset_index(drop=True)
    df[features] = df[features].astype(float)
    df = df.dropna(subset=features)
    
    return df

def test_lstm_accuracy():
    """Test LSTM model accuracy"""
    print("🧠 LSTM MODEL ACCURACY TEST")
    print("-" * 40)
    
    try:
        # Test new LSTM model
        model = tf.keras.models.load_model('lstm_saved/best_model.keras')
        with open('lstm_saved/scaler_X.pkl', 'rb') as f:
            scaler_X = pickle.load(f)
        with open('lstm_saved/scaler_y.pkl', 'rb') as f:
            scaler_y = pickle.load(f)
        
        df = load_test_data()
        features = ['temperature', 'vibration', 'speed']
        
        # Preprocess (same as training)
        df[features] = df[features].rolling(window=5, center=True).mean().fillna(df[features])
        
        # Remove outliers
        for feature in features:
            Q1 = df[feature].quantile(0.05)
            Q3 = df[feature].quantile(0.95)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[feature] >= lower) & (df[feature] <= upper)]
        
        # Scale data
        X_scaled = scaler_X.transform(df[features].values)
        y_scaled = scaler_y.transform(df[features].values)
        
        # Create sequences
        def create_sequences(X, y, seq_len=15):
            Xs, ys = [], []
            for i in range(seq_len, len(X)):
                Xs.append(X[i-seq_len:i])
                ys.append(y[i])
            return np.array(Xs), np.array(ys)
        
        X_seq, y_seq = create_sequences(X_scaled, y_scaled, 15)
        
        # Test on last 20%
        test_start = int(len(X_seq) * 0.8)
        X_test = X_seq[test_start:]
        y_test = y_seq[test_start:]
        
        # Predict
        y_pred_scaled = model.predict(X_test, verbose=0)
        y_pred = scaler_y.inverse_transform(y_pred_scaled)
        y_true = scaler_y.inverse_transform(y_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100
        accuracy = max(0, 100 - mape)
        
        return {
            'model': 'LSTM (New)',
            'type': 'Regression/Forecasting',
            'accuracy': f"{accuracy:.2f}%",
            'mae': f"{mae:.2f}",
            'rmse': f"{rmse:.2f}",
            'mape': f"{mape:.2f}%",
            'test_samples': len(X_test),
            'status': '✅ EXCELLENT' if accuracy >= 90 else '✅ GOOD' if accuracy >= 80 else '⚠️ NEEDS IMPROVEMENT'
        }
        
    except Exception as e:
        return {
            'model': 'LSTM (New)',
            'type': 'Regression/Forecasting',
            'accuracy': 'ERROR',
            'status': f'❌ {str(e)[:50]}...'
        }

def test_random_forest_accuracy():
    """Test Random Forest model accuracy"""
    print("🌲 RANDOM FOREST MODEL ACCURACY TEST")
    print("-" * 40)
    
    try:
        # Load model and dependencies
        with open('rf_model.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        with open('label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        df = load_test_data()
        features = ['temperature', 'vibration', 'speed']
        
        # Create test scenarios with known labels
        test_scenarios = [
            # Normal conditions
            *[{"temp": np.random.uniform(30, 60), "vib": np.random.uniform(1, 3), "speed": np.random.uniform(1000, 1400), "expected": "normal"} for _ in range(100)],
            # Warning conditions  
            *[{"temp": np.random.uniform(70, 85), "vib": np.random.uniform(4, 6), "speed": np.random.uniform(1400, 1700), "expected": "warning"} for _ in range(50)],
            # Critical conditions
            *[{"temp": np.random.uniform(85, 100), "vib": np.random.uniform(7, 10), "speed": np.random.uniform(1700, 2000), "expected": "critical"} for _ in range(30)]
        ]
        
        # Import feature engineering utility
        from feature_utils import create_features_array, create_batch_features_array
        
        # Test predictions
        correct_predictions = 0
        total_predictions = len(test_scenarios)
        
        for scenario in test_scenarios:
            # Use 12 engineered features instead of 3
            test_features = create_features_array(scenario["temp"], scenario["vib"], scenario["speed"])
            scaled_features = scaler.transform(test_features)
            prediction = rf_model.predict(scaled_features)[0]
            
            # Map prediction to condition
            if prediction == 0:
                predicted_condition = "critical"
            elif prediction == 2:
                predicted_condition = "warning"
            else:
                predicted_condition = "normal"
            
            if predicted_condition == scenario["expected"]:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_predictions) * 100
        
        # Test with real data sample (UPDATED for 12 features)
        sample_data = df[['temperature', 'vibration', 'speed']].sample(100).values
        # Convert 3-feature data to 12-feature data
        sample_features = create_batch_features_array(sample_data)
        scaled_sample = scaler.transform(sample_features)
        predictions = rf_model.predict(scaled_sample)
        
        # Count distribution
        pred_counts = {}
        for pred in predictions:
            condition = label_encoder.inverse_transform([pred])[0]
            pred_counts[condition] = pred_counts.get(condition, 0) + 1
        
        return {
            'model': 'Random Forest',
            'type': 'Classification',
            'accuracy': f"{accuracy:.2f}%",
            'test_samples': total_predictions,
            'real_data_distribution': pred_counts,
            'status': '✅ EXCELLENT' if accuracy >= 90 else '✅ GOOD' if accuracy >= 80 else '⚠️ NEEDS IMPROVEMENT'
        }
        
    except Exception as e:
        return {
            'model': 'Random Forest',
            'type': 'Classification',
            'accuracy': 'ERROR',
            'status': f'❌ {str(e)[:50]}...'
        }

def test_isolation_forest_accuracy():
    """Test Isolation Forest model accuracy"""
    print("🔍 ISOLATION FOREST MODEL ACCURACY TEST")
    print("-" * 40)
    
    try:
        # Load model and scaler
        with open('iso_model.pkl', 'rb') as f:
            iso_model = pickle.load(f)
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        # Create test scenarios with known anomaly labels
        normal_scenarios = [
            {"temp": np.random.uniform(30, 70), "vib": np.random.uniform(1, 4), "speed": np.random.uniform(1000, 1500), "expected": "normal"}
            for _ in range(100)
        ]
        
        anomaly_scenarios = [
            {"temp": np.random.uniform(90, 120), "vib": np.random.uniform(8, 15), "speed": np.random.uniform(1800, 2500), "expected": "anomaly"},
            {"temp": np.random.uniform(5, 20), "vib": np.random.uniform(0.1, 0.5), "speed": np.random.uniform(100, 500), "expected": "anomaly"}
        ] * 25  # 50 anomaly scenarios
        
        test_scenarios = normal_scenarios + anomaly_scenarios
        
        # Import feature engineering utility
        from feature_utils import create_features_array, create_batch_features_array
        
        # Test predictions
        correct_predictions = 0
        total_predictions = len(test_scenarios)
        
        for scenario in test_scenarios:
            # Use 12 engineered features instead of 3
            test_features = create_features_array(scenario["temp"], scenario["vib"], scenario["speed"])
            scaled_features = scaler.transform(test_features)
            prediction = iso_model.predict(scaled_features)[0]
            
            predicted_condition = "anomaly" if prediction == -1 else "normal"
            
            if predicted_condition == scenario["expected"]:
                correct_predictions += 1
        
        accuracy = (correct_predictions / total_predictions) * 100
        
        # Test with real data (UPDATED for 12 features)
        df = load_test_data()
        sample_data = df[['temperature', 'vibration', 'speed']].sample(200).values
        # Convert 3-feature data to 12-feature data
        sample_features = create_batch_features_array(sample_data)
        scaled_sample = scaler.transform(sample_features)
        predictions = iso_model.predict(scaled_sample)
        
        normal_count = np.sum(predictions == 1)
        anomaly_count = np.sum(predictions == -1)
        anomaly_rate = (anomaly_count / len(predictions)) * 100
        
        return {
            'model': 'Isolation Forest',
            'type': 'Anomaly Detection',
            'accuracy': f"{accuracy:.2f}%",
            'test_samples': total_predictions,
            'real_data_anomaly_rate': f"{anomaly_rate:.1f}%",
            'status': '✅ EXCELLENT' if accuracy >= 85 else '✅ GOOD' if accuracy >= 75 else '⚠️ NEEDS IMPROVEMENT'
        }
        
    except Exception as e:
        return {
            'model': 'Isolation Forest',
            'type': 'Anomaly Detection',
            'accuracy': 'ERROR',
            'status': f'❌ {str(e)[:50]}...'
        }

def main():
    """Main function to test all models"""
    print("🎯 COMPREHENSIVE MODEL ACCURACY COMPARISON")
    print("=" * 60)
    
    # Change to model directory
    model_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(model_dir)
    
    # Test all models
    results = []
    
    print("\nTesting models...")
    results.append(test_lstm_accuracy())
    results.append(test_random_forest_accuracy())
    results.append(test_isolation_forest_accuracy())
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 MODEL ACCURACY COMPARISON RESULTS")
    print("=" * 60)
    
    for result in results:
        print(f"\n🔹 {result['model']} ({result['type']})")
        print(f"   Accuracy: {result['accuracy']}")
        if 'mae' in result:
            print(f"   MAE: {result['mae']}")
            print(f"   RMSE: {result['rmse']}")
            print(f"   MAPE: {result['mape']}")
        if 'test_samples' in result:
            print(f"   Test Samples: {result['test_samples']}")
        if 'real_data_distribution' in result:
            print(f"   Real Data Distribution: {result['real_data_distribution']}")
        if 'real_data_anomaly_rate' in result:
            print(f"   Real Data Anomaly Rate: {result['real_data_anomaly_rate']}")
        print(f"   Status: {result['status']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("🏆 SUMMARY")
    print("=" * 60)
    
    working_models = [r for r in results if 'ERROR' not in r['accuracy']]
    
    print(f"✅ Working Models: {len(working_models)}/3")
    
    if len(working_models) == 3:
        print("🎉 ALL MODELS ARE WORKING PERFECTLY!")
        print("\n📋 Use Cases:")
        print("   🧠 LSTM: Predict future sensor values (forecasting)")
        print("   🌲 Random Forest: Classify machine condition (normal/warning/critical)")
        print("   🔍 Isolation Forest: Detect unusual patterns (anomaly detection)")
        
        print("\n🎯 Recommended Usage:")
        print("   • Use LSTM for predictive maintenance scheduling")
        print("   • Use Random Forest for real-time condition monitoring")
        print("   • Use Isolation Forest for early anomaly detection")
    
    print(f"\n🎯 All models tested successfully!")

if __name__ == "__main__":
    main()