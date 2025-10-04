"""
Regular Chat Module - LLM Based Daily Check-in Chatbot
Executes treatment plan through conversational interactions with patients
"""

from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import threading
import json

router = APIRouter(prefix="/api/patient")

# -------------------------- In-memory stores --------------------------
class ChatStore:
    def __init__(self):
        self.chat_sessions: Dict[str, Dict[str, Any]] = {}
        self.patient_chatbots: Dict[int, Dict[str, Any]] = {}
        self.lock = threading.Lock()

CHAT_DB = ChatStore()

# -------------------------- Models ----------------------------
class InitializeChatbotRequest(BaseModel):
    patient_id: int
    patient_portfolio: Dict[str, Any]
    treatment_plan: Dict[str, Any]
    chatbot_config: Dict[str, Any]

class InitializeChatbotResponse(BaseModel):
    patient_id: int
    chatbot_id: str
    status: str
    message: str

class StartChatRequest(BaseModel):
    patient_id: int
    chat_type: Optional[str] = "daily_check_in"  # daily_check_in, treatment_progress, cognitive_engagement, crisis_support

class StartChatResponse(BaseModel):
    session_id: str
    patient_id: int
    chatbot_message: str
    chat_type: str
    conversation_context: Dict[str, Any]

class ChatMessageRequest(BaseModel):
    session_id: str
    patient_message: str

class ChatMessageResponse(BaseModel):
    session_id: str
    chatbot_message: str
    follow_up_questions: Optional[List[str]] = None
    activity_completed: Optional[bool] = None
    conversation_complete: bool = False
    next_steps: Optional[List[str]] = None

class EndChatRequest(BaseModel):
    session_id: str

class EndChatResponse(BaseModel):
    session_id: str
    patient_id: int
    chat_summary: Dict[str, Any]
    interactions: List[Dict[str, Any]]
    completed_activities: List[str]
    metrics: Dict[str, Any]

class GetChatHistoryResponse(BaseModel):
    patient_id: int
    total_sessions: int
    sessions: List[Dict[str, Any]]

# -------------------------- Chatbot Logic --------------------------
class TreatmentChatbot:
    """
    Chatbot that executes treatment plan through daily check-in conversations
    """

    def __init__(self, patient_id: int, patient_portfolio: Dict[str, Any],
                 treatment_plan: Dict[str, Any], chatbot_config: Dict[str, Any]):
        self.patient_id = patient_id
        self.patient_portfolio = patient_portfolio
        self.treatment_plan = treatment_plan
        self.chatbot_config = chatbot_config
        self.chatbot_id = uuid.uuid4().hex
        self.created_at = datetime.utcnow().isoformat()

        # Extract conversation flows and treatment execution from config
        self.conversation_flows = chatbot_config.get("conversation_flows", {})
        self.treatment_execution = chatbot_config.get("treatment_execution", {})
        self.monitoring_schedule = chatbot_config.get("monitoring_schedule", {})
        self.treatment_goals = chatbot_config.get("treatment_goals", [])

        # Track patient progress
        self.completed_activities = []
        self.activity_metrics = {}

    def start_conversation(self, chat_type: str = "daily_check_in") -> Dict[str, Any]:
        """Start a new conversation based on chat type"""

        flow = self.conversation_flows.get(chat_type, {})

        if not flow:
            # Default flow if not found
            return {
                "initial_message": "Hello! How are you feeling today?",
                "topics": ["General wellness"],
                "expected_duration": "5 minutes"
            }

        # Get appropriate prompts from the flow
        prompts = flow.get("prompts", [])
        initial_message = prompts[0] if prompts else "Hello! How are you today?"

        return {
            "initial_message": initial_message,
            "topics": flow.get("topics", []),
            "expected_duration": flow.get("duration", "10 minutes"),
            "frequency": flow.get("frequency", "daily"),
            "purpose": flow.get("purpose", "Wellness check")
        }

    def process_patient_message(self, session: Dict[str, Any], patient_message: str) -> Dict[str, Any]:
        """Process patient message and generate appropriate response"""

        # Get current activity being discussed
        current_activity_index = session.get("current_activity_index", 0)
        chat_type = session.get("chat_type", "daily_check_in")

        # Get activities for the current chat type
        activities = self._get_activities_for_chat_type(chat_type)

        # Check if we've completed all activities
        if current_activity_index >= len(activities):
            return {
                "message": "Great job! We've covered everything for today. Is there anything else you'd like to discuss?",
                "activity_completed": True,
                "conversation_complete": True,
                "follow_up_questions": [],
                "next_steps": ["End conversation", "Review progress"]
            }

        # Get current activity
        current_activity = activities[current_activity_index]

        # Analyze patient response
        response_analysis = self._analyze_patient_response(patient_message, current_activity)

        # Generate chatbot response based on analysis
        chatbot_response = self._generate_chatbot_response(
            current_activity,
            response_analysis,
            patient_message
        )

        # Track activity progress
        if response_analysis.get("activity_completed", False):
            session["current_activity_index"] += 1
            session["completed_activities"].append({
                "activity_id": current_activity.get("id"),
                "activity_title": current_activity.get("title"),
                "completion_time": datetime.utcnow().isoformat(),
                "patient_response": patient_message,
                "metrics": response_analysis.get("metrics", {})
            })

        # Update session
        session["conversation_turns"] += 1
        session["last_activity_time"] = datetime.utcnow().isoformat()

        return {
            "message": chatbot_response["message"],
            "activity_completed": response_analysis.get("activity_completed", False),
            "conversation_complete": session["current_activity_index"] >= len(activities),
            "follow_up_questions": chatbot_response.get("follow_up_questions", []),
            "next_steps": chatbot_response.get("next_steps", [])
        }

    def _get_activities_for_chat_type(self, chat_type: str) -> List[Dict[str, Any]]:
        """Get activities relevant to the chat type"""

        if chat_type == "daily_check_in":
            # Return daily check-in activities from treatment execution
            activities = []

            # Add activities from all categories for daily check-in
            # Prioritize medical management and lifestyle interventions
            for category_name in ["medical_management", "immediate_actions", "lifestyle_interventions"]:
                if category_name in self.treatment_execution:
                    category_items = self.treatment_execution[category_name]
                    if isinstance(category_items, list):
                        for activity in category_items:
                            if isinstance(activity, dict):
                                # For daily check-in, include activities with daily or weekly frequency
                                freq = activity.get("frequency", "daily")
                                if freq in ["daily", "weekly", "as_needed"]:
                                    activities.append(activity)

            # If no activities found, add from any available category
            if not activities:
                for category_items in self.treatment_execution.values():
                    if isinstance(category_items, list):
                        for activity in category_items:
                            if isinstance(activity, dict):
                                activities.append(activity)

            return activities[:5]  # Limit to 5 activities per daily check-in

        elif chat_type == "treatment_progress":
            # Return all treatment activities for weekly review
            activities = []
            for category in self.treatment_execution.values():
                if isinstance(category, list):
                    activities.extend([a for a in category if isinstance(a, dict)])
            return activities

        elif chat_type == "cognitive_engagement":
            # Return cognitive activities
            activities = []
            if "personalized_recommendations" in self.treatment_execution:
                for activity in self.treatment_execution["personalized_recommendations"]:
                    if isinstance(activity, dict) and activity.get("type") == "cognitive":
                        activities.append(activity)
            return activities

        elif chat_type == "crisis_support":
            # Return safety and emergency activities
            activities = []
            if "support_services" in self.treatment_execution:
                for activity in self.treatment_execution["support_services"]:
                    if isinstance(activity, dict) and activity.get("type") == "safety":
                        activities.append(activity)
            return activities

        return []

    def _analyze_patient_response(self, patient_message: str, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patient response to determine activity completion and sentiment"""

        message_lower = patient_message.lower().strip()

        # Simple sentiment analysis
        positive_words = ["yes", "good", "great", "fine", "okay", "sure", "done", "completed", "finished"]
        negative_words = ["no", "bad", "difficult", "hard", "can't", "cannot", "won't", "didn't", "haven't"]

        has_positive = any(word in message_lower for word in positive_words)
        has_negative = any(word in message_lower for word in negative_words)

        # Determine if activity is completed based on response
        activity_completed = has_positive and not has_negative

        # Extract metrics
        metrics = {
            "sentiment": "positive" if has_positive else "negative" if has_negative else "neutral",
            "engagement_level": "high" if len(patient_message.split()) > 5 else "medium" if len(patient_message.split()) > 2 else "low",
            "response_length": len(patient_message)
        }

        return {
            "activity_completed": activity_completed,
            "sentiment": metrics["sentiment"],
            "metrics": metrics,
            "needs_follow_up": has_negative or not has_positive
        }

    def _generate_chatbot_response(self, activity: Dict[str, Any],
                                  response_analysis: Dict[str, Any],
                                  patient_message: str) -> Dict[str, Any]:
        """Generate chatbot response based on activity and patient response"""

        activity_title = activity.get("title", "this activity")
        activity_type = activity.get("type", "general")
        chat_prompts = activity.get("chat_prompts", [])
        follow_up_questions = activity.get("follow_up_questions", [])

        # Generate appropriate response based on sentiment
        if response_analysis["sentiment"] == "positive":
            message = f"That's wonderful! I'm glad to hear about your progress with {activity_title}. "

            if response_analysis.get("activity_completed"):
                message += "Let me know if you need any help with the next step."
            else:
                message += "How can I further support you with this?"

        elif response_analysis["sentiment"] == "negative":
            message = f"I understand that {activity_title} has been challenging. "
            message += "Let's talk about what specific difficulties you're experiencing. "

            # Add supportive follow-up
            if activity_type == "medication":
                message += "Are you experiencing side effects, or is it difficult to remember?"
            elif activity_type == "physical_activity":
                message += "What's making the exercise difficult for you?"
            elif activity_type == "nutrition":
                message += "What challenges are you facing with your diet?"

        else:  # neutral
            message = f"Thank you for sharing. "
            if chat_prompts:
                # Use next prompt from the activity
                message += chat_prompts[min(1, len(chat_prompts)-1)]
            else:
                message += f"Can you tell me more about {activity_title}?"

        return {
            "message": message,
            "follow_up_questions": follow_up_questions[:2] if follow_up_questions else [],
            "next_steps": self._generate_next_steps(activity, response_analysis)
        }

    def _generate_next_steps(self, activity: Dict[str, Any],
                           response_analysis: Dict[str, Any]) -> List[str]:
        """Generate next steps based on activity and response"""

        if response_analysis.get("activity_completed"):
            return ["Move to next activity", "Continue check-in"]

        if response_analysis.get("needs_follow_up"):
            return ["Discuss challenges", "Adjust activity", "Provide support"]

        return ["Continue discussion", "Clarify activity"]

    def get_session_summary(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of chat session"""

        completed_activities = session.get("completed_activities", [])
        interactions = session.get("interactions", [])

        # Calculate metrics
        total_activities = len(completed_activities)
        total_interactions = len(interactions)
        session_duration = (
            datetime.fromisoformat(session.get("last_activity_time", session["created_at"])) -
            datetime.fromisoformat(session["created_at"])
        ).total_seconds() / 60  # in minutes

        # Analyze sentiment across interactions
        sentiments = []
        for interaction in interactions:
            if "response_analysis" in interaction:
                sentiments.append(interaction["response_analysis"].get("sentiment", "neutral"))

        sentiment_summary = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        }

        return {
            "session_id": session["session_id"],
            "chat_type": session.get("chat_type"),
            "duration_minutes": round(session_duration, 2),
            "total_activities": total_activities,
            "total_interactions": total_interactions,
            "sentiment_summary": sentiment_summary,
            "completed_activities": [
                {
                    "title": a.get("activity_title"),
                    "completion_time": a.get("completion_time"),
                    "metrics": a.get("metrics", {})
                }
                for a in completed_activities
            ],
            "overall_engagement": self._calculate_engagement_score(session),
            "recommendations": self._generate_recommendations(session)
        }

    def _calculate_engagement_score(self, session: Dict[str, Any]) -> str:
        """Calculate overall engagement score for the session"""

        interactions = session.get("interactions", [])
        if not interactions:
            return "low"

        # Calculate based on response lengths and sentiment
        total_score = 0
        for interaction in interactions:
            if "response_analysis" in interaction:
                engagement = interaction["response_analysis"].get("metrics", {}).get("engagement_level", "low")
                total_score += {"high": 3, "medium": 2, "low": 1}.get(engagement, 1)

        avg_score = total_score / len(interactions)

        if avg_score >= 2.5:
            return "high"
        elif avg_score >= 1.5:
            return "medium"
        else:
            return "low"

    def _generate_recommendations(self, session: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on session"""

        recommendations = []

        engagement_score = self._calculate_engagement_score(session)

        if engagement_score == "low":
            recommendations.append("Consider shorter, more frequent check-ins")
            recommendations.append("Use more visual cues and simple language")

        completed_count = len(session.get("completed_activities", []))
        if completed_count < 3:
            recommendations.append("Focus on fewer activities per session")
            recommendations.append("Provide more encouragement and positive reinforcement")

        # Check sentiment
        negative_responses = sum(
            1 for i in session.get("interactions", [])
            if i.get("response_analysis", {}).get("sentiment") == "negative"
        )

        if negative_responses > 2:
            recommendations.append("Follow up with caregiver about challenges")
            recommendations.append("Consider adjusting treatment plan difficulty")

        return recommendations

# -------------------------- Endpoints --------------------------

@router.post("/{patient_id}/chatbot/initialize", response_model=InitializeChatbotResponse)
def initialize_chatbot(patient_id: int, req: InitializeChatbotRequest):
    """
    Initialize a treatment chatbot for a patient using their portfolio,
    treatment plan, and chatbot config from diagnosis_treatment_planning
    """

    with CHAT_DB.lock:
        # Create chatbot instance
        chatbot = TreatmentChatbot(
            patient_id=patient_id,
            patient_portfolio=req.patient_portfolio,
            treatment_plan=req.treatment_plan,
            chatbot_config=req.chatbot_config
        )

        # Store chatbot configuration
        CHAT_DB.patient_chatbots[patient_id] = {
            "chatbot": chatbot,
            "chatbot_id": chatbot.chatbot_id,
            "created_at": chatbot.created_at,
            "status": "active"
        }

    return InitializeChatbotResponse(
        patient_id=patient_id,
        chatbot_id=chatbot.chatbot_id,
        status="active",
        message=f"Chatbot initialized successfully for patient {patient_id}"
    )

@router.post("/{patient_id}/chat/start", response_model=StartChatResponse)
def start_chat_session(patient_id: int, req: StartChatRequest):
    """
    Start a new chat session (daily check-in, treatment progress, etc.)
    """

    # Get patient's chatbot
    patient_bot = CHAT_DB.patient_chatbots.get(patient_id)
    if not patient_bot:
        raise HTTPException(404, f"No chatbot configured for patient {patient_id}. Please initialize first.")

    chatbot: TreatmentChatbot = patient_bot["chatbot"]

    # Start conversation
    conversation_context = chatbot.start_conversation(req.chat_type)

    # Create session
    session_id = uuid.uuid4().hex
    session = {
        "session_id": session_id,
        "patient_id": patient_id,
        "chat_type": req.chat_type,
        "created_at": datetime.utcnow().isoformat(),
        "current_activity_index": 0,
        "completed_activities": [],
        "interactions": [],
        "conversation_turns": 0,
        "last_activity_time": datetime.utcnow().isoformat()
    }

    with CHAT_DB.lock:
        CHAT_DB.chat_sessions[session_id] = session

    return StartChatResponse(
        session_id=session_id,
        patient_id=patient_id,
        chatbot_message=conversation_context["initial_message"],
        chat_type=req.chat_type,
        conversation_context=conversation_context
    )

@router.post("/chat/message", response_model=ChatMessageResponse)
def send_chat_message(req: ChatMessageRequest):
    """
    Send a patient message and receive chatbot response
    """

    session = CHAT_DB.chat_sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Chat session not found")

    patient_id = session["patient_id"]
    patient_bot = CHAT_DB.patient_chatbots.get(patient_id)
    if not patient_bot:
        raise HTTPException(404, f"No chatbot found for patient {patient_id}")

    chatbot: TreatmentChatbot = patient_bot["chatbot"]

    # Process patient message
    response = chatbot.process_patient_message(session, req.patient_message)

    # Store interaction
    interaction = {
        "timestamp": datetime.utcnow().isoformat(),
        "patient_message": req.patient_message,
        "chatbot_response": response["message"],
        "response_analysis": {
            "activity_completed": response.get("activity_completed"),
            "sentiment": "neutral"  # Would be extracted from response analysis
        }
    }

    with CHAT_DB.lock:
        session["interactions"].append(interaction)

    return ChatMessageResponse(
        session_id=req.session_id,
        chatbot_message=response["message"],
        follow_up_questions=response.get("follow_up_questions"),
        activity_completed=response.get("activity_completed"),
        conversation_complete=response.get("conversation_complete", False),
        next_steps=response.get("next_steps")
    )

@router.post("/chat/end", response_model=EndChatResponse)
def end_chat_session(req: EndChatRequest):
    """
    End chat session and return comprehensive JSON summary
    """

    session = CHAT_DB.chat_sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Chat session not found")

    patient_id = session["patient_id"]
    patient_bot = CHAT_DB.patient_chatbots.get(patient_id)
    if not patient_bot:
        raise HTTPException(404, f"No chatbot found for patient {patient_id}")

    chatbot: TreatmentChatbot = patient_bot["chatbot"]

    # Generate session summary
    chat_summary = chatbot.get_session_summary(session)

    # Compile metrics
    metrics = {
        "session_duration_minutes": chat_summary["duration_minutes"],
        "total_activities_completed": chat_summary["total_activities"],
        "total_interactions": chat_summary["total_interactions"],
        "engagement_score": chat_summary["overall_engagement"],
        "sentiment_distribution": chat_summary["sentiment_summary"]
    }

    # Mark session as completed
    with CHAT_DB.lock:
        session["status"] = "completed"
        session["ended_at"] = datetime.utcnow().isoformat()
        session["summary"] = chat_summary

    return EndChatResponse(
        session_id=req.session_id,
        patient_id=patient_id,
        chat_summary=chat_summary,
        interactions=session["interactions"],
        completed_activities=[a["activity_title"] for a in session["completed_activities"]],
        metrics=metrics
    )

@router.get("/{patient_id}/chat/history", response_model=GetChatHistoryResponse)
def get_chat_history(patient_id: int, limit: int = 10):
    """
    Get chat history for a patient
    """

    # Get all sessions for this patient
    patient_sessions = [
        s for s in CHAT_DB.chat_sessions.values()
        if s["patient_id"] == patient_id
    ]

    # Sort by created_at descending
    patient_sessions.sort(key=lambda x: x["created_at"], reverse=True)

    # Limit results
    limited_sessions = patient_sessions[:limit]

    # Format sessions
    formatted_sessions = []
    for session in limited_sessions:
        formatted_sessions.append({
            "session_id": session["session_id"],
            "chat_type": session["chat_type"],
            "created_at": session["created_at"],
            "status": session.get("status", "active"),
            "completed_activities_count": len(session.get("completed_activities", [])),
            "total_interactions": len(session.get("interactions", [])),
            "summary": session.get("summary")
        })

    return GetChatHistoryResponse(
        patient_id=patient_id,
        total_sessions=len(patient_sessions),
        sessions=formatted_sessions
    )

@router.get("/{patient_id}/chatbot/status")
def get_chatbot_status(patient_id: int):
    """
    Get chatbot configuration status for a patient
    """

    patient_bot = CHAT_DB.patient_chatbots.get(patient_id)
    if not patient_bot:
        return {
            "patient_id": patient_id,
            "status": "not_initialized",
            "message": "No chatbot configured for this patient"
        }

    chatbot: TreatmentChatbot = patient_bot["chatbot"]

    return {
        "patient_id": patient_id,
        "chatbot_id": chatbot.chatbot_id,
        "status": patient_bot["status"],
        "created_at": patient_bot["created_at"],
        "total_activities_tracked": len(chatbot.completed_activities),
        "treatment_goals_count": len(chatbot.treatment_goals),
        "monitoring_schedule": chatbot.monitoring_schedule
    }
