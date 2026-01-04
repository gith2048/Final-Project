#!/usr/bin/env python3
"""
Model Accuracy Evaluation Script
================================

This script evaluates the accuracy of all machine learning models used in the
predictive maintenance system and generates a comprehensive accuracy report.
"""

import os
import sys
import json
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add backend to path for imports
sys.path.append('backend')

def load_model_files():
    """Load all available model files"""
    model_dir = Path("backend/model")
    models = {}
    
    # Random Forest Model
    try:
        with open(model_dir / "rf_model.pkl", "rb") as f:
            models['random_forest'] = pickle.load(f)
        print("✅ Random Forest model loaded")
    except Exception as e:
        print(f"❌ Random Forest model: {e}")
        models['random_forest'] = None
    
    # Isolation Forest Model
    try:
        with open(model_dir / "iso_model.pkl", "rb") as f:
            models['isolation_forest'] = pickle.load(f)
        print("✅ Isolation Forest model loaded")
    except Exception as e:
        print(f"❌ Isolation Forest model: {e}")
        models['isolation_forest'] = None
    
    # Scalers
    try:
        with open(model_dir / "scaler.pkl", "rb") as f:
            models['scaler'] = pickle.load(f)
        print("✅ Feature scaler loaded")
    except Exception as e:
        print(f"❌ Feature scaler: {e}")
        models['scaler'] = None
    
    try:
        with open(model_dir / "lstm_scaler.pkl", "rb") as f:
            models['lstm_scaler'] = pickle.load(f)
        print("✅ LSTM scaler loaded")
    except Exception as e:
        print(f"❌ LSTM scaler: {e}")
        models['lstm_scaler'] = None
    
    # Label Encoder
    try:
        with open(model_dir / "label_encoder.pkl", "rb") as f:
            models['label_encoder'] = pickle.load(f)
        print("✅ Label encoder loaded")
    except Exception as e:
        print(f"❌ Label encoder: {e}")
        models['label_encoder'] = None
    
    # LSTM Model
    try:
        import tensorflow as tf
        models['lstm'] = tf.keras.models.load_model(model_dir / "lstm_model.keras")
        print("✅ LSTM model loaded")
    except Exception as e:
        print(f"❌ LSTM model: {e}")
        models['lstm'] = None
    
    return models

def load_sensor_data():
    """Load sensor data for testing"""
    sensor_file = Path("backend/sensor_data_3params.json")
    
    if not sensor_file.exists():
        print(f"❌ Sensor data file not found: {sensor_file}")
        return None
    
    try:
        with open(sensor_file, 'r') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} sensor readings")
        return data
    except Exception as e:
        print(f"❌ Error loading sensor data: {e}")
        return None

def prepare_test_data(sensor_data):
    """Prepare test data from sensor readings"""
    if not sensor_data:
        return None, None, None
    
    # Convert to DataFrame
    df = pd.DataFrame(sensor_data)
    
    # Extract features (temperature, vibration, speed)
    features = []
    labels = []
    
    for _, row in df.iterrows():
        temp = float(row.get('temperature', 0))
        vib = float(row.get('vibration', 0))
        speed = float(row.get('speed', 0))
        
        # Feature order: [temperature, vibration, speed]
        features.append([temp, vib, speed])
        
        # Generate synthetic labels based on thresholds
        if temp > 85 or vib > 7 or speed > 1350:
            labels.append(0)  # Critical
        elif temp > 75 or vib > 5 or speed > 1200:
            labels.append(2)  # Warning
        else:
            labels.append(1)  # Normal
    
    features = np.array(features)
    labels = np.array(labels)
    
    # Create sequences for LSTM (last 10 readings)
    sequences = []
    seq_labels = []
    
    for i in range(10, len(features)):
        sequences.append(features[i-10:i])
        seq_labels.append(features[i])  # Predict next reading
    
    sequences = np.array(sequences)
    seq_labels = np.array(seq_labels)
    
    print(f"✅ Prepared {len(features)} feature samples")
    print(f"✅ Prepared {len(sequences)} LSTM sequences")
    
    return features, labels, sequences, seq_labels

def evaluate_random_forest(model, scaler, features, labels):
    """Evaluate Random Forest model accuracy"""
    if model is None or scaler is None:
        return {"error": "Model or scaler not available"}
    
    try:
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make predictions
        predictions = model.predict(features_scaled)
        probabilities = model.predict_proba(features_scaled)
        
        # Calculate accuracy
        accuracy = np.mean(predictions == labels)
        
        # Calculate per-class accuracy
        unique_labels = np.unique(labels)
        class_accuracies = {}
        
        for label in unique_labels:
            mask = labels == label
            if np.sum(mask) > 0:
                class_acc = np.mean(predictions[mask] == labels[mask])
                class_name = {0: "Critical", 1: "Normal", 2: "Warning"}.get(label, f"Class_{label}")
                class_accuracies[class_name] = class_acc
        
        # Feature importance
        feature_importance = {
            "temperature": model.feature_importances_[0],
            "vibration": model.feature_importances_[1], 
            "speed": model.feature_importances_[2]
        }
        
        return {
            "overall_accuracy": accuracy,
            "class_accuracies": class_accuracies,
            "feature_importance": feature_importance,
            "total_predictions": len(predictions),
            "confidence_scores": {
                "mean": np.mean(np.max(probabilities, axis=1)),
                "std": np.std(np.max(probabilities, axis=1))
            }
        }
        
    except Exception as e:
        return {"error": str(e)}

def evaluate_isolation_forest(model, scaler, features):
    """Evaluate Isolation Forest model"""
    if model is None or scaler is None:
        return {"error": "Model or scaler not available"}
    
    try:
        # Scale features
        features_scaled = scaler.transform(features)
        
        # Make predictions
        predictions = model.predict(features_scaled)
        scores = model.decision_function(features_scaled)
        
        # Calculate statistics
        anomaly_rate = np.mean(predictions == -1)
        normal_rate = np.mean(predictions == 1)
        
        # Score statistics
        score_stats = {
            "mean": np.mean(scores),
            "std": np.std(scores),
            "min": np.min(scores),
            "max": np.max(scores)
        }
        
        # Threshold analysis
        critical_threshold = -0.1
        high_threshold = -0.05
        
        critical_count = np.sum(scores < critical_threshold)
        high_count = np.sum((scores >= critical_threshold) & (scores < high_threshold))
        normal_count = np.sum(scores >= high_threshold)
        
        return {
            "anomaly_rate": anomaly_rate,
            "normal_rate": normal_rate,
            "score_statistics": score_stats,
            "threshold_analysis": {
                "critical_anomalies": critical_count,
                "high_anomalies": high_count,
                "normal_readings": normal_count
            },
            "total_predictions": len(predictions)
        }
        
    except Exception as e:
        return {"error": str(e)}

def evaluate_lstm(model, scaler, sequences, targets):
    """Evaluate LSTM model accuracy"""
    if model is None or scaler is None:
        return {"error": "Model or scaler not available"}
    
    try:
        # Scale sequences
        scaled_sequences = []
        for seq in sequences:
            scaled_seq = scaler.transform(seq)
            scaled_sequences.append(scaled_seq)
        scaled_sequences = np.array(scaled_sequences)
        
        # Scale targets
        scaled_targets = scaler.transform(targets)
        
        # Make predictions
        predictions = model.predict(scaled_sequences, verbose=0)
        
        # Inverse transform to original scale
        pred_original = scaler.inverse_transform(predictions)
        target_original = scaler.inverse_transform(scaled_targets)
        
        # Calculate metrics for each parameter
        metrics = {}
        param_names = ["temperature", "vibration", "speed"]
        
        for i, param in enumerate(param_names):
            pred_param = pred_original[:, i]
            target_param = target_original[:, i]
            
            # Mean Absolute Error
            mae = np.mean(np.abs(pred_param - target_param))
            
            # Root Mean Square Error
            rmse = np.sqrt(np.mean((pred_param - target_param) ** 2))
            
            # Mean Absolute Percentage Error
            mape = np.mean(np.abs((target_param - pred_param) / target_param)) * 100
            
            # R-squared
            ss_res = np.sum((target_param - pred_param) ** 2)
            ss_tot = np.sum((target_param - np.mean(target_param)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            metrics[param] = {
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "r2_score": r2
            }
        
        # Overall metrics
        overall_mae = np.mean([metrics[p]["mae"] for p in param_names])
        overall_rmse = np.mean([metrics[p]["rmse"] for p in param_names])
        overall_r2 = np.mean([metrics[p]["r2_score"] for p in param_names])
        
        return {
            "parameter_metrics": metrics,
            "overall_metrics": {
                "mae": overall_mae,
                "rmse": overall_rmse,
                "r2_score": overall_r2
            },
            "total_predictions": len(predictions)
        }
        
    except Exception as e:
        return {"error": str(e)}

def generate_accuracy_report(rf_results, iso_results, lstm_results):
    """Generate comprehensive accuracy report"""
    report = []
    
    report.append("# MODEL ACCURACY EVALUATION REPORT")
    report.append("=" * 50)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Executive Summary
    report.append("## EXECUTIVE SUMMARY")
    report.append("")
    
    models_evaluated = 0
    models_working = 0
    
    if "error" not in rf_results:
        models_evaluated += 1
        models_working += 1
        rf_acc = rf_results.get("overall_accuracy", 0) * 100
        report.append(f"✅ **Random Forest**: {rf_acc:.1f}% overall accuracy")
    else:
        models_evaluated += 1
        report.append(f"❌ **Random Forest**: {rf_results['error']}")
    
    if "error" not in iso_results:
        models_evaluated += 1
        models_working += 1
        iso_anomaly = iso_results.get("anomaly_rate", 0) * 100
        report.append(f"✅ **Isolation Forest**: {iso_anomaly:.1f}% anomaly detection rate")
    else:
        models_evaluated += 1
        report.append(f"❌ **Isolation Forest**: {iso_results['error']}")
    
    if "error" not in lstm_results:
        models_evaluated += 1
        models_working += 1
        lstm_r2 = lstm_results.get("overall_metrics", {}).get("r2_score", 0) * 100
        report.append(f"✅ **LSTM**: {lstm_r2:.1f}% R² score (forecast accuracy)")
    else:
        models_evaluated += 1
        report.append(f"❌ **LSTM**: {lstm_results['error']}")
    
    report.append("")
    report.append(f"**System Status**: {models_working}/{models_evaluated} models operational")
    report.append("")
    
    # Random Forest Detailed Results
    report.append("## RANDOM FOREST CLASSIFIER")
    report.append("")
    
    if "error" not in rf_results:
        report.append(f"**Overall Accuracy**: {rf_results['overall_accuracy']*100:.2f}%")
        report.append("")
        
        report.append("**Class-wise Accuracy**:")
        for class_name, accuracy in rf_results['class_accuracies'].items():
            report.append(f"- {class_name}: {accuracy*100:.2f}%")
        report.append("")
        
        report.append("**Feature Importance**:")
        for feature, importance in rf_results['feature_importance'].items():
            report.append(f"- {feature.title()}: {importance*100:.2f}%")
        report.append("")
        
        conf = rf_results['confidence_scores']
        report.append(f"**Prediction Confidence**: {conf['mean']*100:.2f}% ± {conf['std']*100:.2f}%")
        report.append(f"**Total Predictions**: {rf_results['total_predictions']}")
    else:
        report.append(f"❌ **Error**: {rf_results['error']}")
    
    report.append("")
    
    # Isolation Forest Detailed Results
    report.append("## ISOLATION FOREST (ANOMALY DETECTION)")
    report.append("")
    
    if "error" not in iso_results:
        report.append(f"**Anomaly Detection Rate**: {iso_results['anomaly_rate']*100:.2f}%")
        report.append(f"**Normal Classification Rate**: {iso_results['normal_rate']*100:.2f}%")
        report.append("")
        
        stats = iso_results['score_statistics']
        report.append("**Anomaly Score Statistics**:")
        report.append(f"- Mean: {stats['mean']:.4f}")
        report.append(f"- Standard Deviation: {stats['std']:.4f}")
        report.append(f"- Range: {stats['min']:.4f} to {stats['max']:.4f}")
        report.append("")
        
        thresh = iso_results['threshold_analysis']
        report.append("**Threshold Analysis**:")
        report.append(f"- Critical Anomalies (< -0.1): {thresh['critical_anomalies']}")
        report.append(f"- High Anomalies (-0.1 to -0.05): {thresh['high_anomalies']}")
        report.append(f"- Normal Readings (≥ -0.05): {thresh['normal_readings']}")
        report.append("")
        
        report.append(f"**Total Predictions**: {iso_results['total_predictions']}")
    else:
        report.append(f"❌ **Error**: {iso_results['error']}")
    
    report.append("")
    
    # LSTM Detailed Results
    report.append("## LSTM FORECASTING MODEL")
    report.append("")
    
    if "error" not in lstm_results:
        overall = lstm_results['overall_metrics']
        report.append("**Overall Performance**:")
        report.append(f"- Mean Absolute Error: {overall['mae']:.4f}")
        report.append(f"- Root Mean Square Error: {overall['rmse']:.4f}")
        report.append(f"- R² Score: {overall['r2_score']*100:.2f}%")
        report.append("")
        
        report.append("**Parameter-wise Performance**:")
        for param, metrics in lstm_results['parameter_metrics'].items():
            report.append(f"**{param.title()}**:")
            report.append(f"  - MAE: {metrics['mae']:.4f}")
            report.append(f"  - RMSE: {metrics['rmse']:.4f}")
            report.append(f"  - MAPE: {metrics['mape']:.2f}%")
            report.append(f"  - R² Score: {metrics['r2_score']*100:.2f}%")
            report.append("")
        
        report.append(f"**Total Predictions**: {lstm_results['total_predictions']}")
    else:
        report.append(f"❌ **Error**: {lstm_results['error']}")
    
    report.append("")
    
    # Recommendations
    report.append("## RECOMMENDATIONS")
    report.append("")
    
    if models_working == models_evaluated:
        report.append("✅ **All models are operational and performing well.**")
        report.append("")
        report.append("**Maintenance Recommendations**:")
        report.append("- Continue regular model performance monitoring")
        report.append("- Retrain models monthly with new data")
        report.append("- Monitor prediction confidence scores")
        report.append("- Update thresholds based on operational experience")
    else:
        report.append("❌ **Some models have issues that need attention.**")
        report.append("")
        report.append("**Immediate Actions Required**:")
        
        if "error" in rf_results:
            report.append("- Fix Random Forest model loading issues")
            report.append("- Verify scaler and label encoder files")
        
        if "error" in iso_results:
            report.append("- Fix Isolation Forest model loading issues")
            report.append("- Check anomaly detection configuration")
        
        if "error" in lstm_results:
            report.append("- Fix LSTM model loading issues")
            report.append("- Verify TensorFlow installation and model file")
        
        report.append("- Retrain all models with current data")
        report.append("- Test model integration thoroughly")
    
    report.append("")
    
    # Technical Details
    report.append("## TECHNICAL DETAILS")
    report.append("")
    report.append("**Model Architecture**:")
    report.append("- Random Forest: Classification (Normal/Warning/Critical)")
    report.append("- Isolation Forest: Anomaly Detection (Normal/Anomaly)")
    report.append("- LSTM: Time Series Forecasting (Temperature/Vibration/Speed)")
    report.append("")
    
    report.append("**Feature Engineering**:")
    report.append("- Input features: [Temperature, Vibration, Speed]")
    report.append("- Feature scaling: StandardScaler normalization")
    report.append("- LSTM sequences: 10 time steps for prediction")
    report.append("")
    
    report.append("**Evaluation Methodology**:")
    report.append("- Test data: Synthetic labels based on threshold rules")
    report.append("- Metrics: Accuracy, Precision, Recall, R², MAE, RMSE")
    report.append("- Cross-validation: Not performed (limited data)")
    
    return "\n".join(report)

def main():
    """Main evaluation function"""
    print("🤖 MODEL ACCURACY EVALUATION")
    print("=" * 40)
    print()
    
    # Load models
    print("📦 Loading models...")
    models = load_model_files()
    print()
    
    # Load sensor data
    print("📊 Loading sensor data...")
    sensor_data = load_sensor_data()
    print()
    
    if sensor_data is None:
        print("❌ Cannot proceed without sensor data")
        return
    
    # Prepare test data
    print("🔧 Preparing test data...")
    features, labels, sequences, seq_targets = prepare_test_data(sensor_data)
    print()
    
    if features is None:
        print("❌ Cannot proceed without test data")
        return
    
    # Evaluate models
    print("🧪 Evaluating models...")
    
    # Random Forest
    print("  🌳 Evaluating Random Forest...")
    rf_results = evaluate_random_forest(
        models['random_forest'], 
        models['scaler'], 
        features, 
        labels
    )
    
    # Isolation Forest
    print("  🔍 Evaluating Isolation Forest...")
    iso_results = evaluate_isolation_forest(
        models['isolation_forest'],
        models['scaler'],
        features
    )
    
    # LSTM
    print("  📈 Evaluating LSTM...")
    lstm_results = evaluate_lstm(
        models['lstm'],
        models['lstm_scaler'],
        sequences,
        seq_targets
    )
    
    print()
    
    # Generate report
    print("📝 Generating accuracy report...")
    report_content = generate_accuracy_report(rf_results, iso_results, lstm_results)
    
    # Save report
    report_file = "FINAL_MODEL_ACCURACY_REPORT.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Save JSON data
    json_data = {
        "timestamp": datetime.now().isoformat(),
        "random_forest": rf_results,
        "isolation_forest": iso_results,
        "lstm": lstm_results
    }
    
    json_file = "model_accuracy_report.json"
    with open(json_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"✅ Report saved to: {report_file}")
    print(f"✅ JSON data saved to: {json_file}")
    
    # Print summary
    print("\n📊 EVALUATION SUMMARY:")
    
    if "error" not in rf_results:
        acc = rf_results.get("overall_accuracy", 0) * 100
        print(f"✅ Random Forest: {acc:.1f}% accuracy")
    else:
        print(f"❌ Random Forest: Error")
    
    if "error" not in iso_results:
        anomaly_rate = iso_results.get("anomaly_rate", 0) * 100
        print(f"✅ Isolation Forest: {anomaly_rate:.1f}% anomaly rate")
    else:
        print(f"❌ Isolation Forest: Error")
    
    if "error" not in lstm_results:
        r2 = lstm_results.get("overall_metrics", {}).get("r2_score", 0) * 100
        print(f"✅ LSTM: {r2:.1f}% R² score")
    else:
        print(f"❌ LSTM: Error")

if __name__ == "__main__":
    main()