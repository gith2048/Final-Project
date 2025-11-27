# train_models.py
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report

# 1) Load dataset
DATA_PATH = os.path.abspath("../sensor_data_3params.json")
df = pd.read_json(DATA_PATH)

# 2) Clean & sanitize data
df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
df["vibration"]   = pd.to_numeric(df["vibration"], errors="coerce")
df["speed"]       = pd.to_numeric(df["speed"], errors="coerce")

df = df.dropna()
df["temperature"] = df["temperature"].clip(lower=0)
df["vibration"]   = df["vibration"].clip(lower=0)
df["speed"]       = df["speed"].clip(lower=0)

# 3) Auto-generate condition labels (same logic as frontend thresholds)
def classify_row(row):
    score = 0
    if row["temperature"] > 75: score += 1
    if row["vibration"] > 5: score += 1
    if row["speed"] > 1500: score += 1
    return "critical" if score >= 2 else "warning" if score == 1 else "normal"

df["condition"] = df.apply(classify_row, axis=1)

# 4) Features & labels
features = ["temperature", "vibration", "speed"]
X = df[features].values.astype(float)
le = LabelEncoder()
y = le.fit_transform(df["condition"])

# 5) Save label encoder
MODEL_DIR = os.path.abspath(".")
os.makedirs(MODEL_DIR, exist_ok=True)
with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "wb") as f:
    pickle.dump(le, f)
print("✔ label_encoder.pkl saved.")

# 6) Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 7) Scale features with StandardScaler (used for RF & ISO)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

with open(os.path.join(MODEL_DIR, "scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)
print("✔ scaler.pkl saved.")

# 8) Train Random Forest on scaled data
rf = RandomForestClassifier(n_estimators=200, random_state=42)
rf.fit(X_train_scaled, y_train)
with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "wb") as f:
    pickle.dump(rf, f)
print("✔ rf_model.pkl saved.")

# 9) Train Isolation Forest on scaled full X
iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(scaler.transform(X))  # fit on scaled entire dataset
with open(os.path.join(MODEL_DIR, "iso_model.pkl"), "wb") as f:
    pickle.dump(iso, f)
print("✔ iso_model.pkl saved.")

# 10) Evaluation
y_pred = rf.predict(X_test_scaled)
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

print("\n🎉 Training complete.")
