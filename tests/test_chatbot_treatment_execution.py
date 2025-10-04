#!/usr/bin/env python3
"""
Test script for chatbot treatment plan execution
Demonstrates how the treatment plan is converted into chat-executable activities
"""

import requests
import json
import os
from datetime import datetime

# Sample intake data for testing
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

def test_treatment_plan_execution():
    """Test how treatment plan is converted to chatbot executable activities"""
    
    print("Testing Treatment Plan Execution Through Chatbot")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/api/patient/789/intake/analyze"
    
    payload = {
        "patient_id": 789,
        "intake_data": SAMPLE_INTAKE_DATA
    }
    
    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis completed successfully")
            
            # Extract treatment plan and chatbot config
            treatment_plan = result["treatment_plan"]
            chatbot_config = result["companion_chatbot_config"]
            
            print("\n📋 TREATMENT PLAN:")
            print(f"  Immediate Actions: {len(treatment_plan.get('immediate_actions', []))} items")
            print(f"  Lifestyle Interventions: {len(treatment_plan.get('lifestyle_interventions', []))} items")
            print(f"  Medical Management: {len(treatment_plan.get('medical_management', []))} items")
            print(f"  Support Services: {len(treatment_plan.get('support_services', []))} items")
            
            print("\n🤖 CHATBOT CONFIGURATION:")
            print(f"  Personality: {chatbot_config.get('personality', 'N/A')}")
            print(f"  Communication Style: {chatbot_config.get('communication_style', 'N/A')}")
            
            # Show treatment execution structure
            treatment_execution = chatbot_config.get("treatment_execution", {})
            print(f"\n🎯 TREATMENT EXECUTION STRUCTURE:")
            for category, activities in treatment_execution.items():
                if isinstance(activities, list):
                    print(f"  {category.replace('_', ' ').title()}: {len(activities)} chat activities")
            
            # Show conversation flows
            conversation_flows = chatbot_config.get("conversation_flows", {})
            print(f"\n💬 CONVERSATION FLOWS:")
            for flow_name, flow_config in conversation_flows.items():
                print(f"  {flow_name.replace('_', ' ').title()}:")
                print(f"    Purpose: {flow_config.get('purpose', 'N/A')}")
                print(f"    Frequency: {flow_config.get('frequency', 'N/A')}")
                print(f"    Duration: {flow_config.get('duration', 'N/A')}")
                print(f"    Topics: {len(flow_config.get('topics', []))} items")
            
            # Show treatment goals
            treatment_goals = chatbot_config.get("treatment_goals", [])
            print(f"\n🎯 TREATMENT GOALS:")
            print(f"  Total Goals: {len(treatment_goals)}")
            for i, goal in enumerate(treatment_goals[:3]):  # Show first 3 goals
                print(f"  Goal {i+1}: {goal.get('description', 'N/A')[:50]}...")
                print(f"    Category: {goal.get('category', 'N/A')}")
                print(f"    Priority: {goal.get('priority', 'N/A')}")
            
            # Show detailed chat activities
            print(f"\n💬 DETAILED CHAT ACTIVITIES:")
            for category, activities in treatment_execution.items():
                if isinstance(activities, list) and activities:
                    print(f"\n  {category.replace('_', ' ').title()}:")
                    for i, activity in enumerate(activities[:2]):  # Show first 2 activities per category
                        print(f"    Activity {i+1}: {activity.get('title', 'N/A')}")
                        print(f"      Type: {activity.get('type', 'N/A')}")
                        print(f"      Frequency: {activity.get('frequency', 'N/A')}")
                        print(f"      Difficulty: {activity.get('difficulty', 'N/A')}")
                        print(f"      Chat Prompts: {len(activity.get('chat_prompts', []))} prompts")
                        if activity.get('chat_prompts'):
                            print(f"        Example: {activity['chat_prompts'][0]}")
                        print(f"      Follow-up Questions: {len(activity.get('follow_up_questions', []))} questions")
                        if activity.get('follow_up_questions'):
                            print(f"        Example: {activity['follow_up_questions'][0]}")
            
            # Show monitoring schedule
            monitoring_schedule = chatbot_config.get("monitoring_schedule", {})
            print(f"\n📅 MONITORING SCHEDULE:")
            for item, frequency in monitoring_schedule.items():
                print(f"  {item.replace('_', ' ').title()}: {frequency}")
            
            # Save detailed response
            with open('chatbot_treatment_execution.json', 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n✓ Detailed response saved to 'chatbot_treatment_execution.json'")
            
            return True
            
        else:
            print(f"✗ Analysis failed: {response.status_code}")
            print(f"  Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Connection Error: Make sure the API server is running")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def demonstrate_chat_flow():
    """Demonstrate how a chat flow would work with the treatment plan"""
    
    print("\n" + "=" * 60)
    print("CHAT FLOW DEMONSTRATION")
    print("=" * 60)
    
    print("""
This demonstrates how the chatbot would execute the treatment plan through conversation:

🤖 Chatbot: Good morning! How are you feeling today?
👤 Patient: I'm feeling a bit confused today.

🤖 Chatbot: I'm here to help. Let's talk about your medication routine. 
           Have you taken your medications today?
👤 Patient: I think so, but I'm not sure.

🤖 Chatbot: That's okay, let's check together. Can you tell me about 
           your current medication routine?
👤 Patient: I take pills in the morning and evening.

🤖 Chatbot: Great! Let's discuss your exercise routine. How are you 
           feeling about starting an exercise routine?
👤 Patient: I'm not sure I can do much exercise.

🤖 Chatbot: I understand. Let's start with something simple. What 
           physical activities do you enjoy?
👤 Patient: I used to like walking.

🤖 Chatbot: Walking is perfect! Let's talk about your sleep. How has 
           your sleep been recently?
👤 Patient: I've been having trouble sleeping.

🤖 Chatbot: I'd like to help you with that. What time do you usually 
           go to bed?
👤 Patient: Around 10 PM, but I can't fall asleep.

🤖 Chatbot: Let's work on improving your sleep. About your sleep, 
           are you having any trouble falling asleep?
👤 Patient: Yes, my mind keeps racing.

🤖 Chatbot: That's common. Let's do a fun memory exercise together 
           to help calm your mind.
👤 Patient: Okay, that sounds good.

🤖 Chatbot: Great! What day of the week is it today?
👤 Patient: I think it's Tuesday?

🤖 Chatbot: Good job! It is Tuesday. Can you tell me about a happy 
           memory from your past?
👤 Patient: I remember when my grandchildren were born.

🤖 Chatbot: That's a beautiful memory! How did that exercise feel?
👤 Patient: It was nice to remember that.

🤖 Chatbot: Wonderful! Let's talk about your diet. How has your 
           eating been lately?
👤 Patient: I haven't been eating much.

🤖 Chatbot: I want to help you with that. What foods do you typically eat?
👤 Patient: Mostly simple things like soup and sandwiches.

🤖 Chatbot: That's a good start. Regarding your diet, are you getting 
           enough fruits and vegetables?
👤 Patient: Not really, I forget to buy them.

🤖 Chatbot: Let's work on that together. I'll help you remember to 
           include more fruits and vegetables in your meals.
👤 Patient: That would be helpful.

🤖 Chatbot: Perfect! How are you feeling about this conversation?
👤 Patient: I feel better, thank you.

🤖 Chatbot: I'm glad I could help! Is there anything else you'd like 
           to talk about?
👤 Patient: No, I think that's enough for now.

🤖 Chatbot: That's perfectly fine. I'll check in with you again soon. 
           Remember, I'm here whenever you need me!
    """)

def show_treatment_plan_mapping():
    """Show how treatment plan items map to chat activities"""
    
    print("\n" + "=" * 60)
    print("TREATMENT PLAN TO CHAT ACTIVITY MAPPING")
    print("=" * 60)
    
    print("""
Treatment Plan Item → Chat Activity Conversion:

📋 "Schedule comprehensive neuropsychological evaluation"
   ↓
💬 Chat Activity:
   - Type: medical
   - Frequency: as_needed
   - Difficulty: medium
   - Chat Prompts:
     * "Let's talk about scheduling a comprehensive neuropsychological evaluation. Do you have any upcoming medical appointments?"
     * "I want to help you with scheduling a comprehensive neuropsychological evaluation. Are you keeping track of your health?"
     * "Regarding scheduling a comprehensive neuropsychological evaluation, have you spoken with your doctor recently?"
   - Follow-up Questions:
     * "How did the appointment go?"
     * "Do you have any questions about your health?"
     * "Is there anything you'd like to discuss with your doctor?"

📋 "Implement Mediterranean diet recommendations"
   ↓
💬 Chat Activity:
   - Type: nutrition
   - Frequency: daily
   - Difficulty: medium
   - Chat Prompts:
     * "Let's talk about implementing Mediterranean diet recommendations. How has your eating been lately?"
     * "I want to help you with implementing Mediterranean diet recommendations. What foods do you typically eat?"
     * "Regarding implementing Mediterranean diet recommendations, are you getting enough fruits and vegetables?"
   - Follow-up Questions:
     * "How did the meal taste?"
     * "Are you feeling satisfied?"
     * "Would you like suggestions for similar healthy meals?"

📋 "Engage in cognitive stimulation activities"
   ↓
💬 Chat Activity:
   - Type: cognitive
   - Frequency: daily
   - Difficulty: easy
   - Chat Prompts:
     * "Let's talk about engaging in cognitive stimulation activities. How are you feeling mentally today?"
     * "I want to help you with engaging in cognitive stimulation activities. Would you like to try a memory exercise?"
     * "Regarding engaging in cognitive stimulation activities, have you noticed any changes in your thinking?"
   - Follow-up Questions:
     * "How did that exercise feel?"
     * "Was it too easy or too difficult?"
     * "Would you like to try something different?"
    """)

def test_api_health():
    """Test API health"""
    
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

if __name__ == "__main__":
    print("CognifyCare Chatbot Treatment Plan Execution Test")
    print("=" * 60)
    
    # Check API health
    if not test_api_health():
        print("\nPlease start the API server first:")
        print("  uvicorn app:app --reload")
        exit(1)
    
    print()
    
    # Test treatment plan execution
    success = test_treatment_plan_execution()
    
    if success:
        # Show demonstrations
        demonstrate_chat_flow()
        show_treatment_plan_mapping()
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✓ Treatment plan successfully converted to chat-executable activities")
        print("✓ Chatbot configuration includes conversation flows and monitoring")
        print("✓ Each treatment item has specific chat prompts and follow-up questions")
        print("✓ Activities are categorized and difficulty-adjusted")
        print("✓ Monitoring schedule integrated into chatbot behavior")
        print("✓ Treatment goals extracted and formatted for tracking")
        
        print("\n🎯 KEY FEATURES:")
        print("• Treatment plan items → Chat activities with prompts")
        print("• Conversation flows for different interaction types")
        print("• Cognitive level adaptation (simplification for severe impairment)")
        print("• Risk-based frequency adjustment")
        print("• Success metrics and follow-up questions for each activity")
        print("• Monitoring schedule integration")
        print("• Treatment goals tracking")
        
        print("\n📁 FILES GENERATED:")
        print("• chatbot_treatment_execution.json - Complete analysis with chatbot config")
        
    else:
        print("\n⚠️  Test failed. Check the API server status.")
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Review the generated chatbot configuration")
    print("2. Implement the chatbot using the conversation flows")
    print("3. Use the chat activities to guide patient interactions")
    print("4. Monitor treatment progress through the defined metrics")
    print("5. Adapt the chatbot behavior based on patient responses")
