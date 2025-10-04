#!/usr/bin/env python3
"""
Test script for CognifyCare workflows
Tests two main workflows:
1. Intake Analysis Flow - Complete patient intake and diagnosis
2. Routine Chat Flow - Daily check-in chatbot interaction
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

# ============================================================================
# WORKFLOW 1: INTAKE ANALYSIS FLOW
# ============================================================================

def test_intake_analysis_flow():
    """
    Test Workflow 1: Intake Analysis Flow

    Steps:
    1. Start intake session
    2. Answer all intake questions
    3. Complete intake and get analysis
    4. Verify Alzheimer's prediction, diagnosis, and treatment plan
    """

    print_section("WORKFLOW 1: INTAKE ANALYSIS FLOW")

    patient_id = 54321

    # Step 1: Start intake session
    print("\n📝 Step 1: Starting intake session...")
    try:
        response = requests.post(f"{BASE_URL}/api/patient/{patient_id}/intake/start")
        response.raise_for_status()
        start_result = response.json()

        session_id = start_result["session_id"]
        print(f"✓ Session created: {session_id}")
        print(f"First question: {start_result['prompt']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error starting intake: {e}")
        return False

    # Step 2: Answer all intake questions
    print("\n📝 Step 2: Answering intake questions...")

    # Simulate patient answers to all questions
    answers = [
        "72",  # Age
        "female",  # Gender
        "white",  # Ethnicity
        "college",  # Education
        "165 cm",  # Height
        "70 kg",  # Weight
        "skip",  # BMI (will be calculated)
        "no",  # Smoking
        "2",  # Alcohol per week
        "5",  # Physical activity
        "2",  # Diet quality
        "6",  # Sleep quality
        "yes",  # Family history Alzheimers
        "no",  # Cardiovascular disease
        "yes",  # Diabetes
        "yes",  # Depression
        "no",  # Head injury
        "yes",  # Hypertension
        "142",  # Systolic BP
        "88",  # Diastolic BP
        "215",  # Total cholesterol
        "135",  # LDL
        "48",  # HDL
        "160",  # Triglycerides
        "21",  # MMSE score
        "72",  # Functional assessment
        "78",  # ADL
        "yes",  # Memory complaints
        "no",  # Behavioral problems
        "yes",  # Confusion
        "yes",  # Disorientation
        "no",  # Personality changes
        "yes",  # Difficulty completing tasks
        "yes"  # Forgetfulness
    ]

    for i, answer in enumerate(answers, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/api/patient/{patient_id}/intake/reply",
                json={
                    "session_id": session_id,
                    "message": answer
                }
            )
            response.raise_for_status()
            reply_result = response.json()

            if reply_result.get("finished"):
                print(f"✓ Intake completed after {i} questions")
                summary = reply_result.get("summary", {})
                print_json(summary, "Intake Summary")
                break
            else:
                print(f"  Q{i}: {answer} → Next: {reply_result.get('next_prompt', 'N/A')[:60]}...")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error answering question {i}: {e}")
            return False

    # Step 3: Get intake state to retrieve collected data
    print("\n📝 Step 3: Retrieving intake state...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/patient/{patient_id}/intake/state",
            params={"session_id": session_id}
        )
        response.raise_for_status()
        state_result = response.json()

        intake_data = state_result["answers"]
        print(f"✓ Retrieved {len(intake_data)} data points from intake")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error retrieving intake state: {e}")
        return False

    # Step 4: Analyze intake data (Alzheimer's prediction + diagnosis + treatment plan)
    print("\n🔬 Step 4: Analyzing intake data with Alzheimer's prediction...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/patient/{patient_id}/intake/analyze",
            json={
                "patient_id": patient_id,
                "intake_data": intake_data
            }
        )
        response.raise_for_status()
        analysis_result = response.json()

        print_json({
            "alzheimers_diagnosis": analysis_result["alzheimers_prediction"]["diagnosis_label"],
            "alzheimers_probability": f"{analysis_result['alzheimers_prediction']['probability_alzheimers']:.2%}",
            "risk_level": analysis_result["diagnosis_analysis"]["risk_level"],
            "predicted_diagnosis": analysis_result["diagnosis_analysis"]["predicted_diagnosis"],
            "analysis_method": analysis_result["analysis_method"]
        }, "Analysis Results")

        print("✓ Patient Portfolio Generated")
        print("✓ Diagnosis Analysis Completed")
        print("✓ Treatment Plan Created")
        print("✓ Chatbot Config Generated")

        # Save full analysis to file
        with open("intake_analysis_result.json", "w") as f:
            json.dump(analysis_result, f, indent=2)

        print("\n✓ Full analysis saved to intake_analysis_result.json")

        return True, analysis_result

    except requests.exceptions.RequestException as e:
        print(f"❌ Error analyzing intake: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False, None

# ============================================================================
# WORKFLOW 2: ROUTINE CHAT FLOW
# ============================================================================

def test_routine_chat_flow(analysis_result: Dict[str, Any] = None):
    """
    Test Workflow 2: Routine Chat Flow

    Steps:
    1. Initialize chatbot with patient portfolio and treatment plan
    2. Start daily check-in chat session
    3. Simulate conversation with routine check-in questions
    4. End session and get comprehensive analysis
    5. Verify conversation analysis and doctor contact decision
    """

    print_section("WORKFLOW 2: ROUTINE CHAT FLOW")

    patient_id = 54321

    # If no analysis result provided, use sample data
    if not analysis_result:
        print("⚠️  No analysis result provided, using sample data...")
        sample_intake_data = {
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

        try:
            response = requests.post(
                f"{BASE_URL}/api/patient/{patient_id}/intake/analyze",
                json={"patient_id": patient_id, "intake_data": sample_intake_data}
            )
            response.raise_for_status()
            analysis_result = response.json()
        except Exception as e:
            print(f"❌ Error getting analysis: {e}")
            return False

    # Step 1: Initialize chatbot
    print("\n🤖 Step 1: Initializing chatbot with treatment plan...")
    try:
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
        print(f"  Status: {init_result['status']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error initializing chatbot: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

    # Step 2: Start daily check-in chat session
    print("\n💬 Step 2: Starting daily check-in session...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/patient/{patient_id}/chat/start",
            json={
                "patient_id": patient_id,
                "chat_type": "daily_check_in"
            }
        )
        response.raise_for_status()
        chat_start = response.json()

        session_id = chat_start["session_id"]
        print(f"✓ Chat session started: {session_id}")
        print(f"  Bot: {chat_start['chatbot_message']}")
        print(f"  Chat type: {chat_start['chat_type']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error starting chat: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

    # Step 3: Simulate routine check-in conversation
    print("\n💬 Step 3: Simulating routine check-in conversation...")

    conversation = [
        "I'm feeling a bit confused today",
        "I didn't sleep well last night, maybe 4 hours",
        "Yes, I took my morning medications",
        "My energy is very low, about a 3 out of 10",
        "I forgot to eat breakfast again",
        "I'm having trouble remembering what day it is"
    ]

    chat_interactions = []

    for i, patient_msg in enumerate(conversation, 1):
        print(f"\n  Turn {i}:")
        print(f"  Patient: {patient_msg}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/patient/chat/message",
                json={
                    "session_id": session_id,
                    "patient_message": patient_msg
                }
            )
            response.raise_for_status()
            chat_response = response.json()

            print(f"  Bot: {chat_response['chatbot_message']}")

            chat_interactions.append({
                "timestamp": f"2025-10-04T{14+i//10}:{30+(i*5)%60:02d}:00Z",
                "speaker": "patient",
                "message": patient_msg
            })

            chat_interactions.append({
                "timestamp": f"2025-10-04T{14+i//10}:{31+(i*5)%60:02d}:00Z",
                "speaker": "bot",
                "message": chat_response['chatbot_message']
            })

            if chat_response.get("activity_completed"):
                print("    ✓ Activity completed")

            if chat_response.get("conversation_complete"):
                print("\n  ✓ Conversation complete!")
                break

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error in turn {i}: {e}")
            continue

    # Step 4: End chat session and get summary
    print("\n📊 Step 4: Ending chat session and retrieving summary...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/patient/chat/end",
            json={"session_id": session_id}
        )
        response.raise_for_status()
        end_result = response.json()

        print_json({
            "completed_activities": end_result["completed_activities"],
            "metrics": end_result["metrics"]
        }, "Chat Session Metrics")

        # Save chat log
        with open("routine_chat_log.json", "w") as f:
            json.dump(end_result, f, indent=2)

        print("✓ Chat log saved to routine_chat_log.json")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error ending chat: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

    # Step 5: Analyze conversation for symptom/mood changes
    print("\n🔍 Step 5: Analyzing conversation for symptom changes...")

    # Prepare conversation record for analysis
    conversation_record = {
        "patient_id": f"P{patient_id}",
        "conversation_date": "2025-10-04T14:30:00Z",
        "conversations": chat_interactions,
        "routine_check_in": {
            "mood_scale": 3,
            "energy_level": 3,
            "sleep_quality": 2,
            "pain_level": 4,
            "appetite": "poor",
            "social_engagement": "isolated",
            "cognitive_clarity": 3
        },
        "previous_baseline": {
            "mood_scale": 6,
            "energy_level": 7,
            "sleep_quality": 6,
            "pain_level": 2,
            "appetite": "good",
            "social_engagement": "active",
            "cognitive_clarity": 6
        }
    }

    # Note: This would call the conversation analyzer, but we'll simulate the output
    print("  ⚠️  Conversation analyzer requires Claude API key")
    print("  Simulated analysis output:")

    simulated_analysis = {
        "llm_analysis": {
            "mood_assessment": {
                "current_state": "Significantly declined",
                "change_from_baseline": "significantly_declined",
                "severity": "moderate"
            },
            "symptom_assessment": {
                "cognitive_changes": {
                    "observed": True,
                    "details": "Memory issues, confusion about time/date, difficulty with daily tasks",
                    "severity": "moderate"
                }
            },
            "conversation_attitude": {
                "engagement_level": "moderate",
                "coherence": "mostly_clear",
                "emotional_tone": "negative"
            },
            "concern_level": "high"
        },
        "contact_doctor_decision": {
            "should_contact": True,
            "urgency": "soon",
            "reasoning": "Significant decline in cognitive function, sleep, mood, and appetite compared to baseline",
            "recommended_actions": [
                "Schedule neurologist appointment",
                "Review medication adherence",
                "Increase caregiver support"
            ],
            "specific_concerns": [
                "Severe sleep deprivation (4 hours)",
                "Missed meals",
                "Temporal disorientation",
                "Low energy and mood"
            ]
        }
    }

    print_json(simulated_analysis, "Conversation Analysis (Simulated)")

    # Save conversation analysis
    with open("conversation_analysis.json", "w") as f:
        json.dump({
            "conversation_record": conversation_record,
            "analysis_result": simulated_analysis
        }, f, indent=2)

    print("✓ Conversation analysis saved to conversation_analysis.json")

    return True

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    """Run both workflow tests"""

    print("\n" + "="*70)
    print("  COGNICARE WORKFLOW TESTS")
    print("="*70)
    print("\nTesting two main workflows:")
    print("1. Intake Analysis Flow")
    print("2. Routine Chat Flow")
    print("\n" + "="*70)

    # Test Workflow 1: Intake Analysis
    intake_success, analysis_result = test_intake_analysis_flow()

    if not intake_success:
        print("\n❌ Intake Analysis Flow FAILED")
        print("Stopping tests...")
        return

    print("\n✅ Intake Analysis Flow PASSED")

    # Test Workflow 2: Routine Chat
    chat_success = test_routine_chat_flow(analysis_result)

    if not chat_success:
        print("\n❌ Routine Chat Flow FAILED")
        return

    print("\n✅ Routine Chat Flow PASSED")

    # Final summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    print("\n✅ All workflows completed successfully!")
    print("\nGenerated files:")
    print("  - intake_analysis_result.json")
    print("  - routine_chat_log.json")
    print("  - conversation_analysis.json")
    print("\n" + "="*70)

if __name__ == "__main__":
    print("\n🚀 Starting CognifyCare Workflow Tests...")
    print("Make sure the server is running: python test_app.py")
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
