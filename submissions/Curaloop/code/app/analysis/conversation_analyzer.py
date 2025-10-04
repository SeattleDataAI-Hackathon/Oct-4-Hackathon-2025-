"""
Conversation Analysis Module
Analyzes patient conversation records to detect significant changes in symptoms and mood
Uses Claude API for intelligent analysis
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import anthropic
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Create router for conversation analysis endpoints
router = APIRouter(prefix="/api/conversation", tags=["conversation_analysis"])


class ConversationAnalyzer:
    """
    Analyzes conversation records to detect symptom and mood changes in patients.
    Returns recommendations on whether medical intervention is needed.
    """

    def __init__(self, claude_api_key: Optional[str] = None):
        """
        Initialize the conversation analyzer with Claude API

        Args:
            claude_api_key: Anthropic API key for Claude. If not provided, will try to read from environment
        """
        self.api_key = claude_api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Claude API key is required. Provide it or set ANTHROPIC_API_KEY environment variable.")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

    def analyze_conversation_record(self, conversation_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a conversation record to detect significant changes in patient symptoms and mood

        Args:
            conversation_record: Dictionary containing conversation history in JSON format
                Expected structure:
                {
                    "patient_id": str,
                    "conversation_date": str,
                    "conversations": [
                        {
                            "timestamp": str,
                            "speaker": str,  # "patient" or "bot"
                            "message": str
                        }
                    ],
                    "routine_check_in": {
                        "mood_scale": int,  # 1-10
                        "energy_level": int,  # 1-10
                        "sleep_quality": int,  # 1-10
                        "pain_level": int,  # 0-10
                        "appetite": str,  # "poor", "fair", "good"
                        "social_engagement": str,  # "isolated", "limited", "active"
                        "cognitive_clarity": int  # 1-10
                    },
                    "previous_baseline": Optional[Dict]  # Previous check-in data for comparison
                }

        Returns:
            Dictionary containing analysis results in JSON format:
            {
                "analysis_timestamp": str,
                "patient_id": str,
                "llm_analysis": {
                    "mood_assessment": {
                        "current_state": str,
                        "change_from_baseline": str,  # "improved", "stable", "declined", "significantly_declined"
                        "indicators": [str],
                        "severity": str  # "normal", "mild", "moderate", "severe"
                    },
                    "symptom_assessment": {
                        "cognitive_changes": {
                            "observed": bool,
                            "details": str,
                            "severity": str
                        },
                        "behavioral_changes": {
                            "observed": bool,
                            "details": str,
                            "severity": str
                        },
                        "physical_symptoms": {
                            "observed": bool,
                            "details": str,
                            "severity": str
                        }
                    },
                    "conversation_attitude": {
                        "engagement_level": str,  # "high", "moderate", "low", "very_low"
                        "coherence": str,  # "clear", "mostly_clear", "confused", "very_confused"
                        "emotional_tone": str,  # "positive", "neutral", "negative", "distressed"
                        "concerns_expressed": [str]
                    },
                    "routine_check_in_analysis": {
                        "significant_changes": [str],
                        "trends": str,
                        "risk_indicators": [str]
                    },
                    "clinical_insights": str,
                    "concern_level": str  # "low", "moderate", "high", "critical"
                },
                "contact_doctor_decision": {
                    "should_contact": bool,
                    "urgency": str,  # "routine", "soon", "urgent", "immediate"
                    "reasoning": str,
                    "recommended_actions": [str],
                    "specific_concerns": [str]
                }
            }
        """

        # Validate input
        self._validate_conversation_record(conversation_record)

        # Prepare the analysis prompt
        prompt = self._create_analysis_prompt(conversation_record)

        # Call Claude API for analysis
        llm_response = self._call_claude_api(prompt)

        # Parse and structure the response
        analysis_result = self._parse_llm_response(llm_response, conversation_record)

        return analysis_result

    def _validate_conversation_record(self, record: Dict[str, Any]) -> None:
        """Validate that the conversation record has required fields"""
        required_fields = ["patient_id", "conversation_date", "conversations"]

        for field in required_fields:
            if field not in record:
                raise ValueError(f"Missing required field in conversation record: {field}")

        if not isinstance(record["conversations"], list) or len(record["conversations"]) == 0:
            raise ValueError("Conversations must be a non-empty list")

    def _create_analysis_prompt(self, record: Dict[str, Any]) -> str:
        """
        Create the detailed analysis prompt for Claude API
        This is the core prompt that instructs Claude how to analyze the conversation
        """

        # Extract conversation history
        conversations = record.get("conversations", [])
        conversation_text = self._format_conversations(conversations)

        # Extract routine check-in data
        routine_check_in = record.get("routine_check_in", {})
        previous_baseline = record.get("previous_baseline", None)

        # Build the comprehensive prompt
        prompt = f"""You are a clinical AI assistant specializing in analyzing patient conversations for Alzheimer's and dementia care. Your task is to analyze a patient conversation record and determine if there are significant changes in symptoms or mood that warrant contacting their doctor.

**PATIENT ID:** {record.get('patient_id')}
**CONVERSATION DATE:** {record.get('conversation_date')}

---

## CONVERSATION HISTORY

{conversation_text}

---

## ROUTINE CHECK-IN DATA

**Current Check-in:**
- Mood Scale (1-10): {routine_check_in.get('mood_scale', 'N/A')}
- Energy Level (1-10): {routine_check_in.get('energy_level', 'N/A')}
- Sleep Quality (1-10): {routine_check_in.get('sleep_quality', 'N/A')}
- Pain Level (0-10): {routine_check_in.get('pain_level', 'N/A')}
- Appetite: {routine_check_in.get('appetite', 'N/A')}
- Social Engagement: {routine_check_in.get('social_engagement', 'N/A')}
- Cognitive Clarity (1-10): {routine_check_in.get('cognitive_clarity', 'N/A')}

{self._format_baseline_comparison(previous_baseline, routine_check_in) if previous_baseline else "**No previous baseline available for comparison**"}

---

## ANALYSIS INSTRUCTIONS

Please provide a comprehensive analysis of this patient's conversation record focusing on:

### 1. MOOD ASSESSMENT
- Evaluate the patient's current emotional state based on conversation tone and check-in data
- Determine if there are changes from the baseline (if available)
- Identify specific indicators of mood changes (positive or negative)
- Assess severity of any mood-related concerns

### 2. SYMPTOM ASSESSMENT
Analyze for changes in:
- **Cognitive function**: Memory issues, confusion, disorientation, difficulty with tasks
- **Behavioral patterns**: Agitation, aggression, withdrawal, personality changes
- **Physical symptoms**: Pain, fatigue, sleep disturbances, appetite changes

### 3. CONVERSATION ATTITUDE ANALYSIS
- **Engagement level**: How actively the patient participates in conversation
- **Coherence**: How clear and logical their responses are
- **Emotional tone**: Overall emotional quality of their communication
- **Concerns expressed**: What the patient is worried about or mentioning

### 4. ROUTINE CHECK-IN ANALYSIS
- Identify significant changes in quantitative metrics
- Recognize concerning trends or patterns
- Flag any risk indicators

### 5. CLINICAL INSIGHTS
Provide professional clinical perspective on:
- Overall patient status
- Potential underlying causes for observed changes
- Relationship between different symptoms/signs
- Risk assessment

### 6. DOCTOR CONTACT DECISION
Based on your analysis, determine:
- Should the doctor be contacted? (Yes/No)
- What is the urgency level? (routine/soon/urgent/immediate)
- What is the reasoning for this decision?
- What specific actions should be taken?
- What are the specific concerns to communicate to the doctor?

---

## OUTPUT FORMAT

Provide your analysis as a **valid JSON object** with the following structure:

```json
{{
    "mood_assessment": {{
        "current_state": "description of current mood state",
        "change_from_baseline": "improved|stable|declined|significantly_declined|no_baseline",
        "indicators": ["indicator 1", "indicator 2"],
        "severity": "normal|mild|moderate|severe"
    }},
    "symptom_assessment": {{
        "cognitive_changes": {{
            "observed": true|false,
            "details": "specific details about cognitive changes observed",
            "severity": "none|mild|moderate|severe"
        }},
        "behavioral_changes": {{
            "observed": true|false,
            "details": "specific details about behavioral changes observed",
            "severity": "none|mild|moderate|severe"
        }},
        "physical_symptoms": {{
            "observed": true|false,
            "details": "specific details about physical symptoms observed",
            "severity": "none|mild|moderate|severe"
        }}
    }},
    "conversation_attitude": {{
        "engagement_level": "high|moderate|low|very_low",
        "coherence": "clear|mostly_clear|confused|very_confused",
        "emotional_tone": "positive|neutral|negative|distressed",
        "concerns_expressed": ["concern 1", "concern 2"]
    }},
    "routine_check_in_analysis": {{
        "significant_changes": ["change 1", "change 2"],
        "trends": "description of observed trends",
        "risk_indicators": ["risk 1", "risk 2"]
    }},
    "clinical_insights": "comprehensive clinical perspective on the patient's overall status",
    "concern_level": "low|moderate|high|critical",
    "contact_doctor_decision": {{
        "should_contact": true|false,
        "urgency": "routine|soon|urgent|immediate",
        "reasoning": "detailed reasoning for the decision",
        "recommended_actions": ["action 1", "action 2"],
        "specific_concerns": ["concern 1", "concern 2"]
    }}
}}
```

**IMPORTANT:**
- Return ONLY the JSON object, no additional text
- Ensure all fields are present in your response
- Use clinical terminology appropriately
- Be specific and evidence-based in your assessments
- Consider both acute changes and gradual trends
- Prioritize patient safety in your recommendations

Please analyze this conversation record now."""

        return prompt

    def _format_conversations(self, conversations: List[Dict[str, Any]]) -> str:
        """Format conversation history for the prompt"""
        formatted = []

        for conv in conversations:
            timestamp = conv.get('timestamp', 'Unknown time')
            speaker = conv.get('speaker', 'Unknown').upper()
            message = conv.get('message', '')

            formatted.append(f"[{timestamp}] {speaker}: {message}")

        return "\n".join(formatted)

    def _format_baseline_comparison(self, previous: Dict[str, Any], current: Dict[str, Any]) -> str:
        """Format baseline comparison data"""
        comparison = "**Previous Baseline (for comparison):**\n"

        metrics = [
            ('mood_scale', 'Mood Scale'),
            ('energy_level', 'Energy Level'),
            ('sleep_quality', 'Sleep Quality'),
            ('pain_level', 'Pain Level'),
            ('appetite', 'Appetite'),
            ('social_engagement', 'Social Engagement'),
            ('cognitive_clarity', 'Cognitive Clarity')
        ]

        for key, label in metrics:
            prev_val = previous.get(key, 'N/A')
            curr_val = current.get(key, 'N/A')

            # Calculate change for numeric values
            if isinstance(prev_val, (int, float)) and isinstance(curr_val, (int, float)):
                change = curr_val - prev_val
                change_str = f" (Change: {'+' if change >= 0 else ''}{change})"
            else:
                change_str = ""

            comparison += f"- {label}: {prev_val} → {curr_val}{change_str}\n"

        return comparison

    def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API to perform the analysis

        Args:
            prompt: The analysis prompt

        Returns:
            Raw response text from Claude
        """
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # Lower temperature for more consistent clinical analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            response_text = message.content[0].text
            return response_text

        except Exception as e:
            raise RuntimeError(f"Claude API call failed: {str(e)}")

    def _parse_llm_response(self, llm_response: str, original_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse the LLM response and structure it as the final output

        Args:
            llm_response: Raw response from Claude
            original_record: Original conversation record

        Returns:
            Structured analysis result
        """
        try:
            # Try to parse as JSON
            # Sometimes Claude wraps JSON in markdown code blocks, so we need to extract it
            import re

            # Remove markdown code blocks if present
            json_match = re.search(r'```json\s*(.*?)\s*```', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find any JSON object in the response
                json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = llm_response

            # Parse the JSON
            llm_analysis = json.loads(json_str)

            # Extract the contact decision from the parsed response
            contact_decision = llm_analysis.pop("contact_doctor_decision", {
                "should_contact": False,
                "urgency": "routine",
                "reasoning": "Unable to determine from analysis",
                "recommended_actions": [],
                "specific_concerns": []
            })

            # Build the final structured result
            result = {
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "patient_id": original_record.get("patient_id"),
                "llm_analysis": llm_analysis,
                "contact_doctor_decision": contact_decision
            }

            return result

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\n\nResponse: {llm_response}")
        except Exception as e:
            raise RuntimeError(f"Error parsing LLM response: {str(e)}")

    def batch_analyze(self, conversation_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple conversation records in batch

        Args:
            conversation_records: List of conversation record dictionaries

        Returns:
            List of analysis results
        """
        results = []

        for record in conversation_records:
            try:
                result = self.analyze_conversation_record(record)
                results.append(result)
            except Exception as e:
                # Add error result for this record
                results.append({
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "patient_id": record.get("patient_id", "unknown"),
                    "error": str(e),
                    "llm_analysis": None,
                    "contact_doctor_decision": {
                        "should_contact": False,
                        "urgency": "routine",
                        "reasoning": f"Analysis failed: {str(e)}",
                        "recommended_actions": ["Retry analysis", "Manual review required"],
                        "specific_concerns": ["Analysis error"]
                    }
                })

        return results


# ==================== FastAPI Endpoints ====================

# Request/Response Models
class ConversationMessage(BaseModel):
    timestamp: str
    speaker: str  # "patient" or "bot"
    message: str

class RoutineCheckIn(BaseModel):
    mood_scale: Optional[int] = None
    energy_level: Optional[int] = None
    sleep_quality: Optional[int] = None
    pain_level: Optional[int] = None
    appetite: Optional[str] = None
    social_engagement: Optional[str] = None
    cognitive_clarity: Optional[int] = None

class ConversationRecord(BaseModel):
    patient_id: str
    conversation_date: str
    conversations: List[ConversationMessage]
    routine_check_in: Optional[RoutineCheckIn] = None
    previous_baseline: Optional[Dict[str, Any]] = None

class AnalyzeConversationRequest(BaseModel):
    conversation_record: ConversationRecord
    claude_api_key: Optional[str] = None  # Can be provided per request or use env variable

class AnalyzeConversationResponse(BaseModel):
    analysis_timestamp: str
    patient_id: str
    llm_analysis: Dict[str, Any]
    contact_doctor_decision: Dict[str, Any]

class BatchAnalyzeRequest(BaseModel):
    conversation_records: List[ConversationRecord]
    claude_api_key: Optional[str] = None

class BatchAnalyzeResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_analyzed: int
    errors: int

# Global analyzer instance (will be initialized with API key)
_analyzer_instance: Optional[ConversationAnalyzer] = None

def get_analyzer(api_key: Optional[str] = None) -> ConversationAnalyzer:
    """Get or create analyzer instance with API key"""
    global _analyzer_instance

    # If API key provided, create new instance
    if api_key:
        return ConversationAnalyzer(claude_api_key=api_key)

    # Try to use existing instance or create with env variable
    if _analyzer_instance is None:
        try:
            _analyzer_instance = ConversationAnalyzer()
        except ValueError:
            raise HTTPException(
                status_code=500,
                detail="Claude API key not configured. Provide it in request or set ANTHROPIC_API_KEY environment variable."
            )

    return _analyzer_instance

@router.post("/analyze", response_model=AnalyzeConversationResponse)
def analyze_conversation(request: AnalyzeConversationRequest):
    """
    Analyze a single conversation record to detect symptom/mood changes
    and determine if doctor contact is needed
    """
    try:
        # Get analyzer instance
        analyzer = get_analyzer(request.claude_api_key)

        # Convert Pydantic model to dict
        record_dict = request.conversation_record.dict()

        # Perform analysis
        result = analyzer.analyze_conversation_record(record_dict)

        return AnalyzeConversationResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/analyze/batch", response_model=BatchAnalyzeResponse)
def batch_analyze_conversations(request: BatchAnalyzeRequest):
    """
    Analyze multiple conversation records in batch
    """
    try:
        # Get analyzer instance
        analyzer = get_analyzer(request.claude_api_key)

        # Convert Pydantic models to dicts
        records_dicts = [rec.dict() for rec in request.conversation_records]

        # Perform batch analysis
        results = analyzer.batch_analyze(records_dicts)

        # Count errors
        errors = sum(1 for r in results if "error" in r)

        return BatchAnalyzeResponse(
            results=results,
            total_analyzed=len(results),
            errors=errors
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/health")
def conversation_analyzer_health():
    """Health check for conversation analyzer"""
    api_key_configured = os.environ.get("ANTHROPIC_API_KEY") is not None

    return {
        "status": "healthy",
        "service": "Conversation Analyzer",
        "claude_api_configured": api_key_configured
    }


# Example usage and testing
if __name__ == "__main__":
    # Example conversation record
    example_record = {
        "patient_id": "P12345",
        "conversation_date": "2025-10-04T14:30:00Z",
        "conversations": [
            {
                "timestamp": "2025-10-04T14:30:00Z",
                "speaker": "bot",
                "message": "Good afternoon! How are you feeling today?"
            },
            {
                "timestamp": "2025-10-04T14:30:15Z",
                "speaker": "patient",
                "message": "I'm... I'm not sure. I feel confused."
            },
            {
                "timestamp": "2025-10-04T14:30:30Z",
                "speaker": "bot",
                "message": "I understand. Can you tell me more about how you're feeling confused?"
            },
            {
                "timestamp": "2025-10-04T14:30:50Z",
                "speaker": "patient",
                "message": "I can't remember if I ate breakfast. And I don't know where my daughter is."
            },
            {
                "timestamp": "2025-10-04T14:31:10Z",
                "speaker": "bot",
                "message": "Let me help you. Your daughter visited yesterday and she'll be back tomorrow. Did you sleep well last night?"
            },
            {
                "timestamp": "2025-10-04T14:31:30Z",
                "speaker": "patient",
                "message": "No... I kept waking up. My head hurts."
            }
        ],
        "routine_check_in": {
            "mood_scale": 3,
            "energy_level": 4,
            "sleep_quality": 2,
            "pain_level": 6,
            "appetite": "poor",
            "social_engagement": "isolated",
            "cognitive_clarity": 3
        },
        "previous_baseline": {
            "mood_scale": 6,
            "energy_level": 7,
            "sleep_quality": 7,
            "pain_level": 2,
            "appetite": "good",
            "social_engagement": "active",
            "cognitive_clarity": 6
        }
    }

    # Note: To run this example, you need to set ANTHROPIC_API_KEY environment variable
    # analyzer = ConversationAnalyzer()
    # result = analyzer.analyze_conversation_record(example_record)
    # print(json.dumps(result, indent=2))
