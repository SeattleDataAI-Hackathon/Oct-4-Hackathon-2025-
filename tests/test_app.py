#!/usr/bin/env python3
"""
Minimal FastAPI app to test the app folder endpoints
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.analysis import router as analysis_router, configure_llm
from app.analysis.conversation_analyzer import router as conversation_router
from app.patient.intake import router as intake_router
from app.patient.regular_chat import router as chat_router
from app.doctor.review import router as doctor_router

# Create FastAPI app
app = FastAPI(title="CognifyCare Test App")

# Include routers
app.include_router(analysis_router)
app.include_router(conversation_router)
app.include_router(doctor_router)
app.include_router(intake_router)
app.include_router(chat_router)

# LLM Configuration endpoint
class LLMConfigRequest(BaseModel):
    api_key: str
    provider: str = "openai"

@app.post("/api/admin/configure-llm")
def configure_llm_endpoint(config: LLMConfigRequest):
    """Configure LLM for diagnosis and treatment planning"""
    try:
        configure_llm(config.api_key, config.provider)
        return {
            "status": "success",
            "message": f"LLM configured with provider: {config.provider}",
            "llm_available": True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure LLM: {str(e)}"
        )

# Intake Analysis endpoint
class IntakeAnalysisRequest(BaseModel):
    patient_id: int
    intake_data: dict

class IntakeAnalysisResponse(BaseModel):
    patient_id: int
    alzheimers_prediction: dict
    patient_portfolio: dict
    diagnosis_analysis: dict
    treatment_plan: dict
    companion_chatbot_config: dict
    analysis_timestamp: str
    analysis_method: str

@app.post("/api/patient/{patient_id}/intake/analyze", response_model=IntakeAnalysisResponse)
def analyze_intake_with_alzheimers_prediction(patient_id: int, req: IntakeAnalysisRequest):
    """Analyze patient intake data with Alzheimer's prediction"""
    from app.analysis.diagnosis_treatment_planning import diagnosis_planner
    
    if not diagnosis_planner.is_predictor_available():
        raise HTTPException(
            status_code=503, 
            detail="Alzheimer's predictor model not available. Please ensure model files are properly loaded."
        )
    
    try:
        # Use the diagnosis planner to analyze intake data
        analysis_result = diagnosis_planner.analyze_intake_data(req.intake_data)
        
        return IntakeAnalysisResponse(
            patient_id=patient_id,
            alzheimers_prediction=analysis_result["alzheimers_prediction"],
            patient_portfolio=analysis_result["patient_portfolio"],
            diagnosis_analysis=analysis_result["diagnosis_analysis"],
            treatment_plan=analysis_result["treatment_plan"],
            companion_chatbot_config=analysis_result["companion_chatbot_config"],
            analysis_timestamp=analysis_result["analysis_timestamp"],
            analysis_method=analysis_result["analysis_method"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in intake analysis: {str(e)}"
        )

# Root endpoint
@app.get("/")
def root():
    return {
        "service": "CognifyCare Test App",
        "status": "running",
        "endpoints": {
            "diagnosis_analysis": "/api/analysis/",
            "conversation_analysis": "/api/conversation/",
            "intake": "/api/patient/{patient_id}/intake/",
            "chatbot": "/api/patient/{patient_id}/chatbot/",
            "chat": "/api/patient/{patient_id}/chat/"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
