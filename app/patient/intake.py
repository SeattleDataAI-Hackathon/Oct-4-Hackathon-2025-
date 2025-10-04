"""
CognifyCare — Intake Chat Orchestrator
Start a chat *with no prior user message* and guide the patient through dataset-mapped questions.

Adds three endpoints:
- POST /api/patient/{patient_id}/intake/start           -> create session, return first prompt
- POST /api/patient/{patient_id}/intake/reply           -> accept free-text reply, return next prompt
- GET  /api/patient/{patient_id}/intake/state?session_id= -> inspect session state

This file can be merged into your existing `app.py` or imported as a router.
It reuses the in-memory DB pattern from the earlier skeleton (you can swap to Postgres later).
"""

from __future__ import annotations
from fastapi import FastAPI, APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import re, uuid, threading

app = FastAPI(title="CognifyCare Intake Orchestrator")
router = APIRouter(prefix="/api")

# -------------------------- In-memory stores --------------------------
class MemoryStore:
    def __init__(self):
        self.patients: Dict[int, Dict[str, Any]] = {}
        self.intake_sessions: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def get_or_create_patient(self, patient_id: int) -> Dict[str, Any]:
        with self.lock:
            if patient_id not in self.patients:
                self.patients[patient_id] = {
                    "profile": {
                        "patient_id": patient_id,
                        "created_at": datetime.utcnow().isoformat(),
                        "timezone": "America/Los_Angeles",
                    },
                    "long_term_memory": "",
                    "chat_history": [],
                    "intake_history": [],
                    "routine_history": [],
                    "doctor_plan": None,
                    "last_scores": {"mmse": None, "adl": None, "severity": None},
                }
            return self.patients[patient_id]

DB = MemoryStore()

# -------------------------- Question bank ----------------------------
# Ordered list; each step asks one patient-friendly question and fills a dataset field.
QUESTIONS: List[Dict[str, Any]] = [
    {"id": "age", "field": "Age", "prompt": "To get started, how old are you?", "type": "number", "required": True, "min": 40, "max": 120},
    {"id": "gender", "field": "Gender", "prompt": "What is your gender? (Female, Male, Other/Prefer not to say)", "type": "choice", "map": {"female": 0, "male": 1, "other": 2, "prefer not to say": 2}},
    {"id": "ethnicity", "field": "Ethnicity", "prompt": "Which ethnicity best describes you? (White, Black, Asian, Hispanic/Latino, Other)", "type": "choice", "map": {"white":0, "black":1, "asian":2, "hispanic":3, "latino":3, "other":4}},
    {"id": "education", "field": "EducationLevel", "prompt": "What is the highest level of education you completed? (None/Primary, High school, College/Associate, Bachelor’s, Graduate+)", "type": "choice", "map": {"none":0, "primary":0, "high school":1, "college":2, "associate":2, "bachelor":3, "bachelor’s":3, "graduate":4, "masters":4, "phd":4}},
    {"id": "height", "field": "HeightCm", "prompt": "What is your height? You can say in centimeters or feet and inches.", "type": "text"},
    {"id": "weight", "field": "WeightKg", "prompt": "What is your current weight? You can say kilograms or pounds.", "type": "text"},
    {"id": "bmi", "field": "BMI", "prompt": "If you already know your BMI you can tell me; otherwise I will compute it.", "type": "number", "required": False, "min": 10, "max": 60},

    {"id": "smoking", "field": "Smoking", "prompt": "Do you currently smoke or have you in the last 12 months? (yes/no)", "type": "boolean"},
    {"id": "alcohol", "field": "AlcoholConsumption", "prompt": "On average, how many alcoholic drinks do you have per week? (You can say none)", "type": "number", "min": 0, "max": 100},
    {"id": "activity", "field": "PhysicalActivity", "prompt": "How active are you in a typical week, from 0 (not active) to 10 (very active)?", "type": "number", "min": 0, "max": 10},
    {"id": "diet", "field": "DietQuality", "prompt": "How would you rate your diet quality from 0 (poor) to 3 (excellent)?", "type": "number", "min": 0, "max": 3},
    {"id": "sleep", "field": "SleepQuality", "prompt": "How would you rate your sleep quality in the past week from 0 (very poor) to 10 (excellent)?", "type": "number", "min": 0, "max": 10},

    {"id": "fam_alz", "field": "FamilyHistoryAlzheimers", "prompt": "Has a close family member been diagnosed with Alzheimer’s? (yes/no/unsure)", "type": "tristate"},

    {"id": "c_cv", "field": "CardiovascularDisease", "prompt": "Have you ever been diagnosed with cardiovascular disease? (yes/no/unsure)", "type": "tristate"},
    {"id": "c_dm", "field": "Diabetes", "prompt": "Have you been diagnosed with diabetes? (yes/no/unsure)", "type": "tristate"},
    {"id": "c_dep", "field": "Depression", "prompt": "Have you been diagnosed with depression? (yes/no/unsure)", "type": "tristate"},
    {"id": "c_hi", "field": "HeadInjury", "prompt": "Have you had a significant head injury? (yes/no/unsure)", "type": "tristate"},
    {"id": "c_htn", "field": "Hypertension", "prompt": "Have you been diagnosed with high blood pressure (hypertension)? (yes/no/unsure)", "type": "tristate"},

    {"id": "bps", "field": "SystolicBP", "prompt": "If you know it, what is your most recent systolic blood pressure (the top number)?", "type": "number", "required": False, "min": 80, "max": 220},
    {"id": "bpd", "field": "DiastolicBP", "prompt": "If you know it, what is your most recent diastolic blood pressure (the bottom number)?", "type": "number", "required": False, "min": 40, "max": 140},

    {"id": "chol_t", "field": "CholesterolTotal", "prompt": "If known, what is your recent total cholesterol (mg/dL)?", "type": "number", "required": False, "min": 80, "max": 400},
    {"id": "chol_ldl", "field": "CholesterolLDL", "prompt": "If known, LDL cholesterol (mg/dL)?", "type": "number", "required": False, "min": 30, "max": 300},
    {"id": "chol_hdl", "field": "CholesterolHDL", "prompt": "If known, HDL cholesterol (mg/dL)?", "type": "number", "required": False, "min": 10, "max": 150},
    {"id": "chol_trg", "field": "CholesterolTriglycerides", "prompt": "If known, triglycerides (mg/dL)?", "type": "number", "required": False, "min": 30, "max": 800},

    {"id": "mmse", "field": "MMSE", "prompt": "If you have an MMSE score (0–30), please tell me. If not, you can say 'skip'.", "type": "number", "required": False, "min": 0, "max": 30},
    {"id": "func", "field": "FunctionalAssessment", "prompt": "Rate your ability to manage daily tasks from 0 (unable) to 100 (fully independent).", "type": "number", "required": False, "min": 0, "max": 100},
    {"id": "adl", "field": "ADL", "prompt": "How independent are you in Activities of Daily Living from 0 (need help) to 100 (independent)?", "type": "number", "required": False, "min": 0, "max": 100},

    {"id": "sym_mem", "field": "MemoryComplaints", "prompt": "In the past month, have you had more memory lapses than usual? (yes/no)", "type": "boolean"},
    {"id": "sym_beh", "field": "BehavioralProblems", "prompt": "Have there been behavioral changes (e.g., agitation, apathy)? (yes/no)", "type": "boolean"},
    {"id": "sym_conf", "field": "Confusion", "prompt": "Have you felt confused? (yes/no)", "type": "boolean"},
    {"id": "sym_dis", "field": "Disorientation", "prompt": "Have you felt lost or disoriented in familiar places? (yes/no)", "type": "boolean"},
    {"id": "sym_pers", "field": "PersonalityChanges", "prompt": "Have there been noticeable personality changes? (yes/no)", "type": "boolean"},
    {"id": "sym_tasks", "field": "DifficultyCompletingTasks", "prompt": "Do you have difficulty completing familiar tasks? (yes/no)", "type": "boolean"},
    {"id": "sym_forget", "field": "Forgetfulness", "prompt": "Have you been more forgetful of recent conversations or events? (yes/no)", "type": "boolean"},
]

# -------------------------- Models ----------------------------
class StartResponse(BaseModel):
    session_id: str
    patient_id: int
    prompt: str
    step_index: int
    total_steps: int

class ReplyRequest(BaseModel):
    session_id: str
    message: str

class ReplyResponse(BaseModel):
    session_id: str
    patient_id: int
    saved: Dict[str, Any]
    next_prompt: Optional[str]
    step_index: int
    total_steps: int
    finished: bool
    summary: Optional[Dict[str, Any]] = None

class StateResponse(BaseModel):
    patient_id: int
    created_at: str
    answers: Dict[str, Any]
    step_index: int
    finished: bool
    summary: Optional[Dict[str, Any]] = None

# -------------------------- Helper parsing ----------------------------
YES = {"y","yes","yeah","yep","true","sure"}
NO  = {"n","no","nope","false"}
SKIP= {"skip","unknown","unsure","dont know","don't know","na","n/a","idk"}

_ht_re = re.compile(r"(?:(?P<cm>\d{2,3})\s*cm)|(?:(?P<ft>\d)'?\s*(?P<inch>\d{1,2}) ?\")", re.I)
_wt_re = re.compile(r"(?:(?P<kg>\d{2,3})\s*kg)|(?:(?P<lb>\d{2,3})\s*lb)\b", re.I)
_num_re = re.compile(r"-?\d+(?:\.\d+)?")

def parse_boolean(msg: str) -> Optional[bool]:
    m = msg.strip().lower()
    if m in YES: return True
    if m in NO: return False
    if m in SKIP: return None
    return None

def parse_tristate(msg: str) -> Optional[int]:
    m = msg.strip().lower()
    if m in YES: return 1
    if m in NO: return 0
    if m in SKIP or m in {"unsure"}: return None
    return None

def parse_number(msg: str, minv: Optional[float]=None, maxv: Optional[float]=None) -> Optional[float]:
    m = _num_re.search(msg)
    if not m: return None
    val = float(m.group())
    if minv is not None and val < minv: return None
    if maxv is not None and val > maxv: return None
    return val

def parse_height_cm(msg: str) -> Optional[float]:
    m = _ht_re.search(msg)
    if not m: return parse_number(msg, 120, 230)
    if m.group("cm"): return float(m.group("cm"))
    if m.group("ft") and m.group("inch"):
        ft = int(m.group("ft")); inch = int(m.group("inch"))
        return ft*30.48 + inch*2.54
    return None

def parse_weight_kg(msg: str) -> Optional[float]:
    m = _wt_re.search(msg)
    if not m:
        # try plain number + infer
        val = parse_number(msg, 35, 200)
        return val
    if m.group("kg"): return float(m.group("kg"))
    if m.group("lb"): return float(m.group("lb")) * 0.45359237
    return None

# -------------------------- Severity (stub) ----------------------------
# Simple heuristic for demo; wire your ML/heuristic here

def severity_infer(fields: Dict[str, Any]) -> Dict[str, Any]:
    mmse = float(fields.get("MMSE", 0) or 0)
    adl = float(fields.get("ADL", 100) or 100)
    if mmse >= 24:
        label, sev = "mild", 0.2
    elif mmse >= 10:
        label, sev = "moderate", 0.6
    else:
        label, sev = "severe", 0.9
    if adl < 50: sev += 0.1
    return {"severity_label": label, "severity_score": min(1.0, sev)}

# -------------------------- Orchestrator ----------------------------

def _first_prompt() -> str:
    return "Hello! I’ll guide you through a short health intake. We’ll go one step at a time. If you’re not sure, you can say ‘skip’. " \
           "To get started, how old are you?"

@router.post("/patient/{patient_id}/intake/start", response_model=StartResponse)
def intake_start(patient_id: int):
    DB.get_or_create_patient(patient_id)
    session_id = uuid.uuid4().hex
    DB.intake_sessions[session_id] = {
        "patient_id": patient_id,
        "created_at": datetime.utcnow().isoformat(),
        "answers": {},
        "step_index": 0,
        "finished": False
    }
    prompt = _first_prompt()
    return StartResponse(session_id=session_id, patient_id=patient_id, prompt=prompt, step_index=0, total_steps=len(QUESTIONS))

@router.get("/patient/{patient_id}/intake/state", response_model=StateResponse)
def intake_state(patient_id: int, session_id: str = Query(...)):
    s = DB.intake_sessions.get(session_id)
    if not s or s["patient_id"] != patient_id:
        raise HTTPException(404, "session not found")
    return StateResponse(
        patient_id=s["patient_id"],
        created_at=s["created_at"],
        answers=s["answers"],
        step_index=s["step_index"],
        finished=s["finished"],
        summary=s.get("summary")
    )

@router.post("/patient/{patient_id}/intake/reply", response_model=ReplyResponse)
def intake_reply(patient_id: int, req: ReplyRequest):
    s = DB.intake_sessions.get(req.session_id)
    if not s or s["patient_id"] != patient_id:
        raise HTTPException(404, "session not found for patient")
    if s.get("finished"):
        return ReplyResponse(session_id=req.session_id, patient_id=patient_id, saved={}, next_prompt=None, step_index=s["step_index"], total_steps=len(QUESTIONS), finished=True, summary=s.get("summary"))

    idx = s["step_index"]
    if idx >= len(QUESTIONS):
        s["finished"] = True
        return ReplyResponse(session_id=req.session_id, patient_id=patient_id, saved={}, next_prompt=None, step_index=idx, total_steps=len(QUESTIONS), finished=True, summary=s.get("summary"))

    q = QUESTIONS[idx]
    field = q["field"]
    msg = req.message.strip()

    # parse according to type
    value: Any = None
    if q["type"] == "boolean":
        value = parse_boolean(msg)
    elif q["type"] == "tristate":
        value = parse_tristate(msg)
    elif q["type"] == "number":
        value = parse_number(msg, q.get("min"), q.get("max"))
    elif q["type"] == "choice":
        m = msg.lower()
        if m in q.get("map", {}):
            value = q["map"][m]
        else:
            # try contains match
            for k,v in q.get("map", {}).items():
                if k in m:
                    value = v; break
    elif q["type"] == "text":
        if field == "HeightCm":
            value = parse_height_cm(msg)
        elif field == "WeightKg":
            value = parse_weight_kg(msg)
        else:
            value = msg if msg.lower() not in SKIP else None

    # validation & required handling
    if value is None and q.get("required", False):
        # re-ask with a gentle nudge
        return ReplyResponse(
            session_id=req.session_id,
            patient_id=patient_id,
            saved={},
            next_prompt=f"I might have missed that. {q['prompt']}",
            step_index=idx,
            total_steps=len(QUESTIONS),
            finished=False
        )

    # save answer (can be None for optional)
    s["answers"][field] = value

    # compute BMI if possible after weight
    if field in ("WeightKg","BMI"):
        ht = s["answers"].get("HeightCm")
        wt = s["answers"].get("WeightKg")
        bmi = s["answers"].get("BMI")
        if bmi is None and ht and wt:
            s["answers"]["BMI"] = round(wt / ((ht/100.0)**2), 2)

    # advance step
    s["step_index"] = idx + 1
    finished = s["step_index"] >= len(QUESTIONS)

    if not finished:
        next_q = QUESTIONS[s["step_index"]]
        next_prompt = next_q["prompt"]
        saved = {field: value}
        return ReplyResponse(session_id=req.session_id, patient_id=patient_id, saved=saved, next_prompt=next_prompt, step_index=s["step_index"], total_steps=len(QUESTIONS), finished=False)

    # finalize: persist to patient, run severity, craft summary
    patient = DB.get_or_create_patient(patient_id)
    # log transcript-lite into intake_history and long-term memory
    now = datetime.utcnow().isoformat()
    patient["intake_history"].append({"role":"assistant","text":"Intake completed.","ts":now})
    # persist fields to a simple snapshot; in real DB, normalize
    patient.setdefault("intake_snapshots", []).append({"ts": now, "fields": s["answers"]})

    # Update last known scores if present
    if s["answers"].get("MMSE") is not None:
        patient["last_scores"]["mmse"] = s["answers"]["MMSE"]
    if s["answers"].get("ADL") is not None:
        patient["last_scores"]["adl"] = s["answers"]["ADL"]

    sev = severity_infer(s["answers"])
    patient["last_scores"]["severity"] = sev["severity_score"]

    # auto-alert if moderate/severe
    if sev["severity_label"] in ("moderate","severe"):
        alert = {
            "id": len(DB.alerts),
            "patient_id": patient_id,
            "kind": "intake_change",
            "level": "medium" if sev["severity_label"]=="moderate" else "high",
            "summary": f"Intake suggests {sev['severity_label']} severity",
            "details": {"severity": sev, "answers": s["answers"]},
            "created_at": now,
            "hitl_status": "pending"
        }
        DB.alerts.append(alert)

    s["finished"] = True
    s["summary"] = {"answers": s["answers"], "severity": sev}

    return ReplyResponse(
        session_id=req.session_id,
        patient_id=patient_id,
        saved={field: value},
        next_prompt=None,
        step_index=s["step_index"],
        total_steps=len(QUESTIONS),
        finished=True,
        summary=s["summary"]
    )

app.include_router(router)

# Root for quick check
@app.get("/")
def root():
    return {"service": "CognifyCare Intake Orchestrator", "questions": len(QUESTIONS)}
