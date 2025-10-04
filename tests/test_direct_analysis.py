#!/usr/bin/env python3
"""
Test script for the direct analysis endpoint using DiagnosisTreatmentPlanner
"""

import requests
import json
import os
from datetime import datetime

# Sample patient data for testing
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

def test_direct_analysis_endpoint():
    """Test the direct analysis endpoint"""
    
    print("Testing Direct Analysis Endpoint")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/analysis/direct"
    
    payload = {
        "patient_data": SAMPLE_PATIENT_DATA
    }
    
    print(f"Endpoint: {endpoint}")
    print(f"Patient Data Keys: {list(SAMPLE_PATIENT_DATA.keys())}")
    print()
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Direct analysis completed successfully")
            print()
            
            # Display key results
            print("📊 ALZHEIMER'S PREDICTION:")
            prediction = result['alzheimers_prediction']
            print(f"  Diagnosis: {prediction['diagnosis_label']}")
            print(f"  Alzheimer's Probability: {prediction['probability_alzheimers']:.4f}")
            print(f"  No Alzheimer's Probability: {prediction['probability_no_alzheimers']:.4f}")
            print()
            
            print("👤 PATIENT PORTFOLIO:")
            portfolio = result['patient_portfolio']
            print(f"  Age: {portfolio['demographics']['age']}")
            print(f"  Gender: {portfolio['demographics']['gender']}")
            print(f"  MMSE Score: {portfolio['health_metrics']['mmse_score']}")
            print(f"  ADL Score: {portfolio['health_metrics']['adl_score']}")
            print(f"  Family History: {portfolio['risk_factors']['family_history_alzheimers']}")
            print(f"  Hypertension: {portfolio['risk_factors']['hypertension']}")
            print()
            
            print("🔍 DIAGNOSIS ANALYSIS:")
            diagnosis = result['diagnosis_analysis']
            print(f"  Predicted Diagnosis: {diagnosis['predicted_diagnosis']}")
            print(f"  Risk Level: {diagnosis['risk_level']}")
            print(f"  Confidence Score: {diagnosis['confidence_score']:.4f}")
            print(f"  MMSE Severity: {diagnosis['severity_assessment']['mmse_severity']}")
            print(f"  Functional Independence: {diagnosis['severity_assessment']['functional_independence']}")
            
            # Check for LLM-enhanced fields
            llm_fields = ["clinical_insights", "differential_considerations", "recommended_follow_up"]
            llm_present = any(field in diagnosis for field in llm_fields)
            print(f"  LLM-Enhanced Fields: {'Yes' if llm_present else 'No'}")
            
            if llm_present:
                if "clinical_insights" in diagnosis:
                    print(f"    Clinical Insights: {diagnosis['clinical_insights'][:100]}...")
                if "differential_considerations" in diagnosis:
                    print(f"    Differential Considerations: {len(diagnosis['differential_considerations'])} items")
                if "recommended_follow_up" in diagnosis:
                    print(f"    Follow-up Recommendations: {len(diagnosis['recommended_follow_up'])} items")
            print()
            
            print("🏥 TREATMENT PLAN:")
            treatment = result['treatment_plan']
            print(f"  Immediate Actions: {len(treatment['immediate_actions'])} items")
            print(f"  Lifestyle Interventions: {len(treatment['lifestyle_interventions'])} items")
            print(f"  Medical Management: {len(treatment['medical_management'])} items")
            print(f"  Support Services: {len(treatment['support_services'])} items")
            
            # Check for LLM-enhanced treatment fields
            llm_treatment_fields = ["personalized_recommendations", "risk_specific_interventions", "caregiver_guidance"]
            llm_treatment_present = any(field in treatment for field in llm_treatment_fields)
            print(f"  LLM-Enhanced Treatment Fields: {'Yes' if llm_treatment_present else 'No'}")
            
            if llm_treatment_present:
                if "personalized_recommendations" in treatment:
                    print(f"    Personalized Recommendations: {len(treatment['personalized_recommendations'])} items")
                if "risk_specific_interventions" in treatment:
                    print(f"    Risk-Specific Interventions: {len(treatment['risk_specific_interventions'])} items")
                if "caregiver_guidance" in treatment:
                    print(f"    Caregiver Guidance: {len(treatment['caregiver_guidance'])} items")
            print()
            
            print("🤖 COMPANION CHATBOT CONFIG:")
            chatbot = result['companion_chatbot_config']
            print(f"  Personality: {chatbot['personality']}")
            print(f"  Communication Style: {chatbot['communication_style']}")
            
            # Check for treatment execution structure
            treatment_execution = chatbot.get("treatment_execution")
            if treatment_execution:
                print(f"  Treatment Execution: Enhanced (LLM)")
                print(f"    Categories: {len(treatment_execution)}")
                for category, activities in treatment_execution.items():
                    if isinstance(activities, list):
                        print(f"      {category}: {len(activities)} chat activities")
            else:
                print(f"  Treatment Execution: Basic (Structured)")
                print(f"    Daily Activities: {len(chatbot.get('daily_activities', []))}")
            
            # Check for conversation flows
            conversation_flows = chatbot.get("conversation_flows")
            if conversation_flows:
                print(f"  Conversation Flows: {len(conversation_flows)} flows")
                for flow_name, flow_config in conversation_flows.items():
                    print(f"    {flow_name}: {flow_config.get('frequency', 'N/A')} frequency")
            else:
                print(f"  Conversation Flows: None (Basic config)")
            
            # Check for treatment goals
            treatment_goals = chatbot.get("treatment_goals")
            if treatment_goals:
                print(f"  Treatment Goals: {len(treatment_goals)} goals")
            else:
                print(f"  Treatment Goals: None (Basic config)")
            print()
            
            print("📅 ANALYSIS METADATA:")
            print(f"  Analysis Method: {result['analysis_method']}")
            print(f"  Analysis Timestamp: {result['analysis_timestamp']}")
            print()
            
            # Save full response to file for inspection
            with open('direct_analysis_response.json', 'w') as f:
                json.dump(result, f, indent=2)
            print("✓ Full response saved to 'direct_analysis_response.json'")
            
            return result
            
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Make sure the API server is running on localhost:8000")
        print("  Start the server with: uvicorn app:app --reload")
        return None
        
    except requests.exceptions.Timeout:
        print("✗ Timeout Error: Request took too long")
        return None
        
    except Exception as e:
        print(f"✗ Unexpected Error: {e}")
        return None

def test_api_health():
    """Test if the API is running and healthy"""
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("API Health Check:")
            print(f"  Service: {health.get('service', 'Unknown')}")
            print(f"  Alzheimer's Predictor: {health.get('alzheimers_predictor', 'Unknown')}")
            print(f"  LLM Configured: {health.get('llm_configured', 'Unknown')}")
            return True
        else:
            print(f"✗ API Health Check Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ API not running. Start with: uvicorn app:app --reload")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def demonstrate_usage():
    """Demonstrate how to use the direct analysis endpoint"""
    
    print("\n" + "=" * 60)
    print("USAGE DEMONSTRATION")
    print("=" * 60)
    
    print("""
The direct analysis endpoint provides a simple way to get comprehensive
analysis without going through the patient intake system.

📋 REQUEST FORMAT:
POST /api/analysis/direct
{
    "patient_data": {
        "Age": 75,
        "Gender": 1,
        "MMSE": 26,
        "ADL": 85,
        "FamilyHistoryAlzheimers": 1,
        "MemoryComplaints": 1,
        "Forgetfulness": 1,
        // ... other patient data fields
    }
}

📊 RESPONSE FORMAT:
{
    "patient_portfolio": {
        "demographics": {...},
        "health_metrics": {...},
        "risk_factors": {...},
        "lifestyle_factors": {...}
    },
    "diagnosis_analysis": {
        "predicted_diagnosis": "...",
        "risk_level": "...",
        "confidence_score": 0.85,
        "key_indicators": {...},
        "severity_assessment": {...},
        "clinical_insights": "...",  // LLM-enhanced
        "differential_considerations": [...],  // LLM-enhanced
        "recommended_follow_up": [...]  // LLM-enhanced
    },
    "treatment_plan": {
        "immediate_actions": [...],
        "lifestyle_interventions": [...],
        "medical_management": [...],
        "support_services": [...],
        "personalized_recommendations": [...],  // LLM-enhanced
        "risk_specific_interventions": [...],  // LLM-enhanced
        "caregiver_guidance": [...]  // LLM-enhanced
    },
    "companion_chatbot_config": {
        "personality": "...",
        "communication_style": "...",
        "treatment_execution": {...},  // LLM-enhanced
        "conversation_flows": {...},  // LLM-enhanced
        "treatment_goals": [...]  // LLM-enhanced
    },
    "analysis_timestamp": "2024-01-01T00:00:00",
    "analysis_method": "llm_enhanced",  // or "structured"
    "alzheimers_prediction": {
        "diagnosis_label": "...",
        "probability_alzheimers": 0.15,
        "probability_no_alzheimers": 0.85
    }
}

🎯 USE CASES:
• Direct analysis of patient data without intake flow
• Integration with external systems
• Batch processing of patient records
• Research and development
• Testing and validation

🔧 INTEGRATION EXAMPLE:
```python
import requests

# Prepare patient data
patient_data = {
    "Age": 75,
    "Gender": 1,
    "MMSE": 26,
    # ... other fields
}

# Call direct analysis endpoint
response = requests.post(
    "http://localhost:8000/api/analysis/direct",
    json={"patient_data": patient_data}
)

if response.status_code == 200:
    result = response.json()
    
    # Extract components
    portfolio = result["patient_portfolio"]
    diagnosis = result["diagnosis_analysis"]
    treatment = result["treatment_plan"]
    chatbot_config = result["companion_chatbot_config"]
    
    # Use the results
    print(f"Risk Level: {diagnosis['risk_level']}")
    print(f"Treatment Actions: {len(treatment['immediate_actions'])}")
    print(f"Analysis Method: {result['analysis_method']}")
```
    """)

if __name__ == "__main__":
    print("CognifyCare Direct Analysis Test")
    print("=" * 50)
    print()
    
    # Check API health first
    if test_api_health():
        print()
        # Test the direct analysis endpoint
        result = test_direct_analysis_endpoint()
        
        if result:
            print("✓ Direct analysis test completed successfully!")
            
            # Show usage demonstration
            demonstrate_usage()
            
            print("\n" + "=" * 50)
            print("SUMMARY")
            print("=" * 50)
            print("✓ Direct analysis endpoint is working correctly")
            print("✓ Returns comprehensive patient portfolio")
            print("✓ Provides detailed diagnosis analysis")
            print("✓ Generates complete treatment plan")
            print("✓ Includes companion chatbot configuration")
            print("✓ Tracks analysis method (LLM vs structured)")
            print("✓ Includes Alzheimer's prediction results")
            
            print(f"\n📁 FILES GENERATED:")
            print(f"• direct_analysis_response.json - Complete analysis response")
            
        else:
            print("\n⚠️  Direct analysis test failed")
    else:
        print("\nPlease start the API server first:")
        print("  uvicorn app:app --reload")
        print("  Then run this test again.")
    
    print("\n" + "=" * 50)
    print("NEXT STEPS:")
    print("=" * 50)
    print("1. Use the direct analysis endpoint for external integrations")
    print("2. Configure LLM for enhanced analysis (optional)")
    print("3. Implement the returned chatbot configuration")
    print("4. Use treatment plan for patient care")
    print("5. Monitor analysis results and adjust as needed")
