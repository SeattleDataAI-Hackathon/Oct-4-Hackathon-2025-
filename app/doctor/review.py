"""
Doctor Review Module
Allows doctors to review analysis outputs (intake or conversation) and make decisions
on treatment plan updates. Changes are applied to the chatbot configuration.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

# Import the chatbot store to update configs
from app.patient.regular_chat import CHAT_DB

router = APIRouter(prefix="/api/doctor", tags=["doctor"])


# ==================== Request/Response Models ====================

class DoctorDecision(BaseModel):
    """Doctor's decision on treatment changes"""
    approved: bool
    notes: str
    treatment_changes: Optional[Dict[str, Any]] = None
    urgency_level: Optional[str] = None  # "routine", "soon", "urgent", "immediate"


class IntakeAnalysisReview(BaseModel):
    """Review intake analysis and make treatment decisions"""
    patient_id: int
    intake_analysis: Dict[str, Any]  # Full output from intake analysis endpoint
    doctor_decision: DoctorDecision


class ConversationAnalysisReview(BaseModel):
    """Review conversation analysis and make treatment decisions"""
    patient_id: int
    conversation_analysis: Dict[str, Any]  # Full output from conversation analyzer
    doctor_decision: DoctorDecision


class ReviewResponse(BaseModel):
    """Response after doctor review"""
    patient_id: int
    review_timestamp: str
    decision_applied: bool
    updated_treatment_plan: Optional[Dict[str, Any]] = None
    updated_chatbot_config: Optional[Dict[str, Any]] = None
    message: str


class TreatmentPlanUpdate(BaseModel):
    """Direct treatment plan update"""
    patient_id: int
    updates: Dict[str, Any]  # Changes to apply to treatment plan
    reason: str


# ==================== Helper Functions ====================

def merge_treatment_plans(original: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge treatment plan updates into original plan

    Args:
        original: Original treatment plan
        updates: Updates to apply (can add/modify/remove items)

    Returns:
        Merged treatment plan
    """
    merged = original.copy()

    for key, value in updates.items():
        if key in merged:
            if isinstance(merged[key], list) and isinstance(value, list):
                # For lists, extend with new items
                merged[key].extend(value)
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                # For dicts, merge recursively
                merged[key].update(value)
            else:
                # Replace value
                merged[key] = value
        else:
            # Add new key
            merged[key] = value

    return merged


def update_chatbot_config(patient_id: int, new_treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update chatbot configuration with new treatment plan

    Args:
        patient_id: Patient ID
        new_treatment_plan: Updated treatment plan

    Returns:
        Updated chatbot config
    """
    # Get patient's chatbot
    patient_bot = CHAT_DB.patient_chatbots.get(patient_id)

    if not patient_bot:
        raise ValueError(f"No chatbot found for patient {patient_id}")

    chatbot = patient_bot["chatbot"]

    # Update treatment plan
    chatbot.treatment_plan = new_treatment_plan

    # Regenerate treatment execution from updated plan
    chatbot.treatment_execution = _regenerate_treatment_execution(new_treatment_plan)

    # Update the stored config
    updated_config = {
        "personality": chatbot.chatbot_config.get("personality"),
        "communication_style": chatbot.chatbot_config.get("communication_style"),
        "treatment_execution": chatbot.treatment_execution,
        "daily_activities": chatbot.chatbot_config.get("daily_activities", []),
        "safety_features": chatbot.chatbot_config.get("safety_features", []),
        "personalization": chatbot.chatbot_config.get("personalization", {}),
        "conversation_flows": chatbot.conversation_flows,
        "monitoring_schedule": new_treatment_plan.get("monitoring_schedule", {}),
        "treatment_goals": _extract_treatment_goals(new_treatment_plan)
    }

    # Update chatbot config
    chatbot.chatbot_config = updated_config

    return updated_config


def _regenerate_treatment_execution(treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Regenerate treatment execution structure from treatment plan"""
    from app.analysis.diagnosis_treatment_planning import DiagnosisTreatmentPlanner

    planner = DiagnosisTreatmentPlanner()

    # Convert treatment plan items to chat activities
    execution = {}

    for category, items in treatment_plan.items():
        if isinstance(items, list) and category not in ["monitoring_schedule"]:
            execution[category] = [
                planner._convert_to_chat_activities([item])[0] if isinstance(item, str) else item
                for item in items
            ]

    return execution


def _extract_treatment_goals(treatment_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract treatment goals from plan"""
    goals = []

    for section, items in treatment_plan.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str):
                    goal = {
                        "id": f"goal_{len(goals) + 1}",
                        "description": item,
                        "category": section,
                        "status": "active",
                        "priority": "high" if "immediate" in section else "medium",
                        "target_date": "ongoing"
                    }
                    goals.append(goal)

    return goals


# ==================== Endpoints ====================

@router.post("/review/intake", response_model=ReviewResponse)
def review_intake_analysis(review: IntakeAnalysisReview):
    """
    Doctor reviews intake analysis and makes treatment decisions

    This endpoint:
    1. Receives full intake analysis output
    2. Receives doctor's decision and treatment changes
    3. Updates the patient's treatment plan if approved
    4. Updates the chatbot configuration with new treatment plan
    """

    try:
        patient_id = review.patient_id
        decision = review.doctor_decision
        intake_analysis = review.intake_analysis

        # Get original treatment plan from analysis
        original_treatment_plan = intake_analysis.get("treatment_plan", {})
        original_chatbot_config = intake_analysis.get("companion_chatbot_config", {})

        if not decision.approved:
            # Decision not approved, return without changes
            return ReviewResponse(
                patient_id=patient_id,
                review_timestamp=datetime.utcnow().isoformat(),
                decision_applied=False,
                updated_treatment_plan=None,
                updated_chatbot_config=None,
                message=f"Intake review completed. No changes applied. Doctor notes: {decision.notes}"
            )

        # Approved - apply treatment changes
        updated_treatment_plan = original_treatment_plan

        if decision.treatment_changes:
            # Merge treatment changes
            updated_treatment_plan = merge_treatment_plans(
                original_treatment_plan,
                decision.treatment_changes
            )

        # Update chatbot configuration
        try:
            updated_chatbot_config = update_chatbot_config(patient_id, updated_treatment_plan)

            return ReviewResponse(
                patient_id=patient_id,
                review_timestamp=datetime.utcnow().isoformat(),
                decision_applied=True,
                updated_treatment_plan=updated_treatment_plan,
                updated_chatbot_config=updated_chatbot_config,
                message=f"Intake review approved. Treatment plan and chatbot updated. Doctor notes: {decision.notes}"
            )

        except ValueError as e:
            # Chatbot not initialized yet - return treatment plan only
            return ReviewResponse(
                patient_id=patient_id,
                review_timestamp=datetime.utcnow().isoformat(),
                decision_applied=True,
                updated_treatment_plan=updated_treatment_plan,
                updated_chatbot_config=None,
                message=f"Treatment plan updated. Chatbot not yet initialized. Doctor notes: {decision.notes}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing intake review: {str(e)}"
        )


@router.post("/review/conversation", response_model=ReviewResponse)
def review_conversation_analysis(review: ConversationAnalysisReview):
    """
    Doctor reviews conversation analysis and makes treatment decisions

    This endpoint:
    1. Receives full conversation analysis output (symptom/mood changes)
    2. Receives doctor's decision and treatment adjustments
    3. Updates the patient's treatment plan if changes needed
    4. Updates the chatbot configuration with adjusted treatment
    """

    try:
        patient_id = review.patient_id
        decision = review.doctor_decision
        conversation_analysis = review.conversation_analysis

        # Get patient's current chatbot and treatment plan
        patient_bot = CHAT_DB.patient_chatbots.get(patient_id)

        if not patient_bot:
            raise HTTPException(
                status_code=404,
                detail=f"No chatbot found for patient {patient_id}. Cannot update treatment plan."
            )

        chatbot = patient_bot["chatbot"]
        current_treatment_plan = chatbot.treatment_plan

        if not decision.approved:
            # Decision not approved, return without changes
            return ReviewResponse(
                patient_id=patient_id,
                review_timestamp=datetime.utcnow().isoformat(),
                decision_applied=False,
                updated_treatment_plan=None,
                updated_chatbot_config=None,
                message=f"Conversation review completed. No changes applied. Doctor notes: {decision.notes}"
            )

        # Approved - apply treatment changes
        updated_treatment_plan = current_treatment_plan

        if decision.treatment_changes:
            # Merge treatment changes
            updated_treatment_plan = merge_treatment_plans(
                current_treatment_plan,
                decision.treatment_changes
            )

        # Update chatbot configuration
        updated_chatbot_config = update_chatbot_config(patient_id, updated_treatment_plan)

        # Extract conversation insights for reference
        contact_decision = conversation_analysis.get("contact_doctor_decision", {})
        llm_analysis = conversation_analysis.get("llm_analysis", {})

        return ReviewResponse(
            patient_id=patient_id,
            review_timestamp=datetime.utcnow().isoformat(),
            decision_applied=True,
            updated_treatment_plan=updated_treatment_plan,
            updated_chatbot_config=updated_chatbot_config,
            message=f"Conversation review approved. Treatment plan and chatbot updated based on symptom changes. "
                   f"Concern level: {llm_analysis.get('concern_level', 'N/A')}. "
                   f"Doctor notes: {decision.notes}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing conversation review: {str(e)}"
        )


@router.post("/treatment/update", response_model=ReviewResponse)
def update_treatment_plan_direct(update: TreatmentPlanUpdate):
    """
    Direct treatment plan update by doctor (without prior analysis review)

    This endpoint allows doctors to make direct updates to treatment plans,
    for example during regular check-ups or when adjusting ongoing care.
    """

    try:
        patient_id = update.patient_id

        # Get patient's current chatbot and treatment plan
        patient_bot = CHAT_DB.patient_chatbots.get(patient_id)

        if not patient_bot:
            raise HTTPException(
                status_code=404,
                detail=f"No chatbot found for patient {patient_id}. Initialize chatbot first."
            )

        chatbot = patient_bot["chatbot"]
        current_treatment_plan = chatbot.treatment_plan

        # Merge updates into current plan
        updated_treatment_plan = merge_treatment_plans(current_treatment_plan, update.updates)

        # Update chatbot configuration
        updated_chatbot_config = update_chatbot_config(patient_id, updated_treatment_plan)

        return ReviewResponse(
            patient_id=patient_id,
            review_timestamp=datetime.utcnow().isoformat(),
            decision_applied=True,
            updated_treatment_plan=updated_treatment_plan,
            updated_chatbot_config=updated_chatbot_config,
            message=f"Treatment plan updated directly. Reason: {update.reason}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating treatment plan: {str(e)}"
        )


@router.get("/patient/{patient_id}/current-plan")
def get_current_treatment_plan(patient_id: int):
    """
    Get the current treatment plan and chatbot config for a patient
    """

    try:
        patient_bot = CHAT_DB.patient_chatbots.get(patient_id)

        if not patient_bot:
            raise HTTPException(
                status_code=404,
                detail=f"No chatbot found for patient {patient_id}"
            )

        chatbot = patient_bot["chatbot"]

        return {
            "patient_id": patient_id,
            "chatbot_id": chatbot.chatbot_id,
            "current_treatment_plan": chatbot.treatment_plan,
            "current_chatbot_config": chatbot.chatbot_config,
            "treatment_goals": chatbot.treatment_goals,
            "monitoring_schedule": chatbot.monitoring_schedule,
            "last_updated": patient_bot.get("created_at")
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving treatment plan: {str(e)}"
        )


@router.get("/health")
def doctor_review_health():
    """Health check for doctor review module"""
    return {
        "status": "healthy",
        "service": "Doctor Review Module",
        "endpoints": {
            "intake_review": "/api/doctor/review/intake",
            "conversation_review": "/api/doctor/review/conversation",
            "direct_update": "/api/doctor/treatment/update",
            "get_current_plan": "/api/doctor/patient/{patient_id}/current-plan"
        }
    }
