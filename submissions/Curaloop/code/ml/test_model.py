#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/zophie/Documents/GitHub/Oct-4-Hackathon-2025-/ml')

from alzheimers_predictor import AlzheimersPredictor
import pandas as pd
import numpy as np

def test_model_loading():
    """Test if the model can be loaded successfully"""
    print("Testing model loading...")

    predictor = AlzheimersPredictor()

    try:
        predictor.load_model(
            model_path='alzheimers_model.joblib',
            scaler_path='alzheimers_scaler.joblib'
        )
        print("✓ Model loaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        return False

def test_prediction_functionality():
    """Test if predictions work with various patient profiles"""
    print("\nTesting prediction functionality...")

    predictor = AlzheimersPredictor()
    predictor.load_model(
        model_path='alzheimers_model.joblib',
        scaler_path='alzheimers_scaler.joblib'
    )

    # Test case 1: Low risk patient
    low_risk_patient = {
        'Age': 65,
        'Gender': 1,
        'Ethnicity': 0,
        'EducationLevel': 3,
        'BMI': 22.5,
        'Smoking': 0,
        'AlcoholConsumption': 2.0,
        'PhysicalActivity': 8.0,
        'DietQuality': 8.0,
        'SleepQuality': 8.0,
        'FamilyHistoryAlzheimers': 0,
        'CardiovascularDisease': 0,
        'Diabetes': 0,
        'Depression': 0,
        'HeadInjury': 0,
        'Hypertension': 0,
        'SystolicBP': 120,
        'DiastolicBP': 80,
        'CholesterolTotal': 180,
        'CholesterolLDL': 100,
        'CholesterolHDL': 60,
        'CholesterolTriglycerides': 120,
        'MMSE': 29,
        'FunctionalAssessment': 9.0,
        'MemoryComplaints': 0,
        'BehavioralProblems': 0,
        'ADL': 0.5,
        'Confusion': 0,
        'Disorientation': 0,
        'PersonalityChanges': 0,
        'DifficultyCompletingTasks': 0,
        'Forgetfulness': 0
    }

    # Test case 2: High risk patient
    high_risk_patient = {
        'Age': 85,
        'Gender': 0,
        'Ethnicity': 0,
        'EducationLevel': 0,
        'BMI': 20.0,
        'Smoking': 1,
        'AlcoholConsumption': 15.0,
        'PhysicalActivity': 1.0,
        'DietQuality': 2.0,
        'SleepQuality': 3.0,
        'FamilyHistoryAlzheimers': 1,
        'CardiovascularDisease': 1,
        'Diabetes': 1,
        'Depression': 1,
        'HeadInjury': 1,
        'Hypertension': 1,
        'SystolicBP': 160,
        'DiastolicBP': 95,
        'CholesterolTotal': 280,
        'CholesterolLDL': 180,
        'CholesterolHDL': 30,
        'CholesterolTriglycerides': 300,
        'MMSE': 15,
        'FunctionalAssessment': 3.0,
        'MemoryComplaints': 1,
        'BehavioralProblems': 1,
        'ADL': 8.0,
        'Confusion': 1,
        'Disorientation': 1,
        'PersonalityChanges': 1,
        'DifficultyCompletingTasks': 1,
        'Forgetfulness': 1
    }

    test_cases = [
        ("Low Risk Patient", low_risk_patient),
        ("High Risk Patient", high_risk_patient)
    ]

    for case_name, patient_data in test_cases:
        try:
            result = predictor.predict_diagnosis(patient_data)
            print(f"\n{case_name}:")
            print(f"  Diagnosis: {result['diagnosis_label']}")
            print(f"  Alzheimer's Probability: {result['probability_alzheimers']:.4f}")
            print(f"  No Alzheimer's Probability: {result['probability_no_alzheimers']:.4f}")
        except Exception as e:
            print(f"✗ Error predicting for {case_name}: {e}")
            return False

    print("\n✓ Prediction functionality working correctly")
    return True

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\nTesting edge cases...")

    predictor = AlzheimersPredictor()
    predictor.load_model(
        model_path='alzheimers_model.joblib',
        scaler_path='alzheimers_scaler.joblib'
    )

    # Test missing features
    incomplete_patient = {
        'Age': 70,
        'Gender': 1,
        'MMSE': 25
    }

    try:
        result = predictor.predict_diagnosis(incomplete_patient)
        print("✗ Should have failed with missing features")
        return False
    except ValueError as e:
        print(f"✓ Correctly caught missing features: {str(e)[:50]}...")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    return True

def check_model_files():
    """Check model file formats and sizes"""
    print("\nChecking model files...")

    files_to_check = [
        'alzheimers_model.joblib',
        'alzheimers_scaler.joblib',
        'feature_names.joblib'
    ]

    for file_name in files_to_check:
        if os.path.exists(file_name):
            size = os.path.getsize(file_name)
            print(f"✓ {file_name}: {size:,} bytes")
        else:
            print(f"✗ {file_name}: File not found")
            return False

    return True

def export_to_pickle():
    """Export model to pickle format as alternative"""
    print("\nExporting to pickle format...")

    try:
        import joblib
        import pickle

        # Load joblib files
        model = joblib.load('alzheimers_model.joblib')
        scaler = joblib.load('alzheimers_scaler.joblib')
        feature_names = joblib.load('feature_names.joblib')

        # Save as pickle
        with open('alzheimers_model.pkl', 'wb') as f:
            pickle.dump(model, f)

        with open('alzheimers_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)

        with open('feature_names.pkl', 'wb') as f:
            pickle.dump(feature_names, f)

        print("✓ Models exported to pickle format")

        # Test pickle loading
        with open('alzheimers_model.pkl', 'rb') as f:
            test_model = pickle.load(f)
        print("✓ Pickle files can be loaded successfully")

        return True

    except Exception as e:
        print(f"✗ Error exporting to pickle: {e}")
        return False

def main():
    print("Alzheimer's Model Testing Suite")
    print("=" * 40)

    # Change to ml directory
    os.chdir('/Users/zophie/Documents/GitHub/Oct-4-Hackathon-2025-/ml')

    tests = [
        test_model_loading,
        test_prediction_functionality,
        test_edge_cases,
        check_model_files,
        export_to_pickle
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 40)
    print("Test Summary:")
    print(f"Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("✓ All tests passed! Model is ready for API integration.")
        print("\nRecommendation: Use joblib format for production as it's more efficient.")
        print("Pickle files created as backup option.")
    else:
        print("✗ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()