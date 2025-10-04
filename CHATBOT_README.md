# Regular Chat Chatbot - Daily Check-in System

## Overview

The Regular Chat Chatbot is a comprehensive daily check-in system that executes treatment plans through conversational interactions with Alzheimer's patients. It uses patient portfolio information and treatment plans generated from `diagnosis_treatment_planning.py` to provide personalized, empathetic support.

## Features

### Core Capabilities
- ✅ **Treatment Plan Execution**: Converts treatment plan items into conversational activities
- ✅ **Daily Check-ins**: Structured conversations covering medication, lifestyle, and wellness
- ✅ **Personalized Configuration**: Adapts communication style based on cognitive level (MMSE scores)
- ✅ **Multiple Chat Types**: Daily check-in, treatment progress, cognitive engagement, crisis support
- ✅ **Sentiment Analysis**: Tracks patient mood and engagement throughout conversations
- ✅ **Comprehensive Logging**: All interactions compiled into JSON format
- ✅ **Activity Tracking**: Monitors completion of treatment activities with metrics

### Chat Types
1. **Daily Check-in** - Quick wellness checks covering medication, sleep, mood, energy
2. **Treatment Progress** - Weekly review of treatment plan adherence
3. **Cognitive Engagement** - Memory exercises and cognitive stimulation
4. **Crisis Support** - Emergency support and safety checks

## API Endpoints

### 1. Initialize Chatbot
```http
POST /api/patient/{patient_id}/chatbot/initialize
```

**Request Body:**
```json
{
  "patient_id": 12345,
  "patient_portfolio": { /* from diagnosis_treatment_planning */ },
  "treatment_plan": { /* from diagnosis_treatment_planning */ },
  "chatbot_config": { /* from diagnosis_treatment_planning */ }
}
```

**Response:**
```json
{
  "patient_id": 12345,
  "chatbot_id": "a1b2c3d4e5f6",
  "status": "active",
  "message": "Chatbot initialized successfully for patient 12345"
}
```

### 2. Start Chat Session
```http
POST /api/patient/{patient_id}/chat/start
```

**Request Body:**
```json
{
  "patient_id": 12345,
  "chat_type": "daily_check_in"
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "patient_id": 12345,
  "chatbot_message": "Good morning! How are you feeling today?",
  "chat_type": "daily_check_in",
  "conversation_context": {
    "initial_message": "Good morning! How are you feeling today?",
    "topics": ["Mood and energy level", "Medication adherence", "Sleep quality"],
    "expected_duration": "5-10 minutes",
    "frequency": "daily",
    "purpose": "Daily wellness and treatment adherence check"
  }
}
```

### 3. Send Chat Message
```http
POST /api/patient/chat/message
```

**Request Body:**
```json
{
  "session_id": "abc123",
  "patient_message": "I'm feeling good today, took my medication"
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "chatbot_message": "That's wonderful! I'm glad to hear about your progress...",
  "follow_up_questions": [
    "How are you feeling after taking your medication?",
    "Are you experiencing any side effects?"
  ],
  "activity_completed": true,
  "conversation_complete": false,
  "next_steps": ["Move to next activity", "Continue check-in"]
}
```

### 4. End Chat Session
```http
POST /api/patient/chat/end
```

**Request Body:**
```json
{
  "session_id": "abc123"
}
```

**Response:**
```json
{
  "session_id": "abc123",
  "patient_id": 12345,
  "chat_summary": {
    "session_id": "abc123",
    "chat_type": "daily_check_in",
    "duration_minutes": 8.5,
    "total_activities": 5,
    "total_interactions": 12,
    "sentiment_summary": {
      "positive": 8,
      "negative": 2,
      "neutral": 2
    },
    "completed_activities": [
      {
        "title": "Medication adherence check",
        "completion_time": "2025-10-04T10:15:23Z",
        "metrics": {
          "sentiment": "positive",
          "engagement_level": "high",
          "response_length": 45
        }
      }
    ],
    "overall_engagement": "high",
    "recommendations": []
  },
  "interactions": [
    {
      "timestamp": "2025-10-04T10:12:00Z",
      "patient_message": "I'm feeling good today",
      "chatbot_response": "That's wonderful! I'm glad to hear...",
      "response_analysis": {
        "activity_completed": true,
        "sentiment": "positive"
      }
    }
  ],
  "completed_activities": [
    "Medication adherence check",
    "Sleep quality assessment",
    "Energy level check"
  ],
  "metrics": {
    "session_duration_minutes": 8.5,
    "total_activities_completed": 5,
    "total_interactions": 12,
    "engagement_score": "high",
    "sentiment_distribution": {
      "positive": 8,
      "negative": 2,
      "neutral": 2
    }
  }
}
```

### 5. Get Chat History
```http
GET /api/patient/{patient_id}/chat/history?limit=10
```

**Response:**
```json
{
  "patient_id": 12345,
  "total_sessions": 25,
  "sessions": [
    {
      "session_id": "abc123",
      "chat_type": "daily_check_in",
      "created_at": "2025-10-04T10:00:00Z",
      "status": "completed",
      "completed_activities_count": 5,
      "total_interactions": 12,
      "summary": { /* chat summary */ }
    }
  ]
}
```

### 6. Get Chatbot Status
```http
GET /api/patient/{patient_id}/chatbot/status
```

**Response:**
```json
{
  "patient_id": 12345,
  "chatbot_id": "a1b2c3d4e5f6",
  "status": "active",
  "created_at": "2025-10-04T09:00:00Z",
  "total_activities_tracked": 15,
  "treatment_goals_count": 12,
  "monitoring_schedule": {
    "cognitive_assessment": "Every 6 months",
    "medical_follow_up": "Every 3 months",
    "lifestyle_review": "Monthly",
    "caregiver_check_in": "Weekly",
    "check_in_frequency": "daily"
  }
}
```

## Usage Example

### Complete Workflow

```python
import requests

BASE_URL = "http://localhost:8000"
patient_id = 12345

# 1. Get analysis from intake
response = requests.post(
    f"{BASE_URL}/api/patient/{patient_id}/intake/analyze",
    json={"patient_id": patient_id, "intake_data": intake_data}
)
analysis = response.json()

# 2. Initialize chatbot
requests.post(
    f"{BASE_URL}/api/patient/{patient_id}/chatbot/initialize",
    json={
        "patient_id": patient_id,
        "patient_portfolio": analysis["patient_portfolio"],
        "treatment_plan": analysis["treatment_plan"],
        "chatbot_config": analysis["companion_chatbot_config"]
    }
)

# 3. Start chat session
response = requests.post(
    f"{BASE_URL}/api/patient/{patient_id}/chat/start",
    json={"patient_id": patient_id, "chat_type": "daily_check_in"}
)
session = response.json()

# 4. Send messages
response = requests.post(
    f"{BASE_URL}/api/patient/chat/message",
    json={
        "session_id": session["session_id"],
        "patient_message": "I'm feeling good today"
    }
)

# 5. End session and get summary
response = requests.post(
    f"{BASE_URL}/api/patient/chat/end",
    json={"session_id": session["session_id"]}
)
summary = response.json()
```

## Testing

Run the comprehensive test script:

```bash
# Start the server
python test_app.py

# In another terminal, run the test
python test_chatbot.py
```

The test script will:
1. Analyze patient intake data
2. Initialize chatbot with treatment plan
3. Start a daily check-in session
4. Simulate a conversation
5. End session and retrieve JSON summary
6. Save full interaction log to `chat_session_log.json`

## Chatbot Configuration

The chatbot adapts based on the patient's cognitive level (MMSE score):

### Severe Cognitive Impairment (MMSE < 18)
- Very simple language with frequent repetition
- Visual cues essential
- Limited to 3 activities per category
- All activities simplified to "easy" difficulty

### Mild Cognitive Impairment (18 ≤ MMSE < 24)
- Simple language with occasional repetition
- Moderate cognitive exercises
- Limited to 5 activities per category

### Normal Cognition (MMSE ≥ 24)
- Standard communication
- Full range of activities

## Activity Types

The chatbot handles these activity categories:
- **Medication**: Reminders and adherence tracking
- **Physical Activity**: Exercise encouragement
- **Nutrition**: Diet quality and meal planning
- **Sleep**: Sleep quality assessment
- **Cognitive**: Memory exercises and brain games
- **Social**: Social interaction support
- **Medical**: Appointment tracking
- **Safety**: Safety checks and emergency support

## Metrics Tracked

### Per Activity:
- Sentiment (positive/negative/neutral)
- Engagement level (high/medium/low)
- Response length
- Completion status

### Per Session:
- Duration
- Total activities completed
- Total interactions
- Overall engagement score
- Sentiment distribution
- Recommendations for improvement

## Integration with Treatment Planning

The chatbot directly executes treatment plans from `diagnosis_treatment_planning.py`:

```python
# Treatment plan structure
treatment_plan = {
    "immediate_actions": [...],
    "lifestyle_interventions": [...],
    "medical_management": [...],
    "support_services": [...],
    "monitoring_schedule": {...}
}

# Converted to chat activities with:
# - chat_prompts
# - frequency (daily/weekly/monthly)
# - difficulty (easy/medium/hard)
# - success_metrics
# - follow_up_questions
```

## File Structure

```
app/patient/regular_chat.py - Main chatbot implementation
test_chatbot.py             - Comprehensive test script
chat_session_log.json       - Generated interaction logs
```

## Next Steps

To extend functionality:
1. Add voice interaction support
2. Implement reminder scheduling
3. Add caregiver notification system
4. Integrate with wearable devices
5. Add multimedia support (images, videos)
6. Implement emotion detection from text
7. Add multi-language support
