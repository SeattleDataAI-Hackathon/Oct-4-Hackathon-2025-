# api_server.py - RPO-DRA FastAPI Server
# Rescue Priority Optimizer with Dynamic Resource Allocation

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional, Dict
import sqlite3
import requests
import json

# === Initialize FastAPI ===
app = FastAPI(
    title="RPO-DRA API",
    description="Rescue Priority Optimizer with Dynamic Resource Allocation",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load ML Models ===
print("🤖 Loading RPO-DRA AI Models...")
try:
    model1_pkg = joblib.load('damage_model.pkl')
    model2_pkg = joblib.load('resource_model.pkl')
    
    model1 = model1_pkg['model']
    model2 = model2_pkg['model']
    encoders = model1_pkg['encoders']
    feature_names1 = model1_pkg['feature_names']
    damage_categories = model1_pkg['damage_categories']
    
    print("✅ Models loaded successfully!")
    print(f"   - Model 1: Damage & Need Forecasting")
    print(f"   - Model 2: Resource Allocation")
except Exception as e:
    print(f"⚠️  Warning: Could not load models - {e}")
    model1 = model2 = None

# === Database Setup ===
def get_db():
    conn = sqlite3.connect('dispatch_predictions.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS dispatches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_name TEXT,
            timestamp TEXT,
            
            -- Model 1 Outputs
            damage_severity REAL,
            medical_sar_need REAL,
            animal_rescue_need REAL,
            equipment_need REAL,
            sar_priority REAL,
            
            -- Model 2 Outputs (AI Recommendation)
            ai_fire_engines INTEGER,
            ai_ambulances INTEGER,
            ai_animal_rescue INTEGER,
            ai_heavy_equipment INTEGER,
            ai_sar_teams INTEGER,
            
            -- Human Adjustments
            final_fire_engines INTEGER,
            final_ambulances INTEGER,
            final_animal_rescue INTEGER,
            final_heavy_equipment INTEGER,
            final_sar_teams INTEGER,
            
            -- Metadata
            status TEXT,
            dispatcher_name TEXT,
            adjustment_reason TEXT,
            approved_at TEXT,
            
            -- Structure Data
            structure_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()
print("✅ Database initialized")

# === Request/Response Models ===
class StructureInput(BaseModel):
    area_name: str
    structure_type: str
    structure_category: str = "Single Residence"
    roof_construction: str
    exterior_siding: str
    window_pane: str
    year_built: int
    assessed_value: float
    num_units: int = 1
    num_outbuildings: int = 0
    latitude: Optional[float] = 38.48
    longitude: Optional[float] = -122.03

class DamageAssessment(BaseModel):
    damage_severity: float
    medical_sar_need: float
    animal_rescue_need: float
    equipment_need: float
    sar_priority: float
    extreme_damage_probability: float

class ResourceManifest(BaseModel):
    fire_engines: int
    ambulances: int
    animal_rescue_teams: int
    heavy_equipment: int
    sar_teams: int

class AnalysisResponse(BaseModel):
    area_name: str
    damage_assessment: DamageAssessment
    ai_recommended_manifest: ResourceManifest
    needs_human_review: bool
    timestamp: str
    dispatch_id: int

class DispatchApproval(BaseModel):
    dispatch_id: int
    dispatcher_name: str
    final_manifest: ResourceManifest
    adjustment_reason: str = ""

# === Helper Functions ===
def encode_structure_features(data: StructureInput):
    """Encode structure features for model prediction"""
    
    # Calculate derived features
    structure_age = 2024 - data.year_built
    
    # Encode categorical features
    structure_type_enc = encoders['* Structure Type'].transform([data.structure_type])[0]
    category_enc = encoders['Structure Category'].transform([data.structure_category])[0]
    roof_enc = encoders['* Roof Construction'].transform([data.roof_construction])[0]
    siding_enc = encoders['* Exterior Siding'].transform([data.exterior_siding])[0]
    window_enc = encoders['* Window Pane'].transform([data.window_pane])[0]
    
    # Create feature array matching training
    features = pd.DataFrame([[
        structure_type_enc,
        category_enc,
        roof_enc,
        siding_enc,
        window_enc,
        structure_age,
        data.assessed_value,
        data.num_units,
        data.num_outbuildings
    ]], columns=feature_names1)
    
    return features

# === API Endpoints ===

@app.get("/")
def root():
    return {
        "service": "RPO-DRA - Rescue Priority Optimizer",
        "status": "online",
        "models_loaded": model1 is not None and model2 is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_area(data: StructureInput):
    """
    Analyze area and provide optimal resource allocation
    This is the main endpoint N8n calls
    """
    if not model1 or not model2:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Encode features
        features = encode_structure_features(data)
        
        # Model 1: Predict damage and needs
        needs_pred = model1.predict(features)[0]
        damage_sev, medical_need, animal_need, equipment_need, sar_pri = needs_pred
        
        # Calculate extreme damage probability
        extreme_damage_prob = min(damage_sev / 3.0, 1.0)
        
        # Model 2: Predict optimal resources
        needs_for_model2 = pd.DataFrame([[
            damage_sev, medical_need, animal_need, equipment_need, sar_pri
        ]], columns=['pred_damage', 'pred_medical', 'pred_animal', 
                     'pred_equipment', 'pred_sar'])
        
        resources = model2.predict(needs_for_model2)[0]
        fire_eng, ambulances, animal_rescue, heavy_eq, sar_teams = [int(r) for r in resources]
        
        # Determine if human review needed
        needs_review = (
            extreme_damage_prob > 0.6 or
            medical_need > 7 or
            animal_need > 7 or
            fire_eng >= 3
        )
        
        # Save to database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO dispatches 
            (area_name, timestamp, damage_severity, medical_sar_need, animal_rescue_need,
             equipment_need, sar_priority, ai_fire_engines, ai_ambulances, ai_animal_rescue,
             ai_heavy_equipment, ai_sar_teams, status, structure_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.area_name,
            datetime.now().isoformat(),
            float(damage_sev),
            float(medical_need),
            float(animal_need),
            float(equipment_need),
            float(sar_pri),
            fire_eng, ambulances, animal_rescue, heavy_eq, sar_teams,
            'pending_review' if needs_review else 'auto_deployed',
            json.dumps(data.dict())
        ))
        conn.commit()
        dispatch_id = cursor.lastrowid
        conn.close()
        
        return AnalysisResponse(
            area_name=data.area_name,
            damage_assessment=DamageAssessment(
                damage_severity=round(damage_sev, 2),
                medical_sar_need=round(medical_need, 1),
                animal_rescue_need=round(animal_need, 1),
                equipment_need=round(equipment_need, 1),
                sar_priority=round(sar_pri, 1),
                extreme_damage_probability=round(extreme_damage_prob, 3)
            ),
            ai_recommended_manifest=ResourceManifest(
                fire_engines=fire_eng,
                ambulances=ambulances,
                animal_rescue_teams=animal_rescue,
                heavy_equipment=heavy_eq,
                sar_teams=sar_teams
            ),
            needs_human_review=needs_review,
            timestamp=datetime.now().isoformat(),
            dispatch_id=dispatch_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/dispatches")
def get_dispatches(status: Optional[str] = None):
    """Get all dispatch records"""
    conn = get_db()
    
    if status:
        query = "SELECT * FROM dispatches WHERE status=? ORDER BY timestamp DESC"
        rows = conn.execute(query, (status,)).fetchall()
    else:
        query = "SELECT * FROM dispatches ORDER BY timestamp DESC LIMIT 100"
        rows = conn.execute(query).fetchall()
    
    dispatches = [dict(row) for row in rows]
    conn.close()
    
    return {"dispatches": dispatches, "count": len(dispatches)}

@app.get("/stats")
def get_stats():
    """Dashboard statistics"""
    conn = get_db()
    
    pending = conn.execute(
        "SELECT COUNT(*) as c FROM dispatches WHERE status='pending_review'"
    ).fetchone()['c']
    
    deployed_today = conn.execute(
        "SELECT COUNT(*) as c FROM dispatches WHERE status='deployed' AND DATE(approved_at)=DATE('now')"
    ).fetchone()['c']
    
    high_priority = conn.execute(
        "SELECT COUNT(*) as c FROM dispatches WHERE sar_priority > 7 AND status='pending_review'"
    ).fetchone()['c']
    
    conn.close()
    
    return {
        "pending_reviews": pending,
        "deployed_today": deployed_today,
        "high_priority_count": high_priority
    }

@app.post("/approve")
def approve_dispatch(request: DispatchApproval):
    """Approve and adjust resource manifest"""
    conn = get_db()
    
    conn.execute('''
        UPDATE dispatches 
        SET status='deployed', 
            dispatcher_name=?, 
            approved_at=?,
            final_fire_engines=?,
            final_ambulances=?,
            final_animal_rescue=?,
            final_heavy_equipment=?,
            final_sar_teams=?,
            adjustment_reason=?
        WHERE id=?
    ''', (
        request.dispatcher_name,
        datetime.now().isoformat(),
        request.final_manifest.fire_engines,
        request.final_manifest.ambulances,
        request.final_manifest.animal_rescue_teams,
        request.final_manifest.heavy_equipment,
        request.final_manifest.sar_teams,
        request.adjustment_reason,
        request.dispatch_id
    ))
    
    conn.commit()
    updated = conn.execute("SELECT * FROM dispatches WHERE id=?", (request.dispatch_id,)).fetchone()
    conn.close()
    
    # Notify N8n
    try:
        requests.post('http://localhost:5678/webhook/dispatch-approval', json={
            'status': 'deployed',
            'dispatcher': request.dispatcher_name,
            'dispatch_id': request.dispatch_id,
            'final_manifest': request.final_manifest.dict()
        }, timeout=2)
    except:
        pass
    
    return {
        "success": True,
        "message": "Dispatch approved and deployed",
        "dispatch": dict(updated) if updated else None
    }

@app.get("/test-dispatch")
def test_dispatch():
    """Quick test endpoint for demo"""
    sample = StructureInput(
        area_name="Quail Canyon",
        structure_type="Single Family Residence Multi Story",
        structure_category="Single Residence",
        roof_construction="Asphalt",
        exterior_siding="Wood",
        window_pane="Single Pane",
        year_built=1997,
        assessed_value=510000,
        num_units=1,
        num_outbuildings=0,
        latitude=38.4749,
        longitude=-122.0444
    )
    return analyze_area(sample)

# === Run Server ===
if __name__ == "__main__":
    import uvicorn
    print("\n🚨 Starting RPO-DRA API Server...")
    print("📡 API Docs: http://localhost:8000/docs")
    print("🧪 Test: http://localhost:8000/test-dispatch\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
