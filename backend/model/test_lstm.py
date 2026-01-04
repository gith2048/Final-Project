#!/usr/bin/env python3
"""
LSTM Model Testing Script
Tests the trained LSTM model with sample data and validates predictions.
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
import json
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def test_lstm_model(model_version='v1'):
    """Test LSTM model with sample data"""
    print(f"🧠 Testing LSTM Model {model_version.upper()}...")
    
    # Load model and scaler
    if model_version == 'v2':
        model_path = 'lstm_model_v2.keras'
        scaler_path = 'lstm_scaler_v2.pkl'
        sequence_length = 10
    else:
        model_path = 'lstm_model.keras'
        scaler_path = 'lstm_scaler.pkl'
        sequence_length = 15
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        return False
    
    if not os.path.exists(scaler_path):
        print(f"❌ Scaler not found: {scaler_path}")
        return False
    
    # Load model
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"✅ Loaded model: {model_path}")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False
    
    # Load scaler
    try:
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        print(f"✅ Loaded scaler: {scaler_path}")
    except Exception as e:
        print(f"❌ Error loading scaler: {e}")
        return False
    
    # Load test data
    df = load_test_data()
    if df is None:
        return False
    
    # Prepare data
    features = ['temperature', 'vibration', 'speed']
    data = df[features].astype(float).values
    
    # Clean data
    data = data[~np.isnan(data).any(axis=1)]
    print(f"✅ Cleaned data: {len(data)} valid samples")
    
    if len(data) < sequence_length + 10:
        print(f"❌ Not enough data for testing (need at least {sequence_length + 10} samples)")
        return False
    
    # Scale data
    scaled_data = scaler.transform(data)
    
    # Create sequences
    def create_sequences(data, seq_len):
        X, y = [], []
        for i in range(seq_len, len(data)):
            X.append(data[i-seq_len:i])
            y.append(data[i])
        return np.array(X), np.array(y)
    
    X, y_true = create_sequences(scaled_data, sequence_length)
    print(f"✅ Created {len(X)} test sequences")
    
    # Make predictions
    print("🔮 Making predictions...")
    y_pred = model.predict(X, verbose=0)
    
    # Transform back to original scale
    y_true_orig = scaler.inverse_transform(y_true)
    y_pred_orig = scaler.inverse_transform(y_pred)
    
    # Calculate metrics
    print("\n📊 Test Results:")
    feature_names = ['Temperature', 'Vibration', 'Speed']
    
    overall_mse = mean_squared_error(y_true_orig, y_pred_orig)
    overall_mae = mean_absolute_error(y_true_orig, y_pred_orig)
    overall_rmse = np.sqrt(overall_mse)
    
    print(f"Overall Metrics:")
    print(f"  MSE: {overall_mse:.6f}")
    print(f"  MAE: {overall_mae:.6f}")
    print(f"  RMSE: {overall_rmse:.6f}")
    
    # Feature-wise metrics
    print(f"\nFeature-wise Performance:")
    mape_scores = []
    
    for i, feature in enumerate(feature_names):
        actual = y_true_orig[:, i]
        predicted = y_pred_orig[:, i]
        
        mse = mean_squared_error(actual, predicted)
        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mse)
        
        # Calculate MAPE
        mask = actual != 0
        if np.sum(mask) > 0:
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        else:
            mape = 100.0
        
        accuracy = max(0, 100 - mape)
        mape_scores.append(mape)
        
        print(f"  {feature}:")
        print(f"    MSE: {mse:.6f}")
        print(f"    MAE: {mae:.6f}")
        print(f"    RMSE: {rmse:.6f}")
        print(f"    MAPE: {mape:.2f}%")
        print(f"    Accuracy: {accuracy:.2f}%")
    
    # Overall accuracy
    avg_mape = np.mean(mape_scores)
    overall_accuracy = max(0, 100 - avg_mape)
    
    print(f"\n🎯 Overall Model Accuracy: {overall_accuracy:.2f}%")
    
    # Sample predictions
    print(f"\n🔍 Sample Predictions (Last 5):")
    print("Actual vs Predicted:")
    for i in range(max(0, len(y_true_orig)-5), len(y_true_orig)):
        actual = y_true_orig[i]
        predicted = y_pred_orig[i]
        print(f"  Sample {i+1}:")
        print(f"    Temp: {actual[0]:.2f} → {predicted[0]:.2f}")
        print(f"    Vib:  {actual[1]:.2f} → {predicted[1]:.2f}")
        print(f"    Speed: {actual[2]:.0f} → {predicted[2]:.0f}")
    
    # Performance assessment
    print(f"\n📈 Performance Assessment:")
    if overall_accuracy >= 90:
        print("  🎊 EXCELLENT! Model performs exceptionally well")
    elif overall_accuracy >= 80:
        print("  ✅ GOOD! Model performs well")
    elif overall_accuracy >= 70:
        print("  👍 FAIR! Model performance is acceptable")
    elif overall_accuracy >= 50:
        print("  ⚠️  POOR! Model needs improvement")
    else:
        print("  ❌ VERY POOR! Model requires significant work")
    
    return True

def compare_models():
    """Compare v1 and v2 LSTM models"""
    print("🔄 Comparing LSTM Model Versions...")
    
    v1_exists = os.path.exists('lstm_model.keras') and os.path.exists('lstm_scaler.pkl')
    v2_exists = os.path.exists('lstm_model_v2.keras') and os.path.exists('lstm_scaler_v2.pkl')
    
    if v1_exists:
        print("\n" + "="*50)
        print("TESTING LSTM V1 MODEL")
        print("="*50)
        test_lstm_model('v1')
    
    if v2_exists:
        print("\n" + "="*50)
        print("TESTING LSTM V2 MODEL")
        print("="*50)
        test_lstm_model('v2')
    
    if v1_exists and v2_exists:
        print("\n" + "="*50)
        print("MODEL COMPARISON SUMMARY")
        print("="*50)
        print("Both models tested successfully!")
        print("Check the results above to compare performance.")
    elif v2_exists:
        print("\n✅ LSTM V2 model tested successfully!")
    elif v1_exists:
        print("\n✅ LSTM V1 model tested successfully!")
    else:
        print("\n❌ No LSTM models found for testing!")

def main():
    """Main testing function"""
    print("🚀 LSTM Model Testing Suite")
    print("="*50)
    
    # Change to model directory
    model_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(model_dir)
    
    # Run tests
    compare_models()
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    main()