#!/usr/bin/env python3
"""
Test script for all endpoints in the app folder
Tests diagnosis_treatment_planning and intake.py endpoints
"""

import requests
import json
import os
from datetime import datetime

# Sample data for testing
SAMPLE_PATIENT_DATA = {
    "Age": 75,
    "Gender": 1,  # Female
    "Ethnicity": 0,
    "EducationLevel": 3,
    "HeightCm": 160,
    "WeightKg": 65,
    "BMI": 25.4,
    "Smoking": 0,  # No
    "AlcoholConsumption": 2.0,
    "PhysicalActivity": 6.0,
    "DietQuality": 7.0,
    "SleepQuality": 6.0,
    "FamilyHistoryAlzheimers": 1,  # Yes
    "CardiovascularDisease": 0,  # No
    "Diabetes": 0,  # No
    "Depression": 0,  # No
    "HeadInjury": 0,  # No
    "Hypertension": 1,  # Yes
    "SystolicBP": 135,
    "DiastolicBP": 85,
    "CholesterolTotal": 200,
    "CholesterolLDL": 120,
    "CholesterolHDL": 55,
    "CholesterolTriglycerides": 150,
    "MMSE": 26,
    "FunctionalAssessment": 8.0,
    "ADL": 85,
    "MemoryComplaints": 1,  # Yes
    "BehavioralProblems": 0,  # No
    "Confusion": 0,  # No
    "Disorientation": 0,  # No
    "PersonalityChanges": 0,  # No
    "DifficultyCompletingTasks": 0,  # No
    "Forgetfulness": 1  # Yes
}

def test_analysis_health():
    """Test analysis module health endpoint"""
    print("Testing Analysis Module Health")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8000/api/analysis/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("✓ Analysis module is healthy")
            print(f"  Status: {health.get('status', 'Unknown')}")
            print(f"  Alzheimer's Predictor: {health.get('alzheimers_predictor', 'Unknown')}")
            print(f"  LLM Configured: {health.get('llm_configured', 'Unknown')}")
            print(f"  LLM Provider: {health.get('llm_provider', 'Unknown')}")
            return True
        else:
            print(f"✗ Analysis module health failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Analysis module health error: {e}")
        return False

def test_direct_analysis():
    """Test direct analysis endpoint"""
    print("\nTesting Direct Analysis Endpoint")
    print("-" * 30)
    
    try:
        payload = {"patient_data": SAMPLE_PATIENT_DATA}
        response = requests.post(
            "http://localhost:8000/api/analysis/direct",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Direct analysis endpoint working")
            print(f"  Analysis Method: {result.get('analysis_method', 'Unknown')}")
            print(f"  Risk Level: {result.get('diagnosis_analysis', {}).get('risk_level', 'Unknown')}")
            print(f"  Treatment Actions: {len(result.get('treatment_plan', {}).get('immediate_actions', []))}")
            print(f"  Chatbot Config: {'Enhanced' if 'treatment_execution' in result.get('companion_chatbot_config', {}) else 'Basic'}")
            return True
        else:
            print(f"✗ Direct analysis failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Direct analysis error: {e}")
        return False

def test_intake_start():
    """Test intake start endpoint"""
    print("\nTesting Intake Start Endpoint")
    print("-" * 30)
    
    try:
        response = requests.post(
            "http://localhost:8000/api/patient/456/intake/start",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Intake start endpoint working")
            print(f"  Session ID: {result.get('session_id', 'Unknown')[:8]}...")
            print(f"  Patient ID: {result.get('patient_id', 'Unknown')}")
            print(f"  Step Index: {result.get('step_index', 'Unknown')}")
            print(f"  Total Steps: {result.get('total_steps', 'Unknown')}")
            return result.get('session_id')
        else:
            print(f"✗ Intake start failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Intake start error: {e}")
        return None

def test_intake_reply(session_id):
    """Test intake reply endpoint"""
    print("\nTesting Intake Reply Endpoint")
    print("-" * 30)
    
    if not session_id:
        print("✗ No session ID available for intake reply test")
        return False
    
    try:
        payload = {
            "session_id": session_id,
            "message": "I am 75 years old"
        }
        response = requests.post(
            "http://localhost:8000/api/patient/456/intake/reply",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Intake reply endpoint working")
            print(f"  Session ID: {result.get('session_id', 'Unknown')[:8]}...")
            print(f"  Step Index: {result.get('step_index', 'Unknown')}")
            print(f"  Finished: {result.get('finished', 'Unknown')}")
            print(f"  Next Prompt: {result.get('next_prompt', 'None')[:50]}...")
            return True
        else:
            print(f"✗ Intake reply failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Intake reply error: {e}")
        return False

def test_intake_state(session_id):
    """Test intake state endpoint"""
    print("\nTesting Intake State Endpoint")
    print("-" * 30)
    
    if not session_id:
        print("✗ No session ID available for intake state test")
        return False
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/patient/456/intake/state?session_id={session_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Intake state endpoint working")
            print(f"  Patient ID: {result.get('patient_id', 'Unknown')}")
            print(f"  Step Index: {result.get('step_index', 'Unknown')}")
            print(f"  Finished: {result.get('finished', 'Unknown')}")
            print(f"  Answers: {len(result.get('answers', {}))} fields")
            return True
        else:
            print(f"✗ Intake state failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Intake state error: {e}")
        return False

def test_llm_configuration():
    """Test LLM configuration (if available)"""
    print("\nTesting LLM Configuration")
    print("-" * 30)
    
    try:
        # Try to configure LLM (this will fail if no real API key, but should not crash)
        api_key = os.getenv("OPENAI_API_KEY", "test-key")
        payload = {
            "api_key": api_key,
            "provider": "openai"
        }
        response = requests.post(
            "http://localhost:8000/api/admin/configure-llm",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ LLM configuration endpoint working")
            print(f"  Status: {result.get('status', 'Unknown')}")
            print(f"  Message: {result.get('message', 'Unknown')}")
            print(f"  LLM Available: {result.get('llm_available', 'Unknown')}")
            return True
        else:
            print(f"✗ LLM configuration failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ LLM configuration error: {e}")
        return False

def main():
    """Run all app folder endpoint tests"""
    print("CognifyCare App Folder Endpoint Test")
    print("=" * 60)
    
    # Test results tracking
    results = {}
    
    # Test analysis module health
    results['analysis_health'] = test_analysis_health()
    
    # Test direct analysis
    results['direct_analysis'] = test_direct_analysis()
    
    # Test intake flow
    session_id = test_intake_start()
    results['intake_start'] = session_id is not None
    
    if session_id:
        results['intake_reply'] = test_intake_reply(session_id)
        results['intake_state'] = test_intake_state(session_id)
    else:
        results['intake_reply'] = False
        results['intake_state'] = False
    
    # Test LLM configuration (optional)
    results['llm_config'] = test_llm_configuration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    if passed_tests == total_tests:
        print("\n🎉 All app folder endpoints are working correctly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} endpoint(s) need attention")
    
    print("\n" + "=" * 60)
    print("ENDPOINTS TESTED:")
    print("=" * 60)
    print("✓ GET  /api/analysis/health - Analysis module health")
    print("✓ POST /api/analysis/direct - Direct analysis")
    print("✓ POST /api/patient/{id}/intake/start - Intake start")
    print("✓ POST /api/patient/{id}/intake/reply - Intake reply")
    print("✓ GET  /api/patient/{id}/intake/state - Intake state")
    print("✓ POST /api/admin/configure-llm - LLM configuration (optional)")
    
    print("\n" + "=" * 60)
    print("FILES TESTED:")
    print("=" * 60)
    print("✓ app/analysis/diagnosis_treatment_planning.py")
    print("✓ app/patient/intake.py")

if __name__ == "__main__":
    main()
