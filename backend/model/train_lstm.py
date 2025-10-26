import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import pickle

# Load your dataset
df = pd.read_csv("machine_data.csv")
df = df.sort_values("timestamp")

# Focus on temperature
scaler = MinMaxScaler()
scaled_temp = scaler.fit_transform(df[["temperature"]])

# Create sequences
def create_sequences(data, seq_len):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i:i+seq_len])
        y.append(data[i+seq_len])
    return np.array(X), np.array(y)

seq_len = 5
X, y = create_sequences(scaled_temp, seq_len)
X = X.reshape((X.shape[0], X.shape[1], 1))

# Build and train model
model = Sequential()
model.add(LSTM(50, input_shape=(seq_len, 1)))
model.add(Dense(1))
model.compile(optimizer="adam", loss="mse")
model.fit(X, y, epochs=10, batch_size=2)

# Save model and scaler
model.save("model/lstm_model.keras")
with open("model/temp_scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("✅ lstm_model.h5 and temp_scaler.pkl saved successfully.")