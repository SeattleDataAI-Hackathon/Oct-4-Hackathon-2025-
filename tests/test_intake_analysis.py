#!/usr/bin/env python3
"""
Test script for the intake analysis endpoint
"""

import requests
import json

# Sample intake data (what would come from the intake flow)
SAMPLE_INTAKE_DATA = {
    "Age": 78,
    "Gender": 0,  # Male
    "Ethnicity": 0,
    "EducationLevel": 2,
    "HeightCm": 175,
    "WeightKg": 80,
    "BMI": 26.1,
    "Smoking": 1,  # Yes
    "AlcoholConsumption": 8.0,
    "PhysicalActivity": 3.0,
    "DietQuality": 4.0,
    "SleepQuality": 4.0,
    "FamilyHistoryAlzheimers": 1,  # Yes
    "CardiovascularDisease": 1,  # Yes
    "Diabetes": 0,
    "Depression": 1,  # Yes
    "HeadInjury": 0,
    "Hypertension": 1,  # Yes
    "SystolicBP": 160,
    "DiastolicBP": 95,
    "CholesterolTotal": 280,
    "CholesterolLDL": 180,
    "CholesterolHDL": 35,
    "CholesterolTriglycerides": 250,
    "MMSE": 18,
    "FunctionalAssessment": 4.0,
    "ADL": 60,
    "MemoryComplaints": 1,  # Yes
    "BehavioralProblems": 1,  # Yes
    "Confusion": 1,  # Yes
    "Disorientation": 1,  # Yes
    "PersonalityChanges": 1,  # Yes
    "DifficultyCompletingTasks": 1,  # Yes
    "Forgetfulness": 1  # Yes
}

def test_intake_analysis():
    """Test the intake analysis endpoint"""
    print("Testing Intake Analysis Endpoint")
    print("-" * 40)
    
    try:
        payload = {
            "patient_data": SAMPLE_INTAKE_DATA
        }
        response = requests.post(
            "http://localhost:8000/api/analysis/direct",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Direct analysis endpoint working (intake analysis)")
            print(f"  Analysis Method: {result.get('analysis_method', 'Unknown')}")
            print(f"  Risk Level: {result.get('diagnosis_analysis', {}).get('risk_level', 'Unknown')}")
            print(f"  Treatment Actions: {len(result.get('treatment_plan', {}).get('immediate_actions', []))}")
            
            # Check chatbot config
            chatbot_config = result.get('companion_chatbot_config', {})
            has_treatment_execution = 'treatment_execution' in chatbot_config
            config_type = "Enhanced" if has_treatment_execution else "Basic"
            print(f"  Chatbot Config: {config_type}")
            
            # Show some key results
            alzheimers_pred = result.get('alzheimers_prediction', {})
            print(f"  Alzheimer's Probability: {alzheimers_pred.get('probability_alzheimers', 'Unknown'):.2f}")
            print(f"  Diagnosis: {alzheimers_pred.get('diagnosis_label', 'Unknown')}")
            
            return True
        else:
            print(f"✗ Intake analysis failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Intake analysis error: {e}")
        return False

def main():
    """Run intake analysis test"""
    print("CognifyCare Intake Analysis Test")
    print("=" * 50)
    
    success = test_intake_analysis()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Intake Analysis: {'✓ PASS' if success else '✗ FAIL'}")
    
    if success:
        print("\n🎉 Intake analysis endpoint is working correctly!")
    else:
        print("\n⚠️  Intake analysis test failed")

if __name__ == "__main__":
    main()