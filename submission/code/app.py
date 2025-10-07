import streamlit as st
import sqlite3
import json
import datetime
import os
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
st.set_page_config(page_title="SustainIQ", layout="wide")

# --- DATABASE SETUP ---
conn = sqlite3.connect("sustainability_feedback.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT,
    suggestion TEXT,
    impact_saved REAL,
    feedback TEXT,
    timestamp TEXT
)
""")
conn.commit()

# --- LOAD SYSTEM PROMPT ---
def load_system_prompt():
    try:
        with open("SustainabilityCoach-SystemPrompt.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        You are a Sustainability Coach. Your task is to analyze a user-provided action and suggest ONE alternative that is more sustainable, practical, and likely to be accepted by the user.
        Output strictly in JSON format with the following keys:
        original_action, suggestion, rationale, metrics {original_impact, suggested_impact}, impact_indicator, evaluation_status.
        Follow the rules and examples exactly as described.
        """

# --- HELPER FUNCTIONS ---
def clean_json_response(raw_output):
    """Clean the raw output to extract valid JSON"""
    # Remove markdown code blocks
    raw_output = re.sub(r'```json\s*', '', raw_output)
    raw_output = re.sub(r'```\s*$', '', raw_output)
    raw_output = raw_output.strip()
    
    # Try to find JSON object boundaries
    start_idx = raw_output.find('{')
    end_idx = raw_output.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = raw_output[start_idx:end_idx + 1]
        return json_str
    
    return raw_output

def get_llm_response(user_action: str):
    system_prompt = load_system_prompt()

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY"),
    )

    model = "gemini-2.0-flash-exp"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"{system_prompt}\n\nUser action: {user_action}"),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        temperature=0.4,
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        raw_output = response.text.strip()
        
        # Clean the response to extract JSON
        cleaned_output = clean_json_response(raw_output)
        
        try:
            parsed_json = json.loads(cleaned_output)
            return parsed_json
        except json.JSONDecodeError as e:
            # If still fails, try to extract JSON from the raw output
            try:
                # Look for JSON pattern in the text
                json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    parsed_json = json.loads(json_str)
                    return parsed_json
            except:
                pass
            
            return {"error": "Invalid JSON format", "raw_output": raw_output, "cleaned_output": cleaned_output}
    except Exception as e:
        return {"error": f"API call failed: {str(e)}"}

def log_feedback(user_input, suggestion, impact_saved, feedback):
    # Round impact_saved to 2 decimal places before saving
    impact_saved_rounded = round(impact_saved, 2)
    c.execute("INSERT INTO feedback (user_input, suggestion, impact_saved, feedback, timestamp) VALUES (?, ?, ?, ?, ?)",
              (user_input, suggestion, impact_saved_rounded, feedback, datetime.datetime.now().isoformat()))
    conn.commit()

def compute_total_score():
    df = conn.execute("SELECT feedback, impact_saved FROM feedback").fetchall()
    yes_points = sum([row[1] for row in df if row[0] == "yes"])
    total_queries = len(df)
    yes_count = len([r for r in df if r[0] == "yes"])
    no_count = total_queries - yes_count
    return yes_points, total_queries, yes_count, no_count

# --- ENHANCED UI ---
st.title("🌱 SustainIQ")

# User Input Section
st.markdown("### 📝 Describe your action or plan:")
user_action = st.text_area(
    "What are you planning to do?",
    placeholder="e.g., Driving to pick up takeout Thai food for dinner, about ten minutes away",
    height=100,
    key="user_input"
)

if st.button("🔍 Analyze Sustainability Impact", type="primary", use_container_width=True):
    if not user_action.strip():
        st.warning("Please enter an action first.")
    else:
        with st.spinner("🤖 Analyzing sustainability impact..."):
            output = get_llm_response(user_action)
        
        # Store the output in session state
        st.session_state['analysis_output'] = output
        st.session_state['user_action'] = user_action

# Display Results if analysis exists
if 'analysis_output' in st.session_state and 'error' not in st.session_state['analysis_output']:
    output = st.session_state['analysis_output']
    user_action = st.session_state['user_action']
    
    # User Input Display
    st.markdown("---")
    st.markdown("### 👤 **USER INPUT**")
    st.info(f"💭 {user_action}")
    
    # AI Response Display
    st.markdown("### 🤖 **AI RESPONSE**")
    
    # Suggestion Box
    if "suggestion" in output:
        st.markdown("**💡 Suggestion:**")
        st.success(output["suggestion"])
    
    # Rationale
    if "rationale" in output:
        st.markdown("**❓ Why?**")
        st.write(output["rationale"])
    
    # Impact Comparison
    if "metrics" in output and isinstance(output["metrics"], dict):
        st.markdown("### 📊 **Impact Comparison**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🔴 Current Impact:**")
            st.error(output["metrics"].get("original_impact", "Unable to estimate"))
        
        with col2:
            st.markdown("**🟢 Suggested Impact:**")
            st.success(output["metrics"].get("suggested_impact", "Unable to estimate"))
    
    # Impact Indicator
    if "impact_indicator" in output:
        impact_level = output["impact_indicator"]
        if impact_level == "high":
            st.markdown("**🎯 Impact: HIGH**")
            st.error("High Impact Change")
        elif impact_level == "medium":
            st.markdown("**🎯 Impact: MEDIUM**")
            st.warning("Medium Impact Change")
        else:
            st.markdown("**🎯 Impact: LOW**")
            st.info("Low Impact Change")
    
    # Evaluation Status
    if "evaluation_status" in output:
        status = output["evaluation_status"]
        if status == "needs_clarification":
            st.warning("⚠️ Needs more information")
        elif status == "already_sustainable":
            st.success("✅ Already sustainable!")
        elif status == "qualitative_only":
            st.info("ℹ️ Qualitative assessment only")
    
    # Feedback Section
    st.markdown("---")
    st.markdown("### 💬 **Was this suggestion helpful?**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, I'll go for it", use_container_width=True, key="yes_feedback"):
            # Calculate impact saved
            if "metrics" in output and isinstance(output["metrics"], dict):
                try:
                    orig = output["metrics"].get("original_impact", "0").split()[0]
                    sug = output["metrics"].get("suggested_impact", "0").split()[0]
                    impact_saved = round(float(orig) - float(sug), 2)
                except:
                    impact_saved = 0.0
            else:
                impact_saved = 0.0
            
            log_feedback(user_action, output.get("suggestion", ""), impact_saved, "yes")
            st.success("🌿 Feedback saved! Thank you for making a sustainable choice.")
            # Clear session state to show updated dashboard
            if 'analysis_output' in st.session_state:
                del st.session_state['analysis_output']
            st.rerun()
    
    with col2:
        if st.button("❌ No, not for me", use_container_width=True, key="no_feedback"):
            log_feedback(user_action, output.get("suggestion", ""), 0.0, "no")
            st.info("🌍 Feedback noted! Maybe next time.")
            # Clear session state to show updated dashboard
            if 'analysis_output' in st.session_state:
                del st.session_state['analysis_output']
            st.rerun()
    
    # JSON Toggle
    with st.expander("🔧 View Full JSON Response", expanded=False):
        st.json(output, expanded=True)

# Display error if exists
elif 'analysis_output' in st.session_state and 'error' in st.session_state['analysis_output']:
    output = st.session_state['analysis_output']
    st.error(f"❌ Error: {output.get('error', 'Unknown error occurred')}")
    if "raw_output" in output:
        st.text("Raw output:")
        st.code(output["raw_output"])
    if "cleaned_output" in output:
        st.text("Cleaned output:")
        st.code(output["cleaned_output"])

# --- DASHBOARD ---
st.markdown("---")
st.header("📊 Sustainability Dashboard")

score, total, yes_ct, no_ct = compute_total_score()

# Metrics in columns
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🌎 CO₂ Saved", f"{score:.2f} kg CO₂")
with col2:
    st.metric("✅ Positive Actions", f"{yes_ct} / {total}")
with col3:
    if total > 0:
        success_rate = (yes_ct / total) * 100
        st.metric("📈 Success Rate", f"{success_rate:.1f}%")

# Recent Feedback
recent = conn.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 5").fetchall()
if recent:
    st.markdown("### 📋 Recent Feedback")
    for r in recent:
        feedback_icon = "✅" if r[4] == "yes" else "❌"
        st.markdown(f"""
        **{feedback_icon} Action:** {r[1]}  
        **💡 Suggestion:** {r[2]}  
        **💾 Saved:** {r[3]:.2f} kg CO₂  
        ---
        """)
else:
    st.info("💡 No feedback yet. Try a few actions above to start building your sustainability score!")

# Footer
st.markdown("---")
st.markdown("🌱 *Making sustainable choices, one decision at a time*")
