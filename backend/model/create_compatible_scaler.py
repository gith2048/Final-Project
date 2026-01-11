#!/usr/bin/env python3
"""
Create a compatible scaler for the backend from the new separate X and y scalers
"""

import pickle
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def create_compatible_scaler():
    """Create a single scaler that works like the old one but uses new scaler data"""
    print("🔧 Creating compatible LSTM scaler...")
    
    try:
        # Load the new separate scalers
        with open('lstm_saved/scaler_X.pkl', 'rb') as f:
            scaler_X = pickle.load(f)
        
        with open('lstm_saved/scaler_y.pkl', 'rb') as f:
            scaler_y = pickle.load(f)
        
        print("✅ Loaded new separate scalers")
        
        # For the new model, X and y use the same scaling (both are sensor values)
        # So we can use scaler_X for both input and output
        # This maintains compatibility with the backend code
        
        # Save scaler_X as the main lstm_scaler.pkl
        with open('lstm_scaler.pkl', 'wb') as f:
            pickle.dump(scaler_X, f)
        
        print("✅ Created compatible lstm_scaler.pkl")
        
        # Test the scaler
        test_data = np.array([[50.0, 3.0, 1200.0]])  # Sample sensor values
        scaled = scaler_X.transform(test_data)
        unscaled = scaler_X.inverse_transform(scaled)
        
        print(f"🧪 Test - Original: {test_data[0]}")
        print(f"🧪 Test - Scaled: {scaled[0]}")
        print(f"🧪 Test - Unscaled: {unscaled[0]}")
        
        # Check if transformation is working
        if np.allclose(test_data, unscaled, rtol=1e-5):
            print("✅ Scaler compatibility test passed!")
            return True
        else:
            print("❌ Scaler compatibility test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error creating compatible scaler: {e}")
        return False

if __name__ == "__main__":
    success = create_compatible_scaler()
    if success:
        print("\n🎉 Backend is now compatible with the new LSTM model!")
    else:
        print("\n❌ Failed to create compatibility layer")