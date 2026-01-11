import os
import json
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

# ---------------------------
# SETTINGS
# ---------------------------
DATA_PATH = "../sensor_data_3params.json"
MODEL_DIR = "./lstm_saved"
FEATURES = ["temperature", "vibration", "speed"]
SEQ_LEN = 15
EPOCHS = 100
BATCH_SIZE = 16

np.random.seed(42)
tf.random.set_seed(42)

os.makedirs(MODEL_DIR, exist_ok=True)

print("🚀 Starting Perfect LSTM Training...")


# ---------------------------
# LOAD DATA
# ---------------------------
with open(DATA_PATH, "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df = df.sort_values("timestamp").reset_index(drop=True)
df[FEATURES] = df[FEATURES].astype(float)
df = df.dropna(subset=FEATURES)

print("✅ Data loaded:", df.shape)


# ---------------------------
# OUTLIER REMOVAL (BEFORE SMOOTHING ✅)
# ---------------------------
for feature in FEATURES:
    Q1 = df[feature].quantile(0.05)
    Q3 = df[feature].quantile(0.95)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df = df[(df[feature] >= lower) & (df[feature] <= upper)]

df = df.reset_index(drop=True)
print("✅ After outlier removal:", df.shape)


# ---------------------------
# SMOOTHING (AFTER OUTLIER REMOVAL ✅)
# ---------------------------
df[FEATURES] = df[FEATURES].rolling(window=5, center=True).mean().fillna(df[FEATURES])


# ---------------------------
# SCALE DATA
# ---------------------------
scaler_X = MinMaxScaler()
X_scaled = scaler_X.fit_transform(df[FEATURES].values)

scaler_y = MinMaxScaler()
y_scaled = scaler_y.fit_transform(df[FEATURES].values)

with open(os.path.join(MODEL_DIR, "scaler_X.pkl"), "wb") as f:
    pickle.dump(scaler_X, f)

with open(os.path.join(MODEL_DIR, "scaler_y.pkl"), "wb") as f:
    pickle.dump(scaler_y, f)


# ---------------------------
# CREATE SEQUENCES
# ---------------------------
def create_sequences(X, y, seq_len=15):
    Xs, ys = [], []
    for i in range(seq_len, len(X)):
        Xs.append(X[i - seq_len : i])
        ys.append(y[i])  # predict next step
    return np.array(Xs), np.array(ys)

X, y = create_sequences(X_scaled, y_scaled, SEQ_LEN)
print("✅ Sequence created:", X.shape, y.shape)


# ---------------------------
# TRAIN/VAL/TEST SPLIT
# ---------------------------
total = len(X)
train_end = int(total * 0.8)
val_end = int(total * 0.9)

X_train, y_train = X[:train_end], y[:train_end]
X_val, y_val = X[train_end:val_end], y[train_end:val_end]
X_test, y_test = X[val_end:], y[val_end:]

print("Train:", X_train.shape, " Val:", X_val.shape, " Test:", X_test.shape)


# ---------------------------
# BUILD MODEL
# ---------------------------
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(SEQ_LEN, len(FEATURES))),
    Dropout(0.1),

    LSTM(96, return_sequences=True),
    Dropout(0.1),

    LSTM(64, return_sequences=False),
    Dropout(0.1),

    Dense(48, activation="relu"),
    Dropout(0.05),

    Dense(24, activation="relu"),
    Dense(len(FEATURES), activation="linear")
])

optimizer = tf.keras.optimizers.Adam(
    learning_rate=0.001,
    clipnorm=1.0   # ✅ prevents exploding gradients
)

model.compile(
    optimizer=optimizer,
    loss=tf.keras.losses.Huber(),   # ✅ stable loss (better than mse for sensor spikes)
    metrics=["mae", "mape"]
)

model.summary()


# ---------------------------
# CALLBACKS
# ---------------------------
callbacks = [
    EarlyStopping(
        monitor="val_loss",
        patience=20,
        restore_best_weights=True,
        verbose=1,
        min_delta=1e-6
    ),
    ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.3,
        patience=8,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        os.path.join(MODEL_DIR, "best_model.keras"),
        monitor="val_loss",
        save_best_only=True,
        verbose=1
    )
]


# ---------------------------
# TRAIN
# ---------------------------
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    shuffle=False,  # ✅ time-series should not shuffle
    callbacks=callbacks,
    verbose=1
)

model.save(os.path.join(MODEL_DIR, "final_model.keras"))

# Save history ✅
with open(os.path.join(MODEL_DIR, "history.pkl"), "wb") as f:
    pickle.dump(history.history, f)

print("✅ Training Completed")


# ---------------------------
# EVALUATE
# ---------------------------
best_model = tf.keras.models.load_model(os.path.join(MODEL_DIR, "best_model.keras"))

y_pred_scaled = best_model.predict(X_test, verbose=0)

y_pred = scaler_y.inverse_transform(y_pred_scaled)
y_true = scaler_y.inverse_transform(y_test)

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(mean_squared_error(y_true, y_pred))
mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100

print("\n📌 TEST METRICS (REAL):")
print(f"✅ MAE  : {mae:.4f}")
print(f"✅ RMSE : {rmse:.4f}")
print(f"✅ MAPE : {mape:.2f}%")

print("\n💾 Saved files:")
print("✔ best_model.keras")
print("✔ final_model.keras")
print("✔ scaler_X.pkl")
print("✔ scaler_y.pkl")
print("✔ history.pkl")
print(f"📁 Folder: {MODEL_DIR}")
