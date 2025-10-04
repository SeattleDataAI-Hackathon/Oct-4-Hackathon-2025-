import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from dotenv import load_dotenv
from openai import OpenAI

# --- Load environment variables from .env ---
load_dotenv()

# --- Initialize OpenAI client ---
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Load trained model and scaler ---
model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")

# --- Disease names and descriptions ---
disease_info = {
    0: {"name": "Healthy", "description": "No major chronic conditions detected. Maintain a balanced lifestyle to stay healthy."},
    1: {"name": "Diabetes", "description": "Elevated glucose levels detected. Monitor diet, exercise regularly, and consult your doctor."},
    2: {"name": "Cardiovascular Disorder", "description": "Potential risk of heart or vascular conditions. Keep track of blood pressure, cholesterol, and physical activity."},
    3: {"name": "Cancer", "description": "Risk factors indicate possible cancer conditions. Regular screenings and medical consultation are advised."},
    4: {"name": "Multi-condition Cases", "description": "Multiple risk factors detected. Follow a comprehensive health plan and consult a healthcare professional."}
}

# --- Minimal chatbot responses (fallback) ---
chat_responses = {
    "exercise": "Regular exercise helps reduce risk for multiple diseases.",
    "diet": "A balanced diet can reduce cholesterol and glucose levels.",
    "blood pressure": "Monitoring your blood pressure regularly is important.",
    "cholesterol": "Check cholesterol levels regularly and maintain a healthy diet.",
    "glucose": "Keep glucose levels in check and maintain balanced meals."
}

def generate_recommendations(disease_name, description):
    prompt = f"""
    The user has been predicted to have: {disease_name}.
    Description: {description}.
    Suggest 3 practical lifestyle recommendations for this user.
    Keep them short, actionable, and easy to understand.
    Format each recommendation as a bullet point.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",   # you can switch to gpt-4 or gpt-3.5 if needed
        messages=[
            {"role": "system", "content": "You are a helpful health assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.7
    )

    text = response.choices[0].message.content.strip()

    # Clean and split into neat bullet points
    recs = [
        line.strip("-•1234567890. ").strip()
        for line in text.split("\n")
        if line.strip()
    ]
    return recs

# --- Streamlit UI ---
st.title("Freakquency - Disease Risk Prediction & AI Recommendations")
st.write("Fill out the questionnaire below to see your predicted disease and AI-generated lifestyle recommendations.")

# --- Streamlit Form ---
with st.form("health_form"):
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=25.0)
    blood_pressure = st.number_input("Blood Pressure", min_value=50, max_value=200, value=120)
    cholesterol_level = st.number_input("Cholesterol Level", min_value=100, max_value=400, value=180)
    glucose_level = st.number_input("Glucose Level", min_value=50, max_value=300, value=100)
    physical_activity = st.number_input("Physical Activity (hours/week)", min_value=0, max_value=50, value=2)
    smoking_status = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
    alcohol_intake = st.selectbox("Alcohol Intake", ["None", "Moderate", "High"])
    family_history = st.selectbox("Family History of Disease?", ["No", "Yes"])
    
    submit_button = st.form_submit_button(label="Predict")

# --- Preprocess and Predict ---
if submit_button:
    # Map categorical values to numeric
    gender_map = {"Male": 0, "Female": 1, "Other": 2}
    smoking_map = {"Never": 0, "Former": 1, "Current": 2}
    alcohol_map = {"None": 0, "Moderate": 1, "High": 2}
    family_map = {"No": 0, "Yes": 1}
    
    input_data = np.array([[ 
        age,
        gender_map[gender],
        bmi,
        blood_pressure,
        cholesterol_level,
        glucose_level,
        physical_activity,
        smoking_map[smoking_status],
        alcohol_map[alcohol_intake],
        family_map[family_history]
    ]])
    
    # Scale features
    input_scaled = scaler.transform(input_data)
    
    # Predict disease class
    prediction = model.predict(input_scaled)[0]
    disease = disease_info[prediction]
    
    # Display prediction in a card-like format
    with st.container():
        st.markdown("### Predicted Disease Category")
        st.markdown(f"**{disease['name']}**")
        st.write(disease["description"])
        
        st.markdown("### AI-Generated Lifestyle Recommendations")
        ai_recs = generate_recommendations(disease['name'], disease['description'])
        for rec in ai_recs:
            st.write(f"- {rec}")

# --- Minimal Chatbot ---
st.subheader("Ask a health-related question:")
user_input = st.text_input("Type your question here...")

if user_input:
    response_given = False
    for key, resp in chat_responses.items():
        if key in user_input.lower():
            st.write(resp)
            response_given = True
            break
    if not response_given:
        st.write("Sorry, I don't have advice for that yet. Try asking about exercise, diet, or blood pressure.")
