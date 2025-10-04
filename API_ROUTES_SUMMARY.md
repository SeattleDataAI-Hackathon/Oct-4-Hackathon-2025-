# CuraLoop API Routes Summary

All routes have been integrated into `api/index.py` and `test_app.py` for deployment.

## 📋 Complete API Endpoints

### 1. Diagnosis & Treatment Planning
**Router:** `app.analysis.diagnosis_treatment_planning`
**Prefix:** `/api/analysis`

- `POST /api/analysis/direct` - Direct analysis with patient data
- `GET /api/analysis/health` - Health check for analysis module

### 2. Conversation Analysis (NEW ✨)
**Router:** `app.analysis.conversation_analyzer`
**Prefix:** `/api/conversation`

- `POST /api/conversation/analyze` - Analyze single conversation for symptom/mood changes
- `POST /api/conversation/analyze/batch` - Batch analyze multiple conversations
- `GET /api/conversation/health` - Health check for conversation analyzer

**Features:**
- Uses Claude AI to analyze patient conversations
- Detects significant symptom/mood changes
- Determines if doctor contact is needed
- Returns urgency level and recommended actions

### 3. Patient Intake
**Router:** `app.patient.intake`
**Prefix:** `/api/patient`

- `POST /api/patient/{patient_id}/intake/start` - Start intake session
- `POST /api/patient/{patient_id}/intake/reply` - Answer intake questions
- `GET /api/patient/{patient_id}/intake/state` - Get intake session state
- `POST /api/patient/{patient_id}/intake/analyze` - Analyze completed intake

### 4. Regular Chat (Daily Check-ins) (NEW ✨)
**Router:** `app.patient.regular_chat`
**Prefix:** `/api/patient`

- `POST /api/patient/{patient_id}/chatbot/initialize` - Initialize chatbot with treatment plan
- `POST /api/patient/{patient_id}/chat/start` - Start chat session (daily_check_in, treatment_progress, etc.)
- `POST /api/patient/chat/message` - Send patient message and get bot response
- `POST /api/patient/chat/end` - End session and get comprehensive JSON summary
- `GET /api/patient/{patient_id}/chat/history` - Get chat history
- `GET /api/patient/{patient_id}/chatbot/status` - Get chatbot configuration status

**Features:**
- Executes treatment plan through conversations
- Multiple chat types: daily_check_in, treatment_progress, cognitive_engagement, crisis_support
- Tracks sentiment, engagement, and activity completion
- Compiles all interactions into JSON

### 5. Root Endpoints

- `GET /` - API information and endpoint list
- `GET /health` - Health check
- `GET /docs` - Auto-generated API documentation (Swagger UI)
- `GET /openapi.json` - OpenAPI schema

## 🔄 Complete Workflow

### Patient Onboarding Flow
```
1. POST /api/patient/{id}/intake/start
2. POST /api/patient/{id}/intake/reply (x34 questions)
3. GET /api/patient/{id}/intake/state
4. POST /api/patient/{id}/intake/analyze
   → Returns: patient_portfolio, diagnosis_analysis, treatment_plan, chatbot_config
```

### Daily Chat Flow
```
1. POST /api/patient/{id}/chatbot/initialize
   - Input: patient_portfolio, treatment_plan, chatbot_config
2. POST /api/patient/{id}/chat/start
   - Input: chat_type (daily_check_in, treatment_progress, etc.)
3. POST /api/patient/chat/message (repeat for conversation)
   - Input: session_id, patient_message
   - Output: chatbot_message, follow_up_questions, activity_completed
4. POST /api/patient/chat/end
   - Output: Complete JSON with all interactions, metrics, completed_activities
```

### Conversation Analysis Flow (Optional)
```
1. POST /api/conversation/analyze
   - Input: conversation_record from chat session
   - Output: mood_assessment, symptom_assessment, contact_doctor_decision
```

## 📦 Dependencies

Added to `requirements.txt`:
- `anthropic` - For conversation analysis with Claude AI
- `uvicorn` - ASGI server for FastAPI

## 🚀 Deployment Files

### Production (Vercel)
**File:** `api/index.py`
- Configured for Vercel serverless deployment
- All routers included
- CORS enabled

### Testing/Development
**File:** `test_app.py`
- Local development server
- Includes all routers
- Additional test endpoints for intake analysis

## ✅ Testing

Run complete workflow test:
```bash
python test_app.py  # Start server
python test_chatbot.py  # Run workflow test
```

Generates:
- `intake_analysis_result.json`
- `routine_chat_log.json`
- `conversation_analysis.json`

## 📊 Data Flow

```
Intake Questions (intake.py)
    ↓
Patient Data → Alzheimer's Predictor (diagnosis_treatment_planning.py)
    ↓
Treatment Plan + Chatbot Config
    ↓
Daily Check-in Chatbot (regular_chat.py)
    ↓
Conversation Record → Conversation Analyzer (conversation_analyzer.py)
    ↓
Doctor Contact Decision + Recommendations
```

## 🔑 Environment Variables

**Required for LLM features:**
- `CLAUDE_API_KEY` - Claude API key for diagnosis planning and conversation analysis
- `ANTHROPIC_API_KEY` - Alternative name (also supported)

**How to set:**
```bash
# Option 1: Set in .env file (recommended)
echo "CLAUDE_API_KEY=your-key-here" > .env

# Option 2: Export in shell
export CLAUDE_API_KEY=sk-ant-api03-...

# Option 3: Provide per request in API call
```

## 📝 Notes

- All routers use consistent `/api/` prefix
- Patient-specific routes use `{patient_id}` path parameter
- Session-based routes use `session_id` in request body
- All responses return structured JSON
- Error handling included with appropriate HTTP status codes
