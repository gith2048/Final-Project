#!/usr/bin/env python3
"""Quick test of all models"""

import os
import numpy as np
import pickle
import tensorflow as tf

def test_models():
    print("🧪 Quick Model Test")
    print("="*40)
    
    results = {}
    
    # Test LSTM V2
    try:
        model = tf.keras.models.load_model('lstm_model_v2_best.keras')
        with open('lstm_scaler_v2.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        # Test prediction
        test_seq = np.array([[[50, 3, 1200] for _ in range(10)]])
        scaled_seq = scaler.transform(test_seq.reshape(-1, 3)).reshape(1, 10, 3)
        pred = model.predict(scaled_seq, verbose=0)
        pred_orig = scaler.inverse_transform(pred)[0]
        
        print(f"✅ LSTM V2: Predicts T={pred_orig[0]:.1f}°C, V={pred_orig[1]:.1f}mm/s, S={pred_orig[2]:.0f}RPM")
        results['lstm_v2'] = True
    except Exception as e:
        print(f"❌ LSTM V2 failed: {e}")
        results['lstm_v2'] = False
    
    # Test LSTM V1
    try:
        model = tf.keras.models.load_model('lstm_model.keras')
        with open('lstm_scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        
        test_seq = np.array([[[50, 3, 1200] for _ in range(10)]])
        scaled_seq = scaler.transform(test_seq.reshape(-1, 3)).reshape(1, 10, 3)
        pred = model.predict(scaled_seq, verbose=0)
        pred_orig = scaler.inverse_transform(pred)[0]
        
        print(f"✅ LSTM V1: Predicts T={pred_orig[0]:.1f}°C, V={pred_orig[1]:.1f}mm/s, S={pred_orig[2]:.0f}RPM")
        results['lstm_v1'] = True
    except Exception as e:
        print(f"❌ LSTM V1 failed: {e}")
        results['lstm_v1'] = False
    
    # Test Random Forest (UPDATED for 12 features)
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
        test_features = create_features_array(50, 3, 1200)
        scaled_features = rf_scaler.transform(test_features)
        pred = rf_model.predict(scaled_features)[0]
        condition = label_encoder.inverse_transform([pred])[0]
        
        print(f"✅ Random Forest: Predicts {condition.upper()} condition")
        results['random_forest'] = True
    except Exception as e:
        print(f"❌ Random Forest failed: {e}")
        results['random_forest'] = False
    
    # Test Isolation Forest (UPDATED for 12 features)
    try:
        with open('iso_model.pkl', 'rb') as f:
            iso_model = pickle.load(f)
        
        # Import feature engineering utility
        from feature_utils import create_features_array
        
        # Use 12 engineered features instead of 3
        test_features = create_features_array(50, 3, 1200)
        scaled_features = rf_scaler.transform(test_features)
        pred = iso_model.predict(scaled_features)[0]
        score = iso_model.decision_function(scaled_features)[0]
        status = "ANOMALY" if pred == -1 else "NORMAL"
        
        print(f"✅ Isolation Forest: Predicts {status} (score: {score:.3f})")
        results['isolation_forest'] = True
    except Exception as e:
        print(f"❌ Isolation Forest failed: {e}")
        results['isolation_forest'] = False
    
    print("\n📊 Summary:")
    working = sum(results.values())
    total = len(results)
    print(f"Working models: {working}/{total}")
    
    if working == total:
        print("🎉 All models are working!")
    elif working >= 3:
        print("✅ Most models are working")
    else:
        print("⚠️ Some models need attention")

if __name__ == "__main__":
    test_models()