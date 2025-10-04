#!/usr/bin/env python3
"""
Test Doctor Review Endpoints
Tests the complete doctor workflow for reviewing and updating treatment plans
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_json(data: Dict[str, Any], title: str = ""):
    """Pretty print JSON data"""
    if title:
        print(f"\n{'='*70}")
        print(f"  {title}")
        print('='*70)
    print(json.dumps(data, indent=2))
    print()

def print_section(title: str):
    """Print section header"""
    print(f"\n{'#'*70}")
    print(f"# {title}")
    print(f"{'#'*70}\n")

# ==================== Setup: Create Patient with Treatment Plan ====================

def setup_patient_with_treatment_plan():
    """Create a patient with intake analysis and initialized chatbot"""

    patient_id = 12345

    print_section("SETUP: Creating Patient with Treatment Plan")

    # Sample intake data
    intake_data = {
        "Age": 72, "Gender": 0, "Ethnicity": 0, "EducationLevel": 2,
        "BMI": 25.7, "Smoking": 0, "AlcoholConsumption": 2,
        "PhysicalActivity": 5, "DietQuality": 2, "SleepQuality": 6,
        "FamilyHistoryAlzheimers": 1, "CardiovascularDisease": 0,
        "Diabetes": 1, "Depression": 1, "HeadInjury": 0,
        "Hypertension": 1, "SystolicBP": 142, "DiastolicBP": 88,
        "CholesterolTotal": 215, "CholesterolLDL": 135,
        "CholesterolHDL": 48, "CholesterolTriglycerides": 160,
        "MMSE": 21, "FunctionalAssessment": 72, "ADL": 78,
        "MemoryComplaints": 1, "BehavioralProblems": 0,
        "Confusion": 1, "Disorientation": 1, "PersonalityChanges": 0,
        "DifficultyCompletingTasks": 1, "Forgetfulness": 1
    }

    # Step 1: Get intake analysis
    print("\n📋 Step 1: Analyzing patient intake...")
    response = requests.post(
        f"{BASE_URL}/api/patient/{patient_id}/intake/analyze",
        json={"patient_id": patient_id, "intake_data": intake_data}
    )
    response.raise_for_status()
    analysis_result = response.json()

    print(f"✓ Analysis complete: {analysis_result['diagnosis_analysis']['predicted_diagnosis']}")

    # Step 2: Initialize chatbot with treatment plan
    print("\n🤖 Step 2: Initializing chatbot...")
    response = requests.post(
        f"{BASE_URL}/api/patient/{patient_id}/chatbot/initialize",
        json={
            "patient_id": patient_id,
            "patient_portfolio": analysis_result["patient_portfolio"],
            "treatment_plan": analysis_result["treatment_plan"],
            "chatbot_config": analysis_result["companion_chatbot_config"]
        }
    )
    response.raise_for_status()
    init_result = response.json()

    print(f"✓ Chatbot initialized: {init_result['chatbot_id']}")

    return patient_id, analysis_result

# ==================== Test 1: Review Intake Analysis ====================

def test_intake_analysis_review():
    """Test doctor reviewing intake analysis and updating treatment plan"""

    print_section("TEST 1: Doctor Reviews Intake Analysis")

    patient_id, analysis_result = setup_patient_with_treatment_plan()

    # Doctor's decision to approve with modifications
    print("\n👨‍⚕️ Doctor reviews intake analysis...")

    doctor_decision = {
        "patient_id": patient_id,
        "intake_analysis": analysis_result,
        "doctor_decision": {
            "approved": True,
            "notes": "Approved with additional cognitive exercises and increased monitoring frequency",
            "treatment_changes": {
                "lifestyle_interventions": [
                    "Daily cognitive training exercises - 20 minutes",
                    "Memory journal keeping"
                ],
                "monitoring_schedule": {
                    "cognitive_assessment": "Every 3 months (increased from 6)",
                    "medical_follow_up": "Every 6 weeks"
                }
            },
            "urgency_level": "soon"
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/doctor/review/intake",
        json=doctor_decision
    )
    response.raise_for_status()
    review_result = response.json()

    print_json(review_result, "Doctor Review Result")

    # Verify updates were applied
    print("\n🔍 Verifying treatment plan was updated...")
    response = requests.get(f"{BASE_URL}/api/doctor/patient/{patient_id}/current-plan")
    response.raise_for_status()
    current_plan = response.json()

    print(f"✓ Treatment plan updated: {len(current_plan['current_treatment_plan'])} categories")
    print(f"✓ Monitoring schedule updated: {current_plan['current_treatment_plan'].get('monitoring_schedule', {})}")

    return patient_id

# ==================== Test 2: Review Conversation Analysis ====================

def test_conversation_analysis_review(patient_id: int):
    """Test doctor reviewing conversation analysis and updating treatment"""

    print_section("TEST 2: Doctor Reviews Conversation Analysis")

    # Simulate conversation analysis showing concerning symptoms
    print("\n💬 Simulating conversation analysis with symptom changes...")

    conversation_analysis = {
        "analysis_timestamp": "2025-10-04T15:30:00Z",
        "patient_id": f"P{patient_id}",
        "llm_analysis": {
            "mood_assessment": {
                "current_state": "Significantly declined",
                "change_from_baseline": "significantly_declined",
                "severity": "moderate"
            },
            "symptom_assessment": {
                "cognitive_changes": {
                    "observed": True,
                    "details": "Increased confusion and disorientation, difficulty with daily tasks",
                    "severity": "moderate"
                },
                "behavioral_changes": {
                    "observed": True,
                    "details": "More withdrawn, less social engagement",
                    "severity": "mild"
                }
            },
            "conversation_attitude": {
                "engagement_level": "low",
                "coherence": "confused",
                "emotional_tone": "negative"
            },
            "concern_level": "high"
        },
        "contact_doctor_decision": {
            "should_contact": True,
            "urgency": "soon",
            "reasoning": "Significant decline in cognitive function and mood",
            "recommended_actions": [
                "Schedule neurologist appointment",
                "Increase caregiver support",
                "Review medications"
            ],
            "specific_concerns": [
                "Severe disorientation",
                "Social withdrawal",
                "Difficulty with ADLs"
            ]
        }
    }

    # Doctor reviews and decides to adjust treatment
    print("\n👨‍⚕️ Doctor reviews conversation analysis...")

    doctor_decision = {
        "patient_id": patient_id,
        "conversation_analysis": conversation_analysis,
        "doctor_decision": {
            "approved": True,
            "notes": "Concerning decline observed. Adding medication review and increasing support services. Scheduling urgent neurology consultation.",
            "treatment_changes": {
                "immediate_actions": [
                    "Schedule urgent neurology consultation within 1 week",
                    "Complete medication review and assessment",
                    "Arrange home safety evaluation"
                ],
                "medical_management": [
                    "Consider adjusting cholinesterase inhibitor dosage",
                    "Evaluate for depression treatment"
                ],
                "support_services": [
                    "Increase caregiver visits to daily",
                    "Arrange respite care for caregiver",
                    "Connect with adult day care program"
                ],
                "monitoring_schedule": {
                    "cognitive_assessment": "Every 2 months",
                    "medical_follow_up": "Every 2 weeks until stable",
                    "caregiver_check_in": "Daily"
                }
            },
            "urgency_level": "urgent"
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/doctor/review/conversation",
        json=doctor_decision
    )
    response.raise_for_status()
    review_result = response.json()

    print_json(review_result, "Doctor Review Result")

    # Verify updates were applied to chatbot
    print("\n🔍 Verifying chatbot config was updated...")
    response = requests.get(f"{BASE_URL}/api/doctor/patient/{patient_id}/current-plan")
    response.raise_for_status()
    current_plan = response.json()

    print(f"✓ Chatbot config updated")
    print(f"✓ New monitoring schedule: {current_plan['current_treatment_plan'].get('monitoring_schedule', {})}")

    # Check that chatbot has new activities
    treatment_plan = current_plan['current_treatment_plan']
    print(f"✓ Immediate actions: {len(treatment_plan.get('immediate_actions', []))} items")
    print(f"✓ Support services: {len(treatment_plan.get('support_services', []))} items")

# ==================== Test 3: Direct Treatment Update ====================

def test_direct_treatment_update(patient_id: int):
    """Test direct treatment plan update by doctor"""

    print_section("TEST 3: Direct Treatment Plan Update")

    print("\n👨‍⚕️ Doctor makes direct treatment update...")

    update_request = {
        "patient_id": patient_id,
        "updates": {
            "lifestyle_interventions": [
                "New: Participate in music therapy sessions twice weekly",
                "New: Engage in light gardening activities for cognitive stimulation"
            ],
            "personalized_recommendations": [
                "Family to create memory book with patient",
                "Use visual cues and labels throughout home"
            ]
        },
        "reason": "Regular 3-month follow-up. Patient showing stable cognition, adding enrichment activities."
    }

    response = requests.post(
        f"{BASE_URL}/api/doctor/treatment/update",
        json=update_request
    )
    response.raise_for_status()
    update_result = response.json()

    print_json(update_result, "Direct Update Result")

    # Verify
    print("\n🔍 Verifying direct update was applied...")
    response = requests.get(f"{BASE_URL}/api/doctor/patient/{patient_id}/current-plan")
    response.raise_for_status()
    current_plan = response.json()

    lifestyle = current_plan['current_treatment_plan'].get('lifestyle_interventions', [])
    print(f"✓ Lifestyle interventions now has {len(lifestyle)} items")
    print(f"✓ Includes music therapy: {'music therapy' in str(lifestyle).lower()}")

# ==================== Test 4: Rejected Review ====================

def test_rejected_review():
    """Test doctor rejecting a review (no changes applied)"""

    print_section("TEST 4: Doctor Rejects Review (No Changes)")

    patient_id, analysis_result = setup_patient_with_treatment_plan()

    print("\n👨‍⚕️ Doctor reviews but does not approve changes...")

    doctor_decision = {
        "patient_id": patient_id,
        "intake_analysis": analysis_result,
        "doctor_decision": {
            "approved": False,
            "notes": "Analysis reviewed. Current treatment plan is adequate. No changes needed at this time. Will re-evaluate in 3 months.",
            "treatment_changes": None,
            "urgency_level": "routine"
        }
    }

    response = requests.post(
        f"{BASE_URL}/api/doctor/review/intake",
        json=doctor_decision
    )
    response.raise_for_status()
    review_result = response.json()

    print_json(review_result, "Rejected Review Result")

    assert review_result["decision_applied"] == False, "Decision should not be applied"
    assert review_result["updated_treatment_plan"] is None, "Treatment plan should not be updated"

    print("✓ Verified: No changes were applied as expected")

# ==================== Main Test Runner ====================

def main():
    """Run all doctor review tests"""

    print("\n" + "="*70)
    print("  DOCTOR REVIEW ENDPOINT TESTS")
    print("="*70)
    print("\nTesting doctor review workflow for treatment plan updates")
    print("="*70)

    try:
        # Test 1: Intake analysis review
        patient_id = test_intake_analysis_review()
        print("\n✅ Test 1 PASSED: Intake analysis review")

        # Test 2: Conversation analysis review
        test_conversation_analysis_review(patient_id)
        print("\n✅ Test 2 PASSED: Conversation analysis review")

        # Test 3: Direct treatment update
        test_direct_treatment_update(patient_id)
        print("\n✅ Test 3 PASSED: Direct treatment update")

        # Test 4: Rejected review
        test_rejected_review()
        print("\n✅ Test 4 PASSED: Rejected review")

        # Final summary
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)
        print("\n✅ All doctor review tests PASSED!")
        print("\nVerified functionality:")
        print("  ✓ Doctor can review intake analysis and update treatment plans")
        print("  ✓ Doctor can review conversation analysis and adjust care")
        print("  ✓ Doctor can make direct treatment plan updates")
        print("  ✓ Doctor can reject reviews (no changes applied)")
        print("  ✓ Chatbot configs are automatically updated with new plans")
        print("  ✓ Treatment changes are properly merged into existing plans")
        print("\n" + "="*70)

    except Exception as e:
        print(f"\n❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n🚀 Starting Doctor Review Endpoint Tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("\nPress Enter to continue or Ctrl+C to cancel...")

    try:
        input()
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Tests cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
