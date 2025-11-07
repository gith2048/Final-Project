import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import pickle

# Load JSON dataset
df = pd.read_json("../sensor_data.json")
df = df.sort_values("timestamp")

# Select only 3 features
features = ["temperature", "speed", "vibration"]
data = df[features]

# Scale features
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(data)

# Create sequences
def create_sequences(data, seq_len):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])  # Predict next 3-feature vector
    return np.array(X), np.array(y)

seq_len = 5
X, y = create_sequences(scaled_data, seq_len)

# Reshape for LSTM: (samples, timesteps, features)
X = X.reshape((X.shape[0], seq_len, len(features)))

# Build and train model
model = Sequential()
model.add(LSTM(64, input_shape=(seq_len, len(features))))
model.add(Dense(len(features)))  # Output: temperature, speed, vibration
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=10, batch_size=32)

# Save model and scaler
model.save("model/lstm_model.keras")
with open("model/multi_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("✅ lstm_model.keras and multi_scaler.pkl saved successfully.")