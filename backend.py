from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import os
from openai import OpenAI

try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

app = FastAPI(title="CarePath API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "common_disorders_dataset_full.csv")
df = pd.read_csv(csv_path)

# Global client (will be initialized when API key is set)
client = None
if OPENAI_API_KEY and OPENAI_API_KEY != "paste-your-api-key-here":
    client = OpenAI(api_key=OPENAI_API_KEY)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message]

class DiagnoseRequest(BaseModel):
    conversation_history: List[Message]

def get_system_prompt():
    return f"""You are CarePath, a medical triage assistant that helps diagnose health conditions.

Your role:
1. Have a natural conversation to understand the patient's symptoms
2. Ask follow-up questions to gather more details
3. Ask about age, gender, and lifestyle factors when relevant
4. Be empathetic and professional

Available disorders in database: {len(df)} conditions

Keep responses concise and focused. Ask one or two questions at a time.
"""

def extract_symptoms_from_conversation(conversation_history: List[Message]):
    """Extract symptoms from conversation history"""
    conv_text = ""
    for msg in conversation_history:
        if msg.role == 'user':
            conv_text += f"Patient: {msg.content}\n"
        elif msg.role == 'assistant':
            conv_text += f"Assistant: {msg.content}\n"

    extraction_prompt = f"""Based on this conversation, extract:
1. All mentioned symptoms (as a comma-separated list)
2. Age group (Children/Adolescents/Adults 20-40/Adults 40+/Elderly)
3. Gender (Male/Female/Equal)
4. Lifestyle factors mentioned (Stress/Obesity/Smoking/Alcohol/Sedentary lifestyle/Trauma history)

Conversation:
{conv_text}

Return in this exact format:
SYMPTOMS: symptom1, symptom2, symptom3
AGE_GROUP: age group
GENDER: gender
LIFESTYLE: factor1, factor2
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": extraction_prompt}],
        temperature=0.3,
        max_tokens=200
    )

    return parse_extraction(response.choices[0].message.content)

def parse_extraction(extraction_text: str):
    """Parse extracted information"""
    lines = extraction_text.strip().split('\n')
    info = {}

    for line in lines:
        if line.startswith('SYMPTOMS:'):
            info['symptoms'] = [s.strip().lower() for s in line.replace('SYMPTOMS:', '').split(',')]
        elif line.startswith('AGE_GROUP:'):
            info['age_group'] = line.replace('AGE_GROUP:', '').strip()
        elif line.startswith('GENDER:'):
            info['gender'] = line.replace('GENDER:', '').strip()
        elif line.startswith('LIFESTYLE:'):
            info['lifestyle'] = [s.strip() for s in line.replace('LIFESTYLE:', '').split(',') if s.strip()]

    return info

def match_symptoms(patient_info: dict):
    """Match symptoms against disorder database"""
    matches = []
    patient_symptoms = set(patient_info.get('symptoms', []))

    for idx, row in df.iterrows():
        disorder_symptoms = set([s.strip().lower() for s in row['Common_Symptoms'].split(',')])

        # Calculate symptom overlap
        overlap = patient_symptoms.intersection(disorder_symptoms)
        match_score = len(overlap) / len(disorder_symptoms) if len(disorder_symptoms) > 0 else 0

        # Partial matching for flexibility
        partial_matches = sum(
            1 for ps in patient_symptoms
            for ds in disorder_symptoms
            if ps in ds or ds in ps
        )

        if match_score > 0 or partial_matches > 0:
            matches.append({
                'disorder_id': row['Disorder_ID'],
                'disorder_name': row['Disorder_Name'],
                'category': row['Category'],
                'match_score': match_score,
                'partial_matches': partial_matches,
                'symptoms': row['Common_Symptoms'],
                'specialist': row['Recommended_Specialist'],
                'emergency': row['Emergency_Flag'],
                'followup_questions': row['Suggested_Followup_Questions']
            })

    # Sort by match score and partial matches
    matches.sort(key=lambda x: (x['match_score'], x['partial_matches']), reverse=True)

    return matches[:5]

def generate_recommendation(matches: List[dict]):
    """Generate doctor recommendation based on matches"""
    if not matches:
        return {
            'possible_condition': 'Unable to determine',
            'category': 'Unknown',
            'confidence': '0%',
            'recommended_specialist': 'General Practitioner',
            'urgency_level': 'Normal',
            'action': 'Please consult a General Practitioner for evaluation',
            'emergency': False,
            'other_possibilities': []
        }

    top_match = matches[0]

    # Determine urgency level
    if top_match['emergency'] == 'Yes':
        recommended_action = 'EMERGENCY: Seek immediate medical attention at the nearest emergency room'
        urgency = 'Emergency'
    elif top_match['match_score'] > 0.5:
        recommended_action = f"Urgent Care: Schedule an appointment with a {top_match['specialist']} soon"
        urgency = 'Urgent Care'
    else:
        recommended_action = f"Normal: Consider consulting a {top_match['specialist']} for evaluation"
        urgency = 'Normal'

    return {
        'possible_condition': top_match['disorder_name'],
        'category': top_match['category'],
        'confidence': f"{top_match['match_score']*100:.1f}%",
        'recommended_specialist': top_match['specialist'],
        'urgency_level': urgency,
        'action': recommended_action,
        'emergency': top_match['emergency'] == 'Yes',
        'other_possibilities': [m['disorder_name'] for m in matches[1:3]] if len(matches) > 1 else []
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    try:
        conversation = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        conversation.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": get_system_prompt()}
            ] + conversation,
            temperature=0.7,
            max_tokens=300
        )

        assistant_message = response.choices[0].message.content

        # Calculate confidence for auto-diagnosis
        if len(request.conversation_history) >= 6:  # After 3 exchanges
            try:
                patient_info = extract_symptoms_from_conversation(request.conversation_history)
                matches = match_symptoms(patient_info)
                if matches and matches[0]['match_score'] >= 0.9:
                    return {
                        "response": assistant_message,
                        "confidence": matches[0]['match_score'] * 100
                    }
            except:
                pass

        return {
            "response": assistant_message,
            "confidence": None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/diagnose")
async def diagnose(request: DiagnoseRequest):
    """Generate diagnosis based on conversation"""
    try:
        patient_info = extract_symptoms_from_conversation(request.conversation_history)
        matches = match_symptoms(patient_info)
        recommendation = generate_recommendation(matches)
        return recommendation

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "CarePath API is running"}

@app.get("/check-api-key")
async def check_api_key():
    """Check if API key is configured"""
    return {"has_api_key": client is not None}

class ApiKeyRequest(BaseModel):
    api_key: str

@app.post("/set-api-key")
async def set_api_key(request: ApiKeyRequest):
    """Save API key to config.py"""
    global client, OPENAI_API_KEY

    try:
        # Validate the key format
        if not request.api_key.startswith('sk-'):
            raise HTTPException(status_code=400, detail="Invalid API key format")

        # Write to config.py
        config_path = os.path.join(script_dir, "config.py")
        config_content = f'''# CarePath Configuration File
# IMPORTANT: Keep this file secure and never commit it to version control

# OpenAI API Key
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "{request.api_key}"
'''

        with open(config_path, 'w') as f:
            f.write(config_content)

        # Update the global client
        OPENAI_API_KEY = request.api_key
        client = OpenAI(api_key=OPENAI_API_KEY)

        return {"success": True, "message": "API key saved successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
