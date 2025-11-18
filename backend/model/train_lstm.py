import pandas as pd
import numpy as np
import os
import pickle
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

# -----------------------------
# Load dataset
# -----------------------------
DATA_PATH = os.path.abspath("../sensor_data_3params.json")
df = pd.read_json(DATA_PATH)
df = df.sort_values("timestamp")

# Select 3 features
features = ["temperature", "vibration", "speed"]
data = df[features].values

# -----------------------------
# Scaling
# -----------------------------
scaler = MinMaxScaler()
scaled = scaler.fit_transform(data)

# Save scaler
MODEL_DIR = os.path.abspath(".")
os.makedirs(MODEL_DIR, exist_ok=True)

with open(os.path.join(MODEL_DIR, "lstm_scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)

# -----------------------------
# Create sequences
# -----------------------------
def create_sequences(data, seq_len=10):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])
    return np.array(X), np.array(y)

seq_len = 10
X, y = create_sequences(scaled, seq_len)

# LSTM expects: (samples, timesteps, features)
X = X.reshape((X.shape[0], seq_len, len(features)))

# -----------------------------
# Build LSTM model
# -----------------------------
model = Sequential()
model.add(LSTM(64, return_sequences=False, input_shape=(seq_len, len(features))))
model.add(Dense(len(features)))
model.compile(optimizer="adam", loss="mse")

# -----------------------------
# Train model
# -----------------------------
model.fit(X, y, epochs=10, batch_size=32)

# -----------------------------
# Save model
# -----------------------------
model_path = os.path.join(MODEL_DIR, "lstm_model.keras")
model.save(model_path)

print("✔ lstm_model.keras saved.")
print("🎉 LSTM Training complete.")
