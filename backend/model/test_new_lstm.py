#!/usr/bin/env python3
"""
Test the newly trained LSTM model from lstm_saved directory
"""

import os
import sys
import numpy as np
import pandas as pd
import pickle
import json
import tensorflow as tf
from sklearn.metrics import mean_squared_error, mean_absolute_error

def test_new_lstm():
    """Test the newly trained LSTM model"""
    print("🧠 TESTING NEWLY TRAINED LSTM MODEL")
    print("="*50)
    
    try:
        # Load the new model and scalers
        model_path = 'lstm_saved/best_model.keras'
        scaler_x_path = 'lstm_saved/scaler_X.pkl'
        scaler_y_path = 'lstm_saved/scaler_y.pkl'
        
        if not all(os.path.exists(p) for p in [model_path, scaler_x_path, scaler_y_path]):
            print("❌ New LSTM model files not found")
            return False
        
        # Load model and scalers
        model = tf.keras.models.load_model(model_path)
        with open(scaler_x_path, 'rb') as f:
            scaler_X = pickle.load(f)
        with open(scaler_y_path, 'rb') as f:
            scaler_y = pickle.load(f)
        
        print("✅ Loaded new LSTM model and scalers")
        
        # Load test data
        data_path = '../sensor_data_3params.json'
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        features = ['temperature', 'vibration', 'speed']
        
        # Prepare test data (same as training)
        df = df.sort_values("timestamp").reset_index(drop=True)
        df[features] = df[features].astype(float)
        df = df.dropna(subset=features)
        
        # Apply same preprocessing as training
        df[features] = df[features].rolling(window=5, center=True).mean().fillna(df[features])
        
        # Remove outliers
        for feature in features:
            Q1 = df[feature].quantile(0.05)
            Q3 = df[feature].quantile(0.95)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[feature] >= lower) & (df[feature] <= upper)]
        
        print(f"✅ Preprocessed {len(df)} data points")
        
        # Scale data
        X_scaled = scaler_X.transform(df[features].values)
        y_scaled = scaler_y.transform(df[features].values)
        
        # Create sequences for testing
        def create_sequences(X, y, seq_len=15):
            Xs, ys = [], []
            for i in range(seq_len, len(X)):
                Xs.append(X[i-seq_len:i])
                ys.append(y[i])
            return np.array(Xs), np.array(ys)
        
        X_seq, y_seq = create_sequences(X_scaled, y_scaled, 15)
        
        # Use last 20% for testing
        test_start = int(len(X_seq) * 0.8)
        X_test = X_seq[test_start:]
        y_test = y_seq[test_start:]
        
        print(f"✅ Created {len(X_test)} test sequences")
        
        # Make predictions
        print("🔮 Making predictions...")
        y_pred_scaled = model.predict(X_test, verbose=0)
        
        # Inverse transform to original scale
        y_pred = scaler_y.inverse_transform(y_pred_scaled)
        y_true = scaler_y.inverse_transform(y_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        
        # Calculate MAPE manually
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100
        accuracy = max(0, 100 - mape)
        
        print("\n📊 NEW LSTM MODEL PERFORMANCE:")
        print(f"✅ MAE (Mean Absolute Error): {mae:.4f}")
        print(f"✅ RMSE (Root Mean Square Error): {rmse:.4f}")
        print(f"✅ MAPE (Mean Absolute Percentage Error): {mape:.2f}%")
        print(f"🎯 ACCURACY: {accuracy:.2f}%")
        
        # Test real-time prediction
        print("\n🔮 Testing real-time prediction...")
        
        # Use last sequence to predict next values
        last_sequence = X_scaled[-15:]
        prediction = model.predict(last_sequence.reshape(1, 15, 3), verbose=0)[0]
        predicted_values = scaler_y.inverse_transform([prediction])[0]
        
        print(f"📈 Next Value Predictions:")
        print(f"   Temperature: {predicted_values[0]:.2f}°C")
        print(f"   Vibration: {predicted_values[1]:.2f} mm/s")
        print(f"   Speed: {predicted_values[2]:.0f} RPM")
        
        # Quality check
        temp_ok = 20 <= predicted_values[0] <= 100
        vib_ok = 0 <= predicted_values[1] <= 10
        speed_ok = 500 <= predicted_values[2] <= 2000
        
        print(f"\n✅ Prediction Quality Check:")
        print(f"   Temperature range (20-100°C): {'✅' if temp_ok else '❌'}")
        print(f"   Vibration range (0-10 mm/s): {'✅' if vib_ok else '❌'}")
        print(f"   Speed range (500-2000 RPM): {'✅' if speed_ok else '❌'}")
        
        # Overall assessment
        if accuracy >= 90 and temp_ok and vib_ok and speed_ok:
            print(f"\n🎉 NEW LSTM MODEL: EXCELLENT PERFORMANCE! ({accuracy:.2f}% accuracy)")
            return True
        elif accuracy >= 80:
            print(f"\n✅ NEW LSTM MODEL: GOOD PERFORMANCE ({accuracy:.2f}% accuracy)")
            return True
        else:
            print(f"\n⚠️ NEW LSTM MODEL: NEEDS IMPROVEMENT ({accuracy:.2f}% accuracy)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing new LSTM model: {e}")
        return False

if __name__ == "__main__":
    test_new_lstm()