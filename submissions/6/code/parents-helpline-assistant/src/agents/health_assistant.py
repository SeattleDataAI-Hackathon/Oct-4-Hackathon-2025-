"""Health Assistant AI agent using Claude API."""
import anthropic
from typing import List, Dict, Optional
import os
import time
from src.utils.logger import get_logger
from src.utils.config import settings
from .prompts import SYSTEM_PROMPT, SAFETY_DISCLAIMER

logger = get_logger(__name__)


class HealthAssistant:
    """
    Health Assistant AI agent for conversing with parents about their baby's health.
    Uses Claude API for natural language processing and empathetic responses.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Health Assistant.

        Args:
            api_key: Anthropic API key (if not provided, uses from settings)
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model
        self.max_tokens = 2048

    async def chat(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        child_age_months: Optional[int] = None,
        include_safety_disclaimer: bool = False,
        is_authenticated: bool = False,
    ) -> Dict[str, any]:
        """
        Send a message to the health assistant and get a response.

        Args:
            message: User's message
            conversation_history: List of previous messages [{"role": "user"|"assistant", "content": "..."}]
            child_age_months: Child's age in months (0-36)
            include_safety_disclaimer: Whether to append safety disclaimer

        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()

        try:
            # Build system prompt with context
            system_prompt = SYSTEM_PROMPT

            if child_age_months is not None:
                system_prompt += f"\n\nCurrent baby's age: {child_age_months} months old."

            # Prepare messages
            messages = conversation_history + [{"role": "user", "content": message}]

            logger.info(f"Sending request to Claude API. Message length: {len(message)} chars")

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt,
                messages=messages,
            )

            # Extract response
            assistant_message = response.content[0].text

            # Add safety disclaimer if requested
            if include_safety_disclaimer:
                assistant_message += f"\n\n{SAFETY_DISCLAIMER}"

            # Calculate response time
            response_time = time.time() - start_time

            logger.info(f"Received response from Claude API. Response time: {response_time:.2f}s")

            # Check if response time exceeds threshold
            if response_time > settings.max_response_time_seconds:
                logger.warning(f"Response time ({response_time:.2f}s) exceeded threshold ({settings.max_response_time_seconds}s)")

            return {
                "content": assistant_message,
                "response_time": response_time,
                "model": self.model,
                "tokens_used": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens,
                },
            }

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return {
                "content": "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment, or if this is urgent, please contact your pediatrician or call your local nurse helpline.",
                "error": str(e),
                "response_time": time.time() - start_time,
            }

        except Exception as e:
            logger.error(f"Unexpected error in chat: {e}")
            return {
                "content": "I apologize, but something went wrong. If your baby needs immediate medical attention, please call 911 or go to the nearest emergency room. Otherwise, please try again or contact your healthcare provider.",
                "error": str(e),
                "response_time": time.time() - start_time,
            }

    def analyze_symptoms(self, symptoms: List[Dict[str, any]]) -> Dict[str, any]:
        """
        Analyze collected symptoms and detect red flags.

        Args:
            symptoms: List of symptom dictionaries with name, severity, duration

        Returns:
            Analysis result with red flags and urgency level
        """
        red_flags = []
        urgency = "routine"  # routine, urgent, emergency

        symptom_names = [s.get("symptom_name", "").lower() for s in symptoms]
        symptom_details = {s.get("symptom_name", "").lower(): s for s in symptoms}

        # Check for emergency red flags
        emergency_keywords = [
            "difficulty breathing",
            "blue lips",
            "blue face",
            "seizure",
            "unresponsive",
            "unconscious",
            "severe allergic reaction",
        ]

        for keyword in emergency_keywords:
            if any(keyword in name for name in symptom_names):
                red_flags.append(f"EMERGENCY: {keyword.title()} detected")
                urgency = "emergency"

        # Check for urgent conditions
        if urgency != "emergency":
            # High fever in young infants
            if "fever" in symptom_names or "high temperature" in symptom_names:
                # Check if severity is high or if there's additional context
                urgency = "urgent"
                red_flags.append("Fever detected - age-appropriate assessment needed")

            # Dehydration signs
            dehydration_signs = ["no wet diapers", "dry mouth", "no tears", "sunken fontanel"]
            if any(sign in name for sign in dehydration_signs for name in symptom_names):
                urgency = "urgent"
                red_flags.append("Possible dehydration signs detected")

            # Severe pain or inconsolable crying
            pain_keywords = ["inconsolable", "severe pain", "won't stop crying"]
            if any(keyword in name for name in symptom_names for keyword in pain_keywords):
                urgency = "urgent"
                red_flags.append("Severe discomfort detected")

        return {
            "urgency": urgency,
            "red_flags": red_flags,
            "requires_immediate_care": urgency == "emergency",
            "requires_urgent_evaluation": urgency == "urgent",
        }

    def format_recommendations(
        self,
        recommendations: List[Dict[str, str]],
        home_remedies: List[Dict[str, str]] = None,
    ) -> str:
        """
        Format recommendations in a parent-friendly way.

        Args:
            recommendations: List of recommendation dictionaries
            home_remedies: Optional list of home remedy dictionaries

        Returns:
            Formatted string with recommendations
        """
        output = "## Recommended Next Steps\n\n"

        # Group recommendations by type
        monitoring = [r for r in recommendations if r.get("recommendation_type") == "monitoring"]
        medications = [r for r in recommendations if r.get("recommendation_type") == "medication"]
        escalation = [r for r in recommendations if r.get("recommendation_type") == "escalation"]
        other = [r for r in recommendations if r.get("recommendation_type") not in ["monitoring", "medication", "escalation"]]

        if monitoring:
            output += "### 👀 Monitor These Signs:\n"
            for rec in monitoring:
                output += f"- {rec.get('description', '')}\n"
            output += "\n"

        if medications:
            output += "### 💊 Medication/Treatment:\n"
            for rec in medications:
                output += f"- {rec.get('description', '')}\n"
                if rec.get('safety_notes'):
                    output += f"  ⚠️ *{rec.get('safety_notes')}*\n"
            output += "\n"

        if other:
            output += "### 🏥 General Care:\n"
            for rec in other:
                output += f"- {rec.get('description', '')}\n"
            output += "\n"

        if home_remedies:
            output += "### 🏡 Home Remedies:\n"
            for remedy in home_remedies:
                output += f"**{remedy.get('remedy_name', '')}**\n"
                output += f"{remedy.get('description', '')}\n\n"
                output += f"*Instructions:* {remedy.get('instructions', '')}\n\n"
                if remedy.get('safety_notes'):
                    output += f"⚠️ *Safety Note: {remedy.get('safety_notes')}*\n\n"

        if escalation:
            output += "### ⚕️ When to Seek Medical Care:\n"
            for rec in escalation:
                output += f"- {rec.get('description', '')}\n"
            output += "\n"

        return output
