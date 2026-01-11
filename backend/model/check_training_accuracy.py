#!/usr/bin/env python3
"""
Check the accuracy potential of both training scripts
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, mean_absolute_error, mean_squared_error
from sklearn.utils.class_weight import compute_class_weight

def analyze_train_models_accuracy():
    """Analyze the accuracy potential of train_models.py"""
    print("🌲 ANALYZING TRAIN_MODELS.PY ACCURACY")
    print("="*50)
    
    try:
        # Load data (same as train_models.py)
        data_path = "../sensor_data_3params.json"
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        features = ["temperature", "vibration", "speed"]
        
        # Clean data
        for col in features:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=features)
        df = df.sort_values("timestamp").reset_index(drop=True)
        
        # Clip negatives
        for col in features:
            df[col] = df[col].clip(lower=0)
        
        print(f"✅ Data loaded: {df.shape}")
        
        # Auto-generate labels (same logic as train_models.py)
        def classify_row(row):
            score = 0
            if row["temperature"] > 75: score += 1
            if row["vibration"] > 5: score += 1
            if row["speed"] > 1500: score += 1
            return "critical" if score >= 2 else "warning" if score == 1 else "normal"
        
        df["condition"] = df.apply(classify_row, axis=1)
        
        # Feature Engineering (same as train_models.py)
        window = 5
        for col in features:
            df[f"{col}_roll_mean"] = df[col].rolling(window).mean()
            df[f"{col}_roll_std"] = df[col].rolling(window).std()
            df[f"{col}_trend"] = df[col].diff()
        
        df = df.fillna(method="bfill").fillna(0)
        
        engineered_features = []
        for col in features:
            engineered_features += [
                col,
                f"{col}_roll_mean",
                f"{col}_roll_std",
                f"{col}_trend"
            ]
        
        X = df[engineered_features].values.astype(float)
        
        # Encode labels
        le = LabelEncoder()
        y = le.fit_transform(df["condition"])
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scaling
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Class weights
        classes = np.unique(y_train)
        weights = compute_class_weight(class_weight="balanced", classes=classes, y=y_train)
        class_weight_dict = {cls: w for cls, w in zip(classes, weights)}
        
        # Train a basic RandomForest (without hyperparameter tuning for speed)
        rf = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            random_state=42,
            class_weight=class_weight_dict,
            n_jobs=-1
        )
        
        print("🚀 Training RandomForest...")
        rf.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = rf.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n📊 TRAIN_MODELS.PY RESULTS:")
        print(f"✅ Random Forest Accuracy: {accuracy*100:.2f}%")
        print(f"✅ Features used: {len(engineered_features)} (with feature engineering)")
        print(f"✅ Class distribution: {dict(zip(le.classes_, np.bincount(y)))}")
        
        # Show classification report
        print("\n📋 Classification Report:")
        print(classification_report(y_test, y_pred, target_names=le.classes_))
        
        return accuracy * 100
        
    except Exception as e:
        print(f"❌ Error analyzing train_models.py: {e}")
        return 0

def analyze_train_lstm_accuracy():
    """Analyze the accuracy potential of train_lstm.py"""
    print("\n🧠 ANALYZING TRAIN_LSTM.PY ACCURACY")
    print("="*50)
    
    try:
        # Load data (same as train_lstm.py)
        data_path = "../sensor_data_3params.json"
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        features = ["temperature", "vibration", "speed"]
        
        df = df.sort_values("timestamp").reset_index(drop=True)
        df[features] = df[features].astype(float)
        df = df.dropna(subset=features)
        
        print(f"✅ Data loaded: {df.shape}")
        
        # Outlier removal (same as train_lstm.py)
        for feature in features:
            Q1 = df[feature].quantile(0.05)
            Q3 = df[feature].quantile(0.95)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            df = df[(df[feature] >= lower) & (df[feature] <= upper)]
        
        df = df.reset_index(drop=True)
        print(f"✅ After outlier removal: {df.shape}")
        
        # Smoothing
        df[features] = df[features].rolling(window=5, center=True).mean().fillna(df[features])
        
        # Scale data
        scaler_X = MinMaxScaler()
        X_scaled = scaler_X.fit_transform(df[features].values)
        
        scaler_y = MinMaxScaler()
        y_scaled = scaler_y.fit_transform(df[features].values)
        
        # Create sequences
        def create_sequences(X, y, seq_len=15):
            Xs, ys = [], []
            for i in range(seq_len, len(X)):
                Xs.append(X[i-seq_len:i])
                ys.append(y[i])
            return np.array(Xs), np.array(ys)
        
        X, y = create_sequences(X_scaled, y_scaled, 15)
        print(f"✅ Sequences created: {X.shape}")
        
        # Split data
        total = len(X)
        train_end = int(total * 0.8)
        val_end = int(total * 0.9)
        
        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]
        
        print(f"✅ Data split - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Build a simple LSTM model for testing
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(64, return_sequences=True, input_shape=(15, 3)),
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.LSTM(32, return_sequences=False),
            tf.keras.layers.Dropout(0.1),
            tf.keras.layers.Dense(16, activation="relu"),
            tf.keras.layers.Dense(3, activation="linear")
        ])
        
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss=tf.keras.losses.Huber(),
            metrics=["mae", "mape"]
        )
        
        print("🚀 Training simplified LSTM model...")
        
        # Train for fewer epochs for testing
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=20,  # Reduced for testing
            batch_size=16,
            shuffle=False,
            verbose=0
        )
        
        # Evaluate
        y_pred_scaled = model.predict(X_test, verbose=0)
        y_pred = scaler_y.inverse_transform(y_pred_scaled)
        y_true = scaler_y.inverse_transform(y_test)
        
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100
        accuracy = max(0, 100 - mape)
        
        print(f"\n📊 TRAIN_LSTM.PY RESULTS:")
        print(f"✅ LSTM Accuracy: {accuracy:.2f}%")
        print(f"✅ MAE: {mae:.4f}")
        print(f"✅ RMSE: {rmse:.4f}")
        print(f"✅ MAPE: {mape:.2f}%")
        print(f"✅ Sequence length: 15")
        print(f"✅ Features: {features}")
        
        return accuracy
        
    except Exception as e:
        print(f"❌ Error analyzing train_lstm.py: {e}")
        return 0

def compare_training_approaches():
    """Compare both training approaches"""
    print("\n🎯 TRAINING APPROACH COMPARISON")
    print("="*60)
    
    # Analyze both approaches
    rf_accuracy = analyze_train_models_accuracy()
    lstm_accuracy = analyze_train_lstm_accuracy()
    
    print("\n" + "="*60)
    print("📊 ACCURACY COMPARISON SUMMARY")
    print("="*60)
    
    print(f"🌲 Random Forest (train_models.py): {rf_accuracy:.2f}%")
    print(f"🧠 LSTM (train_lstm.py): {lstm_accuracy:.2f}%")
    
    if lstm_accuracy > rf_accuracy:
        winner = "LSTM"
        difference = lstm_accuracy - rf_accuracy
    else:
        winner = "Random Forest"
        difference = rf_accuracy - lstm_accuracy
    
    print(f"\n🏆 Winner: {winner} (by {difference:.2f}%)")
    
    print("\n📋 Key Differences:")
    print("🌲 train_models.py:")
    print("   • Uses feature engineering (rolling stats, trends)")
    print("   • Hyperparameter tuning with RandomizedSearchCV")
    print("   • Class balancing with weights")
    print("   • Classification task (normal/warning/critical)")
    
    print("\n🧠 train_lstm.py:")
    print("   • Uses time sequences for temporal patterns")
    print("   • Advanced preprocessing (outlier removal, smoothing)")
    print("   • Regression task (predicts actual sensor values)")
    print("   • Better for forecasting future values")
    
    print("\n🎯 Recommendations:")
    if lstm_accuracy >= 90:
        print("✅ LSTM approach is excellent for forecasting")
    if rf_accuracy >= 80:
        print("✅ Random Forest approach is good for classification")
    
    print("\n💡 For near 100% accuracy:")
    print("   • Use both models together (ensemble)")
    print("   • LSTM for forecasting, RF for condition classification")
    print("   • Consider more advanced architectures (Transformer, GRU)")

def main():
    """Main function"""
    print("🔍 CHECKING TRAINING SCRIPT ACCURACY")
    print("="*60)
    
    # Change to model directory
    model_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(model_dir)
    
    compare_training_approaches()
    
    print("\n🎯 Analysis complete!")

if __name__ == "__main__":
    main()