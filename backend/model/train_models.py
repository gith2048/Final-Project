import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest, RandomForestClassifier

# Load your dataset
df = pd.read_csv("machine_data.csv")
df = df.sort_values("timestamp")

# Isolation Forest

iso = IsolationForest(contamination=0.1)
iso.fit(df[["temperature", "current", "speed"]])

# Save model
with open("model/iso_model.pkl", "wb") as f:
    pickle.dump(iso, f)

print("✅ iso_model.pkl saved successfully.")


# Random Forest
rf = RandomForestClassifier()
rf.fit(df[["temperature", "current", "speed"]], df["failure_label"])
with open("model/rf_model.pkl", "wb") as f:
    pickle.dump(rf, f)