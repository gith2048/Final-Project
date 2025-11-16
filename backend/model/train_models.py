import pandas as pd
import pickle
import os
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report

# Load JSON dataset
df = pd.read_json("../sensor_data.json")

# Flatten nested 'labels' dictionary
labels_df = pd.json_normalize(df["labels"])
df = pd.concat([df.drop(columns=["labels"]), labels_df], axis=1)

# Remove duplicate columns
df = df.loc[:, ~df.columns.duplicated()]

# Print column names for debugging
print("📋 Cleaned columns in dataset:", df.columns.tolist())

# Keep all 5 sensor features + condition + machine_id
df = df[["temperature", "speed", "vibration", "current", "noise", "condition", "machine_id"]]

# Validate required columns
required_cols = ["temperature", "speed", "vibration", "current", "noise", "condition"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    raise ValueError(f"❌ Missing columns in dataset: {missing}")

# Encode 'speed' if it's categorical
if pd.api.types.is_object_dtype(df["speed"]):
    df["speed_encoded"] = LabelEncoder().fit_transform(df["speed"])
    rf_features = ["temperature", "speed_encoded", "vibration", "current", "noise"]
    iso_features = rf_features
else:
    rf_features = ["temperature", "speed", "vibration", "current", "noise"]
    iso_features = rf_features

# Define absolute model directory path
model_dir = os.path.abspath(os.path.join("..", "model"))
os.makedirs(model_dir, exist_ok=True)

# Isolation Forest (unsupervised anomaly detection)
iso = IsolationForest(contamination=0.1, random_state=42)
iso.fit(df[iso_features])
with open(os.path.join(model_dir, "iso_model.pkl"), "wb") as f:
    pickle.dump(iso, f)
print("✅ iso_model.pkl saved successfully.")

# Encode 'condition' for supervised classification
df["condition_encoded"] = LabelEncoder().fit_transform(df["condition"])

# Prepare features and labels
X = df[rf_features]
y = df["condition_encoded"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Save StandardScaler for backend normalization
scaler = StandardScaler()
scaler.fit(X_train)
with open(os.path.join(model_dir, "multi_scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)
print("✅ multi_scaler.pkl saved successfully.")

# Train Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# Save model
with open(os.path.join(model_dir, "rf_model.pkl"), "wb") as f:
    pickle.dump(rf, f)
print("✅ rf_model.pkl saved successfully.")

# Evaluate model
y_pred = rf.predict(X_test)
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

print("🎉 Model training complete.")