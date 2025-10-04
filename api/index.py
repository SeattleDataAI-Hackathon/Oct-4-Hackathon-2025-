"""
CuraLoop Backend API - Vercel Entry Point
Main FastAPI application that combines all module routers
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import only the router from analysis (not the full app)
from app.analysis.diagnosis_treatment_planning import router as analysis_router
from app.analysis.conversation_analyzer import router as conversation_router
from app.doctor.review import router as doctor_router

# For intake, we need to import the router without triggering app creation
# Import the intake module's router directly
import importlib.util
spec = importlib.util.spec_from_file_location("intake", os.path.join(os.path.dirname(__file__), '..', 'app', 'patient', 'intake.py'))
intake_module = importlib.util.module_from_spec(spec)
sys.modules['intake'] = intake_module
spec.loader.exec_module(intake_module)
intake_router = intake_module.router

# Import the regular_chat module's router
spec_chat = importlib.util.spec_from_file_location("regular_chat", os.path.join(os.path.dirname(__file__), '..', 'app', 'patient', 'regular_chat.py'))
chat_module = importlib.util.module_from_spec(spec_chat)
sys.modules['regular_chat'] = chat_module
spec_chat.loader.exec_module(chat_module)
chat_router = chat_module.router

# Create FastAPI application
app = FastAPI(
    title="CuraLoop API",
    description="AI Companion for Alzheimer's Continuous Care",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router)
app.include_router(conversation_router)
app.include_router(doctor_router)
app.include_router(intake_router)
app.include_router(chat_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CuraLoop API",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "diagnosis_analysis": "/api/analysis",
            "conversation_analysis": "/api/conversation",
            "doctor_review": "/api/doctor",
            "patient_intake": "/api/patient/{patient_id}/intake",
            "chatbot_initialization": "/api/patient/{patient_id}/chatbot/initialize",
            "chat_sessions": "/api/patient/{patient_id}/chat",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CuraLoop Backend API"
    }

# Export the app for Vercel
# Vercel will automatically detect and use the 'app' variable
