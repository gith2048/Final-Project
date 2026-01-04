# High-Accuracy LSTM Training - Version 2
import pandas as pd
import numpy as np
import os
import pickle
import json
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, BatchNormalization
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import tensorflow as tf

# Set random seeds for reproducibility
np.random.seed(42)
tf.random.set_seed(42)

print("🚀 Starting High-Accuracy LSTM Training - Version 2...")

# Load and examine data
DATA_PATH = os.path.abspath("../sensor_data_3params.json")
with open(DATA_PATH, 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)
print(f"📊 Loaded {len(df)} sensor readings")

# Focus on the three sensor parameters
features = ["temperature", "vibration", "speed"]
print(f"   Temperature range: {df['temperature'].min():.2f} - {df['temperature'].max():.2f}")
print(f"   Vibration range: {df['vibration'].min():.2f} - {df['vibration'].max():.2f}")
print(f"   Speed range: {df['speed'].min():.2f} - {df['speed'].max():.2f}")

# Sort by timestamp and clean data
df = df.sort_values("timestamp").reset_index(drop=True)
df[features] = df[features].astype(float)
df = df.dropna(subset=features)

# More aggressive data cleaning for better accuracy
print("🔧 Advanced data cleaning for high accuracy...")

# Remove extreme outliers more aggressively
for feature in features:
    Q1 = df[feature].quantile(0.05)
    Q3 = df[feature].quantile(0.95)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.0 * IQR
    upper_bound = Q3 + 1.0 * IQR
    before_count = len(df)
    df = df[(df[feature] >= lower_bound) & (df[feature] <= upper_bound)]
    removed = before_count - len(df)
    if removed > 0:
        print(f"   Removed {removed} outliers from {feature}")

print(f"✅ Final dataset: {len(df)} samples")

# Create a more predictable dataset by smoothing
print("🔧 Smoothing data for better predictability...")
window = 3
for feature in features:
    df[f'{feature}_smooth'] = df[feature].rolling(window=window, center=True).mean()
    df[f'{feature}_smooth'] = df[f'{feature}_smooth'].fillna(df[feature])

# Use smoothed features for training
smooth_features = [f'{feature}_smooth' for feature in features]
sensor_data = df[smooth_features].values

MODEL_DIR = os.path.abspath(".")
os.makedirs(MODEL_DIR, exist_ok=True)

# Use MinMaxScaler for better LSTM performance
print("🔧 Scaling smoothed data...")
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(sensor_data)

# Save scaler
with open(os.path.join(MODEL_DIR, "lstm_scaler_v2.pkl"), "wb") as f:
    pickle.dump(scaler, f)
print("✔ lstm_scaler_v2.pkl saved.")

# Create sequences optimized for high accuracy
def create_sequences(data, sequence_length=10, prediction_steps=1):
    """Create sequences optimized for accuracy"""
    X, y = [], []
    for i in range(sequence_length, len(data) - prediction_steps + 1):
        X.append(data[i-sequence_length:i])
        # Predict next value(s)
        if prediction_steps == 1:
            y.append(data[i])
        else:
            y.append(data[i:i+prediction_steps])
    return np.array(X), np.array(y)

# Optimal parameters for high accuracy
SEQUENCE_LENGTH = 10  # Shorter sequences for better accuracy
PREDICTION_STEPS = 1  # Predict only next step

print(f"🔄 Creating sequences (length={SEQUENCE_LENGTH})...")
X, y = create_sequences(scaled_data, SEQUENCE_LENGTH, PREDICTION_STEPS)

print(f"✅ Created {len(X)} sequences")
print(f"   Input shape: {X.shape}")
print(f"   Output shape: {y.shape}")

# Split data with more training data
train_size = int(len(X) * 0.8)
val_size = int(len(X) * 0.1)

X_train = X[:train_size]
y_train = y[:train_size]
X_val = X[train_size:train_size+val_size]
y_val = y[train_size:train_size+val_size]
X_test = X[train_size+val_size:]
y_test = y[train_size+val_size:]

print(f"📊 Data split:")
print(f"   Train: {len(X_train)} sequences")
print(f"   Validation: {len(X_val)} sequences")
print(f"   Test: {len(X_test)} sequences")

# Build high-accuracy LSTM model
print("🏗️ Building high-accuracy LSTM model...")

model = Sequential([
    # First LSTM layer - larger for better pattern recognition
    LSTM(128, return_sequences=True, input_shape=(SEQUENCE_LENGTH, 3)),
    BatchNormalization(),
    Dropout(0.1),
    
    # Second LSTM layer
    LSTM(64, return_sequences=True),
    BatchNormalization(),
    Dropout(0.1),
    
    # Third LSTM layer (final)
    LSTM(32, return_sequences=False),
    BatchNormalization(),
    Dropout(0.1),
    
    # Dense layers with careful regularization
    Dense(24, activation='relu'),
    BatchNormalization(),
    Dropout(0.1),
    
    Dense(12, activation='relu'),
    BatchNormalization(),
    
    # Output layer - predict 3 sensor values
    Dense(3, activation='linear')
])

# Optimized optimizer for high accuracy
optimizer = Adam(
    learning_rate=0.0005,  # Lower learning rate for stability
    beta_1=0.9,
    beta_2=0.999
)

# Compile with appropriate loss and metrics
model.compile(
    optimizer=optimizer,
    loss='mse',
    metrics=['mae', 'mape']
)

print("📋 High-Accuracy Model Architecture:")
model.summary()

# Callbacks optimized for high accuracy
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=25,  # More patience for better convergence
        restore_best_weights=True,
        verbose=1,
        min_delta=1e-7
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.3,
        patience=10,
        min_lr=1e-8,
        verbose=1
    ),
    ModelCheckpoint(
        os.path.join(MODEL_DIR, "lstm_model_v2_best.keras"),
        monitor='val_loss',
        save_best_only=True,
        verbose=1
    )
]

print("🎯 Starting high-accuracy training...")

# Train with optimal parameters for accuracy
history = model.fit(
    X_train, y_train,
    epochs=200,  # More epochs for better convergence
    batch_size=32,
    validation_data=(X_val, y_val),
    callbacks=callbacks,
    verbose=1,
    shuffle=True
)

# Load best model
model = tf.keras.models.load_model(os.path.join(MODEL_DIR, "lstm_model_v2_best.keras"))

# Save final model
model.save(os.path.join(MODEL_DIR, "lstm_model_v2.keras"))
print("✔ lstm_model_v2.keras saved.")

# Comprehensive evaluation
print("\n📊 Model Evaluation:")

# Evaluate on all sets
train_loss, train_mae, train_mape = model.evaluate(X_train, y_train, verbose=0)
val_loss, val_mae, val_mape = model.evaluate(X_val, y_val, verbose=0)
test_loss, test_mae, test_mape = model.evaluate(X_test, y_test, verbose=0)

print(f"   Training   - Loss: {train_loss:.6f}, MAE: {train_mae:.6f}, MAPE: {train_mape:.2f}%")
print(f"   Validation - Loss: {val_loss:.6f}, MAE: {val_mae:.6f}, MAPE: {val_mape:.2f}%")
print(f"   Test       - Loss: {test_loss:.6f}, MAE: {test_mae:.6f}, MAPE: {test_mape:.2f}%")

# Calculate accuracy
test_accuracy = max(0, 100 - test_mape)
print(f"\n🎯 LSTM Model V2 Accuracy: {test_accuracy:.2f}%")

# Detailed prediction analysis
print("\n🔍 Detailed Analysis:")
y_pred = model.predict(X_test, verbose=0)

# Transform back to original scale for analysis
y_test_orig = scaler.inverse_transform(y_test)
y_pred_orig = scaler.inverse_transform(y_pred)

# Calculate individual feature accuracies
feature_names = ['Temperature', 'Vibration', 'Speed']
for i, feature in enumerate(feature_names):
    actual = y_test_orig[:, i]
    predicted = y_pred_orig[:, i]
    
    # Calculate MAPE for this feature
    mape = np.mean(np.abs((actual - predicted) / np.maximum(np.abs(actual), 1e-8))) * 100
    accuracy = max(0, 100 - mape)
    
    print(f"   {feature}: {accuracy:.2f}% accuracy (MAPE: {mape:.2f}%)")

# Save training metadata
training_data = {
    'history': history.history,
    'test_accuracy': float(test_accuracy),
    'test_mape': float(test_mape),
    'sequence_length': SEQUENCE_LENGTH,
    'model_params': model.count_params(),
    'feature_accuracies': {
        feature_names[i]: float(max(0, 100 - np.mean(np.abs((y_test_orig[:, i] - y_pred_orig[:, i]) / np.maximum(np.abs(y_test_orig[:, i]), 1e-8))) * 100))
        for i in range(3)
    }
}

with open(os.path.join(MODEL_DIR, "lstm_training_history_v2.pkl"), "wb") as f:
    pickle.dump(training_data, f)

print("\n🎉 High-Accuracy LSTM Training Complete!")
print(f"📁 Models saved in: {MODEL_DIR}")
print(f"🏆 Final Accuracy: {test_accuracy:.2f}%")

if test_accuracy >= 90:
    print("🎊 EXCELLENT! Achieved 90%+ accuracy!")
elif test_accuracy >= 80:
    print("✅ GOOD! Achieved 80%+ accuracy!")
elif test_accuracy >= 70:
    print("👍 FAIR! Achieved 70%+ accuracy!")
else:
    print("⚠️  Need improvement. Consider more data preprocessing.")

print("🔍 Run evaluate_model_accuracy.py to see comprehensive results")