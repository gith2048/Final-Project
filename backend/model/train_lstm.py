# train_lstm.py
import pandas as pd
import numpy as np
import os
import pickle
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

DATA_PATH = os.path.abspath("../sensor_data_3params.json")
df = pd.read_json(DATA_PATH)
df = df.sort_values("timestamp")

features = ["temperature", "vibration", "speed"]
data = df[features].astype(float).values

MODEL_DIR = os.path.abspath(".")
os.makedirs(MODEL_DIR, exist_ok=True)

# MinMax scaling for LSTM (fit on whole dataset to keep ranges consistent)
lstm_scaler = MinMaxScaler()
scaled = lstm_scaler.fit_transform(data)

with open(os.path.join(MODEL_DIR, "lstm_scaler.pkl"), "wb") as f:
    pickle.dump(lstm_scaler, f)
print("✔ lstm_scaler.pkl saved.")

# Create sequences
def create_sequences(data, seq_len=10):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])
    return np.array(X), np.array(y)

SEQ_LEN = 10
X, y = create_sequences(scaled, SEQ_LEN)
X = X.reshape((X.shape[0], SEQ_LEN, len(features)))

# Build model
model = Sequential()
model.add(LSTM(64, return_sequences=False, input_shape=(SEQ_LEN, len(features))))
model.add(Dense(32, activation="relu"))
model.add(Dense(len(features)))
model.compile(optimizer="adam", loss="mse")

# Train with validation
model.fit(X, y, epochs=60, batch_size=32, validation_split=0.1, verbose=1)

# Save
model.save(os.path.join(MODEL_DIR, "lstm_model.keras"))
print("✔ lstm_model.keras saved. 🎉 LSTM Training complete.")
