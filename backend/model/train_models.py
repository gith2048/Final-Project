# train_models.py (Improved High Accuracy)
import os
import pickle
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

# ----------------------------
# SETTINGS
# ----------------------------
DATA_PATH = os.path.abspath("../sensor_data_3params.json")
MODEL_DIR = os.path.abspath(".")
FEATURES = ["temperature", "vibration", "speed"]

os.makedirs(MODEL_DIR, exist_ok=True)

# ----------------------------
# 1) Load dataset
# ----------------------------
df = pd.read_json(DATA_PATH)

# ----------------------------
# 2) Clean & sanitize data
# ----------------------------
for col in FEATURES:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=FEATURES)
df = df.sort_values("timestamp").reset_index(drop=True)

# clip negatives
for col in FEATURES:
    df[col] = df[col].clip(lower=0)

print("✅ Data loaded:", df.shape)

# ----------------------------
# 3) Auto-generate labels (your logic)
# ----------------------------
def classify_row(row):
    score = 0
    if row["temperature"] > 75: score += 1
    if row["vibration"] > 5: score += 1
    if row["speed"] > 1500: score += 1
    return "critical" if score >= 2 else "warning" if score == 1 else "normal"

df["condition"] = df.apply(classify_row, axis=1)

# ----------------------------
# 4) Feature Engineering (VERY IMPORTANT for near 100%)
# ----------------------------
window = 5

for col in FEATURES:
    df[f"{col}_roll_mean"] = df[col].rolling(window).mean()
    df[f"{col}_roll_std"]  = df[col].rolling(window).std()
    df[f"{col}_trend"]     = df[col].diff()

df = df.fillna(method="bfill").fillna(0)

engineered_features = []
for col in FEATURES:
    engineered_features += [
        col,
        f"{col}_roll_mean",
        f"{col}_roll_std",
        f"{col}_trend"
    ]

X = df[engineered_features].values.astype(float)

# ----------------------------
# 5) Encode labels
# ----------------------------
le = LabelEncoder()
y = le.fit_transform(df["condition"])

with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "wb") as f:
    pickle.dump(le, f)
print("✔ label_encoder.pkl saved.")

# ----------------------------
# 6) Train-test split (stratify)
# ----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# ----------------------------
# 7) Scaling
# ----------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

with open(os.path.join(MODEL_DIR, "scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)
print("✔ scaler.pkl saved.")

# ----------------------------
# 8) Class Weights (handles imbalance)
# ----------------------------
classes = np.unique(y_train)
weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
class_weight_dict = {cls: w for cls, w in zip(classes, weights)}

# ----------------------------
# 9) RandomForest Hyperparameter Tuning (near 100%)
# ----------------------------
rf = RandomForestClassifier(random_state=42, n_jobs=-1, class_weight=class_weight_dict)

param_dist = {
    "n_estimators": [200, 300, 500, 800],
    "max_depth": [None, 10, 20, 30, 50],
    "min_samples_split": [2, 4, 6, 10],
    "min_samples_leaf": [1, 2, 4, 6],
    "max_features": ["sqrt", "log2", None],
    "bootstrap": [True, False]
}

search = RandomizedSearchCV(
    rf,
    param_distributions=param_dist,
    n_iter=30,
    scoring="f1_weighted",   # better than accuracy
    cv=3,
    verbose=1,
    random_state=42,
    n_jobs=-1
)

print("\n🚀 Training RandomForest with hyperparameter tuning...")
search.fit(X_train_scaled, y_train)

best_rf = search.best_estimator_
print("\n✅ Best RF Parameters:", search.best_params_)

with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "wb") as f:
    pickle.dump(best_rf, f)
print("✔ rf_model.pkl saved.")

# ----------------------------
# 10) Isolation Forest (calibrated contamination)
# ----------------------------
# better: contamination based on critical %
critical_ratio = (df["condition"] == "critical").mean()
contamination = float(np.clip(critical_ratio, 0.01, 0.10))

iso = IsolationForest(
    contamination=contamination,
    random_state=42,
    n_estimators=300
)

iso.fit(scaler.transform(X))  # use full dataset scaled

with open(os.path.join(MODEL_DIR, "iso_model.pkl"), "wb") as f:
    pickle.dump(iso, f)
print(f"✔ iso_model.pkl saved. (contamination={contamination:.3f})")

# ----------------------------
# 11) Evaluation
# ----------------------------
y_pred = best_rf.predict(X_test_scaled)

print("\n📊 Confusion Matrix:\n")
print(confusion_matrix(y_test, y_pred))

print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

print("\n🎉 Training complete.")
