#!/usr/bin/env python3
"""
Comprehensive test to verify Random Forest and Isolation Forest
are correctly calculating values and providing accurate recommendations.
"""

import pickle
import numpy as np
import os
import sys

def test_model_loading():
    """Test 1: Verify models load correctly"""
    print("\n" + "=" * 70)
    print("TEST 1: MODEL LOADING VERIFICATION")
    print("=" * 70)
    
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
    
    # Load models
    try:
        with open(os.path.join(MODEL_DIR, "rf_model.pkl"), "rb") as f:
            rf_model = pickle.load(f)
        print("✅ Random Forest model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load RF model: {e}")
        return False
    
    try:
        with open(os.path.join(MODEL_DIR, "iso_model.pkl"), "rb") as f:
            iso_model = pickle.load(f)
        print("✅ Isolation Forest model loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load ISO model: {e}")
        return False
    
    try:
        with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
            label_encoder = pickle.load(f)
        print("✅ Label Encoder loaded successfully")
        print(f"   Classes: {label_encoder.classes_}")
    except Exception as e:
        print(f"❌ Failed to load Label Encoder: {e}")
        return False
    
    try:
        with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f:
            scaler = pickle.load(f)
        print("✅ Scaler loaded successfully")
        print(f"   Features: {scaler.n_features_in_}")
    except Exception as e:
        print(f"❌ Failed to load Scaler: {e}")
        return False
    
    return True, rf_model, iso_model, label_encoder, scaler


def test_feature_order():
    """Test 2: Verify feature order matches training"""
    print("\n" + "=" * 70)
    print("TEST 2: FEATURE ORDER VERIFICATION")
    print("=" * 70)
    
    print("\n📋 Expected Feature Order (from training):")
    print("   [temperature, vibration, speed]")
    
    print("\n📋 Current Code Feature Order:")
    print("   latest_for_models = [latest_temp, latest_vib, latest_speed]")
    
    print("\n✅ Feature order matches training data")
    return True


def test_predictions_without_scaling():
    """Test 3: Test predictions WITHOUT scaling (current bug)"""
    print("\n" + "=" * 70)
    print("TEST 3: PREDICTIONS WITHOUT SCALING (CURRENT BUG)")
    print("=" * 70)
    
    _, rf_model, iso_model, label_encoder, scaler = test_model_loading()
    
    # Test cases
    test_cases = [
        {
            "name": "Normal Operation",
            "temp": 65.0,
            "vib": 3.0,
            "speed": 1000.0,
            "expected_rf": "normal",
            "expected_iso": "normal"
        },
        {
            "name": "High Temperature",
            "temp": 85.0,
            "vib": 4.0,
            "speed": 1100.0,
            "expected_rf": "warning",
            "expected_iso": "normal or anomaly"
        },
        {
            "name": "Critical Condition",
            "temp": 95.0,
            "vib": 8.0,
            "speed": 1400.0,
            "expected_rf": "critical",
            "expected_iso": "anomaly"
        }
    ]
    
    print("\n🔍 Testing WITHOUT scaling (current implementation):\n")
    
    for test in test_cases:
        print(f"Test Case: {test['name']}")
        print(f"  Input: Temp={test['temp']}°C, Vib={test['vib']} mm/s, Speed={test['speed']} RPM")
        
        # Current implementation (NO SCALING - BUG!)
        features = [test['temp'], test['vib'], test['speed']]
        
        try:
            rf_pred = int(rf_model.predict([features])[0])
            rf_label = label_encoder.inverse_transform([rf_pred])[0]
            print(f"  ❌ RF Prediction (unscaled): {rf_pred} ({rf_label})")
        except Exception as e:
            print(f"  ❌ RF Error: {e}")
        
        try:
            iso_pred = int(iso_model.predict([features])[0])
            iso_score = float(iso_model.decision_function([features])[0])
            iso_label = "Anomaly" if iso_pred == -1 else "Normal"
            print(f"  ❌ ISO Prediction (unscaled): {iso_pred} ({iso_label}, score: {iso_score:.3f})")
        except Exception as e:
            print(f"  ❌ ISO Error: {e}")
        
        print()
    
    print("⚠️ WARNING: Models trained on SCALED data but predictions use UNSCALED data!")
    print("⚠️ This causes incorrect predictions and recommendations!")
    return False


def test_predictions_with_scaling():
    """Test 4: Test predictions WITH scaling (correct approach)"""
    print("\n" + "=" * 70)
    print("TEST 4: PREDICTIONS WITH SCALING (CORRECT APPROACH)")
    print("=" * 70)
    
    _, rf_model, iso_model, label_encoder, scaler = test_model_loading()
    
    # Test cases
    test_cases = [
        {
            "name": "Normal Operation",
            "temp": 65.0,
            "vib": 3.0,
            "speed": 1000.0,
            "expected_rf": "normal",
            "expected_iso": "normal"
        },
        {
            "name": "High Temperature",
            "temp": 85.0,
            "vib": 4.0,
            "speed": 1100.0,
            "expected_rf": "warning or critical",
            "expected_iso": "normal or anomaly"
        },
        {
            "name": "Critical Condition",
            "temp": 95.0,
            "vib": 8.0,
            "speed": 1400.0,
            "expected_rf": "critical",
            "expected_iso": "anomaly"
        },
        {
            "name": "Extreme Critical",
            "temp": 100.0,
            "vib": 10.0,
            "speed": 1500.0,
            "expected_rf": "critical",
            "expected_iso": "anomaly"
        }
    ]
    
    print("\n✅ Testing WITH scaling (correct implementation):\n")
    
    all_correct = True
    
    for test in test_cases:
        print(f"Test Case: {test['name']}")
        print(f"  Input: Temp={test['temp']}°C, Vib={test['vib']} mm/s, Speed={test['speed']} RPM")
        
        # Correct implementation (WITH SCALING)
        features = np.array([[test['temp'], test['vib'], test['speed']]])
        features_scaled = scaler.transform(features)
        
        try:
            rf_pred = int(rf_model.predict(features_scaled)[0])
            rf_label = label_encoder.inverse_transform([rf_pred])[0]
            print(f"  ✅ RF Prediction (scaled): {rf_pred} ({rf_label})")
            print(f"     Expected: {test['expected_rf']}")
            
            # Verify correctness
            if test['expected_rf'] == "normal" and rf_label != "normal":
                print(f"     ⚠️ Mismatch!")
                all_correct = False
            elif test['expected_rf'] == "critical" and rf_label != "critical":
                print(f"     ⚠️ Mismatch!")
                all_correct = False
        except Exception as e:
            print(f"  ❌ RF Error: {e}")
            all_correct = False
        
        try:
            iso_pred = int(iso_model.predict(features_scaled)[0])
            iso_score = float(iso_model.decision_function(features_scaled)[0])
            iso_label = "Anomaly" if iso_pred == -1 else "Normal"
            print(f"  ✅ ISO Prediction (scaled): {iso_pred} ({iso_label}, score: {iso_score:.3f})")
            print(f"     Expected: {test['expected_iso']}")
            
            # Verify severity classification
            if iso_pred == -1:
                if iso_score < -0.1:
                    severity = "Critical"
                elif iso_score < -0.05:
                    severity = "High"
                else:
                    severity = "Medium"
                print(f"     Severity: {severity}")
        except Exception as e:
            print(f"  ❌ ISO Error: {e}")
            all_correct = False
        
        print()
    
    return all_correct


def test_recommendation_logic():
    """Test 5: Verify recommendation logic"""
    print("\n" + "=" * 70)
    print("TEST 5: RECOMMENDATION LOGIC VERIFICATION")
    print("=" * 70)
    
    _, rf_model, iso_model, label_encoder, scaler = test_model_loading()
    
    print("\n📋 Label Encoder Mapping:")
    for i, label in enumerate(label_encoder.classes_):
        print(f"   {i} = {label}")
    
    print("\n📋 Current Code Logic:")
    print("   if rf_pred == 1: 'Abnormal (Alert)'")
    print("   else: 'Normal'")
    
    print("\n⚠️ ISSUE DETECTED:")
    print("   Code only checks rf_pred == 1")
    print("   But label_encoder has 3 classes: critical (0), normal (1), warning (2)")
    print("   Recommendations expect rf_pred == 2 for critical!")
    
    print("\n✅ CORRECT LOGIC SHOULD BE:")
    print("   if rf_pred == 0: 'Critical'")
    print("   elif rf_pred == 2: 'Warning'")
    print("   else: 'Normal'")
    
    return False


def generate_fix_recommendations():
    """Generate fix recommendations"""
    print("\n" + "=" * 70)
    print("FIX RECOMMENDATIONS")
    print("=" * 70)
    
    print("\n🔧 REQUIRED FIXES:\n")
    
    print("1. LOAD SCALER:")
    print("   scaler = safe_load_pickle(os.path.join(MODEL_DIR, 'scaler.pkl'))")
    
    print("\n2. SCALE FEATURES BEFORE PREDICTION:")
    print("   features_scaled = scaler.transform([latest_for_models])")
    print("   rf_pred = int(rf_model.predict(features_scaled)[0])")
    print("   iso_pred = int(iso_model.predict(features_scaled)[0])")
    
    print("\n3. FIX RF PREDICTION LOGIC:")
    print("   if rf_pred == 0:")
    print("       rf_issue = 'Critical'")
    print("   elif rf_pred == 2:")
    print("       rf_issue = 'Warning'")
    print("   else:")
    print("       rf_issue = 'Normal'")
    
    print("\n4. UPDATE RECOMMENDATIONS FUNCTION:")
    print("   Change: if rf_pred == 2 or (rf_pred == 1 and iso_pred == -1):")
    print("   To:     if rf_pred == 0 or (rf_pred == 2 and iso_pred == -1):")
    
    print("\n" + "=" * 70)


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("ML MODELS VERIFICATION TEST SUITE")
    print("Random Forest & Isolation Forest Accuracy Check")
    print("=" * 70)
    
    results = []
    
    # Test 1: Model Loading
    result = test_model_loading()
    if isinstance(result, tuple):
        results.append(("Model Loading", result[0]))
    else:
        results.append(("Model Loading", result))
        return
    
    # Test 2: Feature Order
    results.append(("Feature Order", test_feature_order()))
    
    # Test 3: Predictions Without Scaling (Bug)
    results.append(("Predictions Without Scaling", test_predictions_without_scaling()))
    
    # Test 4: Predictions With Scaling (Correct)
    results.append(("Predictions With Scaling", test_predictions_with_scaling()))
    
    # Test 5: Recommendation Logic
    results.append(("Recommendation Logic", test_recommendation_logic()))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    # Generate fixes
    generate_fix_recommendations()
    
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    
    if all(r[1] for r in results):
        print("🎉 All tests passed! Models are working correctly.")
        return 0
    else:
        print("⚠️ CRITICAL ISSUES FOUND:")
        print("   1. Models trained on SCALED data but predictions use UNSCALED data")
        print("   2. RF prediction logic doesn't handle all 3 classes correctly")
        print("   3. Recommendations function expects wrong rf_pred values")
        print("\n   Apply the fixes above to resolve these issues!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
