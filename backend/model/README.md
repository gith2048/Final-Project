# Model Directory - Essential Files Only

This directory contains only the essential files needed for the predictive maintenance system to function.

## 🚀 Core Training Scripts
- **`train_models.py`** - Main training script for Random Forest and Isolation Forest models (12 features)
- **`train_lstm.py`** - LSTM model training script (3 features)

## 🧠 Trained Models
- **`rf_model.pkl`** - Random Forest classifier (12 features)
- **`iso_model.pkl`** - Isolation Forest anomaly detector (12 features)
- **`lstm_model.keras`** - Main LSTM model (3 features)
- **`lstm_model_v2_best.keras`** - LSTM v2 model (3 features)
- **`lstm_model_smooth_best.keras`** - LSTM smooth model (3 features)

## 🔧 Scalers & Encoders
- **`scaler.pkl`** - StandardScaler for RF/ISO models (12 features)
- **`lstm_scaler.pkl`** - MinMaxScaler for LSTM models (3 features)
- **`lstm_scaler_v2.pkl`** - Scaler for LSTM v2 model
- **`lstm_scaler_smooth.pkl`** - Scaler for LSTM smooth model
- **`label_encoder.pkl`** - Label encoder for RF model outputs

## 🛠️ Utilities
- **`feature_utils.py`** - Essential feature engineering utilities for 12-feature compatibility

## 📁 Additional Models
- **`lstm_saved/`** - Directory containing additional LSTM model variants and scalers

## Usage

### Training New Models
```bash
# Train Random Forest and Isolation Forest models
python train_models.py

# Train LSTM models
python train_lstm.py
```

### Feature Engineering
```python
from feature_utils import create_features_array

# Convert 3 basic features to 12 engineered features
features = create_features_array(temperature, vibration, speed)
```

## Notes
- All test files have been removed to keep only production-ready code
- The system is fully operational with these essential files
- Models are compatible with the backend API endpoints
- Feature engineering is centralized in `feature_utils.py`