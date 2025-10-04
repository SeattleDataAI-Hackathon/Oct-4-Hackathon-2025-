"""
Diagnosis and Treatment Planning Module
Handles Alzheimer's prediction analysis and generates comprehensive treatment plans
"""

from typing import Dict, Any, Optional
from datetime import datetime
import sys
import os
import requests
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Add ml directory to path for Alzheimer's predictor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ml'))

try:
    from alzheimers_predictor import AlzheimersPredictor
    PREDICTOR_AVAILABLE = True
except ImportError:
    PREDICTOR_AVAILABLE = False
    print("Warning: Alzheimer's predictor not available")

class DiagnosisTreatmentPlanner:
    """
    Handles diagnosis analysis and treatment planning for Alzheimer's patients
    """
    
    def __init__(self, llm_api_key: Optional[str] = None, llm_provider: str = "openai"):
        self.predictor = None
        self.llm_api_key = llm_api_key
        self.llm_provider = llm_provider
        self._initialize_predictor()
    
    def _initialize_predictor(self):
        """Initialize the Alzheimer's predictor model"""
        if not PREDICTOR_AVAILABLE:
            return
        
        try:
            self.predictor = AlzheimersPredictor()
            model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'alzheimers_model.joblib')
            scaler_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'alzheimers_scaler.joblib')
            feature_names_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'feature_names.joblib')
            
            self.predictor.load_model(model_path=model_path, scaler_path=scaler_path, feature_names_path=feature_names_path)
            print("✓ Alzheimer's predictor loaded successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not load Alzheimer's predictor: {e}")
            self.predictor = None
    
    def analyze_intake_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze patient intake data and generate comprehensive diagnosis and treatment plan
        
        Args:
            patient_data: Dictionary containing patient intake information
            
        Returns:
            Dictionary containing analysis results
        """
        
        if self.predictor is None:
            raise ValueError("Alzheimer's predictor model not available")
        
        # Ensure we have the required fields for prediction
        patient_data = self._prepare_patient_data(patient_data)
        
        # Run Alzheimer's prediction
        prediction_result = self.predictor.predict_diagnosis(patient_data)
        
        # Generate comprehensive analysis
        analysis = self._generate_comprehensive_analysis(patient_data, prediction_result)
        
        return {
            "alzheimers_prediction": prediction_result,
            "patient_portfolio": analysis["patient_portfolio"],
            "diagnosis_analysis": analysis["diagnosis_analysis"],
            "treatment_plan": analysis["treatment_plan"],
            "companion_chatbot_config": analysis["companion_chatbot_config"],
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analysis_method": analysis["analysis_method"]
        }
    
    def _prepare_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare patient data by filling missing fields with appropriate defaults"""
        
        required_fields = [
            'Age', 'Gender', 'Ethnicity', 'EducationLevel', 'BMI', 'Smoking', 
            'AlcoholConsumption', 'PhysicalActivity', 'DietQuality', 'SleepQuality',
            'FamilyHistoryAlzheimers', 'CardiovascularDisease', 'Diabetes', 
            'Depression', 'HeadInjury', 'Hypertension', 'SystolicBP', 'DiastolicBP',
            'CholesterolTotal', 'CholesterolLDL', 'CholesterolHDL', 
            'CholesterolTriglycerides', 'MMSE', 'FunctionalAssessment',
            'MemoryComplaints', 'BehavioralProblems', 'ADL', 'Confusion',
            'Disorientation', 'PersonalityChanges', 'DifficultyCompletingTasks',
            'Forgetfulness'
        ]
        
        # Create a copy to avoid modifying the original
        prepared_data = patient_data.copy()
        
        # Fill missing fields with default values
        for field in required_fields:
            if field not in prepared_data:
                if field in ['Age', 'Gender', 'Ethnicity', 'EducationLevel']:
                    prepared_data[field] = 0  # Default numeric values
                elif field in ['BMI', 'SystolicBP', 'DiastolicBP', 'CholesterolTotal', 
                              'CholesterolLDL', 'CholesterolHDL', 'CholesterolTriglycerides']:
                    prepared_data[field] = None  # Optional fields
                else:
                    prepared_data[field] = 0  # Default to 0 for binary/scale fields
        
        return prepared_data
    
    def _generate_comprehensive_analysis(self, patient_data: Dict[str, Any], 
                                       prediction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis including portfolio, diagnosis, and treatment plan"""
        
        alzheimers_prob = prediction_result.get("probability_alzheimers", 0)
        risk_level = "High" if alzheimers_prob > 0.7 else "Medium" if alzheimers_prob > 0.4 else "Low"
        
        # Check if LLM is available
        use_llm = self.llm_api_key is not None
        
        # Generate treatment plan first
        treatment_plan = self._generate_treatment_plan(patient_data, prediction_result, risk_level)
        
        # Generate diagnosis analysis
        diagnosis_analysis = self._generate_diagnosis_analysis(patient_data, prediction_result, risk_level)
        
        # Generate chatbot config - use original version if no LLM, enhanced version if LLM available
        if use_llm:
            chatbot_config = self._generate_chatbot_config(patient_data, prediction_result, risk_level, treatment_plan)
        else:
            chatbot_config = self._generate_original_chatbot_config(patient_data, prediction_result, risk_level)
        
        return {
            "patient_portfolio": self._generate_patient_portfolio(patient_data),
            "diagnosis_analysis": diagnosis_analysis,
            "treatment_plan": treatment_plan,
            "companion_chatbot_config": chatbot_config,
            "analysis_method": "llm_enhanced" if use_llm else "structured"
        }
    
    def _generate_patient_portfolio(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive patient portfolio"""
        
        return {
            "demographics": {
                "age": patient_data.get("Age"),
                "gender": "Male" if patient_data.get("Gender") == 1 else "Female",
                "education_level": patient_data.get("EducationLevel", 0)
            },
            "health_metrics": {
                "bmi": patient_data.get("BMI"),
                "mmse_score": patient_data.get("MMSE"),
                "adl_score": patient_data.get("ADL"),
                "functional_assessment": patient_data.get("FunctionalAssessment")
            },
            "risk_factors": {
                "family_history_alzheimers": patient_data.get("FamilyHistoryAlzheimers") == 1,
                "cardiovascular_disease": patient_data.get("CardiovascularDisease") == 1,
                "diabetes": patient_data.get("Diabetes") == 1,
                "depression": patient_data.get("Depression") == 1,
                "hypertension": patient_data.get("Hypertension") == 1,
                "head_injury": patient_data.get("HeadInjury") == 1
            },
            "lifestyle_factors": {
                "smoking": patient_data.get("Smoking") == 1,
                "alcohol_consumption": patient_data.get("AlcoholConsumption", 0),
                "physical_activity": patient_data.get("PhysicalActivity", 0),
                "diet_quality": patient_data.get("DietQuality", 0),
                "sleep_quality": patient_data.get("SleepQuality", 0)
            }
        }
    
    def _generate_diagnosis_analysis(self, patient_data: Dict[str, Any], 
                                   prediction_result: Dict[str, Any], 
                                   risk_level: str) -> Dict[str, Any]:
        """Generate diagnosis analysis using LLM"""
        
        # Prepare context for LLM
        context = {
            "patient_profile": {
                "age": patient_data.get("Age"),
                "gender": "Male" if patient_data.get("Gender") == 1 else "Female",
                "mmse_score": patient_data.get("MMSE"),
                "adl_score": patient_data.get("ADL"),
                "family_history": "Yes" if patient_data.get("FamilyHistoryAlzheimers") == 1 else "No",
                "cardiovascular_disease": "Yes" if patient_data.get("CardiovascularDisease") == 1 else "No",
                "diabetes": "Yes" if patient_data.get("Diabetes") == 1 else "No",
                "depression": "Yes" if patient_data.get("Depression") == 1 else "No",
                "hypertension": "Yes" if patient_data.get("Hypertension") == 1 else "No"
            },
            "prediction": {
                "diagnosis": prediction_result.get("diagnosis_label"),
                "alzheimers_probability": prediction_result.get("probability_alzheimers"),
                "no_alzheimers_probability": prediction_result.get("probability_no_alzheimers")
            },
            "symptoms": {
                "memory_complaints": patient_data.get("MemoryComplaints") == 1,
                "behavioral_changes": patient_data.get("BehavioralProblems") == 1,
                "confusion": patient_data.get("Confusion") == 1,
                "disorientation": patient_data.get("Disorientation") == 1,
                "personality_changes": patient_data.get("PersonalityChanges") == 1,
                "task_difficulty": patient_data.get("DifficultyCompletingTasks") == 1,
                "forgetfulness": patient_data.get("Forgetfulness") == 1
            }
        }
        
        # Generate LLM analysis
        llm_analysis = self._call_llm_for_diagnosis_analysis(context, risk_level)
        
        # Fallback to structured analysis if LLM fails
        if not llm_analysis:
            return self._generate_structured_diagnosis_analysis(patient_data, prediction_result, risk_level)
        
        return llm_analysis
    
    def _generate_treatment_plan(self, patient_data: Dict[str, Any], 
                               prediction_result: Dict[str, Any], 
                               risk_level: str) -> Dict[str, Any]:
        """Generate comprehensive treatment plan using LLM"""
        
        # Prepare context for LLM
        context = {
            "patient_profile": {
                "age": patient_data.get("Age"),
                "gender": "Male" if patient_data.get("Gender") == 1 else "Female",
                "mmse_score": patient_data.get("MMSE"),
                "adl_score": patient_data.get("ADL"),
                "family_history": "Yes" if patient_data.get("FamilyHistoryAlzheimers") == 1 else "No",
                "cardiovascular_disease": "Yes" if patient_data.get("CardiovascularDisease") == 1 else "No",
                "diabetes": "Yes" if patient_data.get("Diabetes") == 1 else "No",
                "depression": "Yes" if patient_data.get("Depression") == 1 else "No",
                "hypertension": "Yes" if patient_data.get("Hypertension") == 1 else "No"
            },
            "prediction": {
                "diagnosis": prediction_result.get("diagnosis_label"),
                "alzheimers_probability": prediction_result.get("probability_alzheimers"),
                "risk_level": risk_level
            },
            "symptoms": {
                "memory_complaints": patient_data.get("MemoryComplaints") == 1,
                "behavioral_changes": patient_data.get("BehavioralProblems") == 1,
                "confusion": patient_data.get("Confusion") == 1,
                "disorientation": patient_data.get("Disorientation") == 1,
                "personality_changes": patient_data.get("PersonalityChanges") == 1,
                "task_difficulty": patient_data.get("DifficultyCompletingTasks") == 1,
                "forgetfulness": patient_data.get("Forgetfulness") == 1
            },
            "lifestyle_factors": {
                "smoking": patient_data.get("Smoking") == 1,
                "alcohol_consumption": patient_data.get("AlcoholConsumption", 0),
                "physical_activity": patient_data.get("PhysicalActivity", 0),
                "diet_quality": patient_data.get("DietQuality", 0),
                "sleep_quality": patient_data.get("SleepQuality", 0)
            }
        }
        
        # Generate LLM treatment plan
        llm_plan = self._call_llm_for_treatment_plan(context, risk_level)
        
        # Fallback to structured plan if LLM fails
        if not llm_plan:
            return self._generate_structured_treatment_plan(patient_data, prediction_result, risk_level)
        
        return llm_plan
    
    def _generate_chatbot_config(self, patient_data: Dict[str, Any], 
                               prediction_result: Dict[str, Any], 
                               risk_level: str, 
                               treatment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate companion chatbot configuration that executes treatment plan through chat"""
        
        # Base configuration
        config = {
            "personality": "Supportive, patient, and encouraging",
            "communication_style": "Simple, clear language with repetition for important information",
            "treatment_execution": {
                "immediate_actions": self._convert_to_chat_activities(treatment_plan.get("immediate_actions", [])),
                "lifestyle_interventions": self._convert_to_chat_activities(treatment_plan.get("lifestyle_interventions", [])),
                "medical_management": self._convert_to_chat_activities(treatment_plan.get("medical_management", [])),
                "support_services": self._convert_to_chat_activities(treatment_plan.get("support_services", [])),
                "personalized_recommendations": self._convert_to_chat_activities(treatment_plan.get("personalized_recommendations", [])),
                "risk_specific_interventions": self._convert_to_chat_activities(treatment_plan.get("risk_specific_interventions", [])),
                "caregiver_guidance": self._convert_to_chat_activities(treatment_plan.get("caregiver_guidance", []))
            },
            "daily_activities": [
                "Morning routine reminders",
                "Medication reminders",
                "Meal planning assistance",
                "Exercise encouragement",
                "Memory games and cognitive exercises"
            ],
            "safety_features": [
                "Emergency contact integration",
                "Location tracking for disorientation episodes",
                "Medication adherence monitoring",
                "Fall risk assessment"
            ],
            "personalization": {
                "adapt_to_cognitive_level": True,
                "use_visual_cues": True,
                "provide_positive_reinforcement": True,
                "maintain_routine_consistency": True
            },
            "conversation_flows": self._generate_conversation_flows(treatment_plan, risk_level),
            "monitoring_schedule": treatment_plan.get("monitoring_schedule", {}),
            "treatment_goals": self._extract_treatment_goals(treatment_plan)
        }
        
        # Customize based on cognitive level
        mmse_score = patient_data.get("MMSE", 30)
        if mmse_score < 18:
            config["communication_style"] = "Very simple language, frequent repetition, visual cues essential"
            config["daily_activities"].extend([
                "Basic orientation questions",
                "Simple memory exercises",
                "Daily routine reinforcement"
            ])
            # Simplify treatment execution for severe cognitive impairment
            config["treatment_execution"] = self._simplify_for_cognitive_level(config["treatment_execution"], "severe")
        elif mmse_score < 24:
            config["communication_style"] = "Simple language with occasional repetition"
            config["daily_activities"].extend([
                "Moderate cognitive exercises",
                "Social interaction prompts",
                "Hobby and interest reminders"
            ])
            # Moderate simplification for mild cognitive impairment
            config["treatment_execution"] = self._simplify_for_cognitive_level(config["treatment_execution"], "mild")
        
        # Add risk-specific features
        if risk_level == "High":
            config["safety_features"].extend([
                "24/7 monitoring alerts",
                "Caregiver notification system",
                "Emergency response integration"
            ])
            config["personalization"]["frequent_check_ins"] = True
            # Increase treatment intensity for high-risk patients
            config["treatment_execution"]["intensity"] = "high"
            config["monitoring_schedule"]["check_in_frequency"] = "daily"
        elif risk_level == "Medium":
            config["treatment_execution"]["intensity"] = "moderate"
            config["monitoring_schedule"]["check_in_frequency"] = "weekly"
        else:
            config["treatment_execution"]["intensity"] = "low"
            config["monitoring_schedule"]["check_in_frequency"] = "bi-weekly"
        
        return config
    
    def _assess_mmse_severity(self, mmse_score: int) -> str:
        """Assess MMSE severity level"""
        if mmse_score >= 24:
            return "Normal"
        elif mmse_score >= 18:
            return "Mild"
        elif mmse_score >= 10:
            return "Moderate"
        else:
            return "Severe"
    
    def _assess_functional_independence(self, adl_score: int) -> str:
        """Assess functional independence level"""
        if adl_score >= 80:
            return "High"
        elif adl_score >= 50:
            return "Moderate"
        else:
            return "Low"
    
    def _call_llm_for_diagnosis_analysis(self, context: Dict[str, Any], risk_level: str) -> Optional[Dict[str, Any]]:
        """Call LLM to generate diagnosis analysis"""
        
        if not self.llm_api_key:
            return None
        
        prompt = f"""
        As a medical AI assistant, analyze the following patient data and provide a comprehensive diagnosis analysis for Alzheimer's disease risk assessment.

        Patient Profile:
        - Age: {context['patient_profile']['age']}
        - Gender: {context['patient_profile']['gender']}
        - MMSE Score: {context['patient_profile']['mmse_score']}
        - ADL Score: {context['patient_profile']['adl_score']}
        - Family History of Alzheimer's: {context['patient_profile']['family_history']}
        - Cardiovascular Disease: {context['patient_profile']['cardiovascular_disease']}
        - Diabetes: {context['patient_profile']['diabetes']}
        - Depression: {context['patient_profile']['depression']}
        - Hypertension: {context['patient_profile']['hypertension']}

        ML Prediction:
        - Diagnosis: {context['prediction']['diagnosis']}
        - Alzheimer's Probability: {context['prediction']['alzheimers_probability']:.2%}
        - No Alzheimer's Probability: {context['prediction']['no_alzheimers_probability']:.2%}

        Symptoms Present:
        - Memory Complaints: {context['symptoms']['memory_complaints']}
        - Behavioral Changes: {context['symptoms']['behavioral_changes']}
        - Confusion: {context['symptoms']['confusion']}
        - Disorientation: {context['symptoms']['disorientation']}
        - Personality Changes: {context['symptoms']['personality_changes']}
        - Task Difficulty: {context['symptoms']['task_difficulty']}
        - Forgetfulness: {context['symptoms']['forgetfulness']}

        Risk Level: {risk_level}

        Please provide a comprehensive diagnosis analysis in JSON format with the following structure:
        {{
            "predicted_diagnosis": "string",
            "risk_level": "string",
            "confidence_score": float,
            "key_indicators": {{
                "cognitive_impairment": boolean,
                "memory_complaints": boolean,
                "behavioral_changes": boolean,
                "confusion": boolean,
                "disorientation": boolean,
                "personality_changes": boolean,
                "task_difficulty": boolean,
                "forgetfulness": boolean
            }},
            "severity_assessment": {{
                "mmse_severity": "string",
                "functional_independence": "string"
            }},
            "clinical_insights": "string",
            "differential_considerations": ["string"],
            "recommended_follow_up": ["string"]
        }}

        Focus on providing clinical insights, differential considerations, and specific follow-up recommendations based on the patient's profile and symptoms.
        """
        
        try:
            if self.llm_provider == "openai":
                return self._call_openai_api(prompt)
            else:
                # Add other LLM providers here
                return None
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None
    
    def _call_llm_for_treatment_plan(self, context: Dict[str, Any], risk_level: str) -> Optional[Dict[str, Any]]:
        """Call LLM to generate treatment plan"""
        
        if not self.llm_api_key:
            return None
        
        prompt = f"""
        As a medical AI assistant, create a comprehensive, personalized treatment plan for this patient based on their Alzheimer's risk assessment.

        Patient Profile:
        - Age: {context['patient_profile']['age']}
        - Gender: {context['patient_profile']['gender']}
        - MMSE Score: {context['patient_profile']['mmse_score']}
        - ADL Score: {context['patient_profile']['adl_score']}
        - Family History of Alzheimer's: {context['patient_profile']['family_history']}
        - Cardiovascular Disease: {context['patient_profile']['cardiovascular_disease']}
        - Diabetes: {context['patient_profile']['diabetes']}
        - Depression: {context['patient_profile']['depression']}
        - Hypertension: {context['patient_profile']['hypertension']}

        Risk Assessment:
        - Diagnosis: {context['prediction']['diagnosis']}
        - Alzheimer's Probability: {context['prediction']['alzheimers_probability']:.2%}
        - Risk Level: {risk_level}

        Symptoms Present:
        - Memory Complaints: {context['symptoms']['memory_complaints']}
        - Behavioral Changes: {context['symptoms']['behavioral_changes']}
        - Confusion: {context['symptoms']['confusion']}
        - Disorientation: {context['symptoms']['disorientation']}
        - Personality Changes: {context['symptoms']['personality_changes']}
        - Task Difficulty: {context['symptoms']['task_difficulty']}
        - Forgetfulness: {context['symptoms']['forgetfulness']}

        Lifestyle Factors:
        - Smoking: {context['lifestyle_factors']['smoking']}
        - Alcohol Consumption: {context['lifestyle_factors']['alcohol_consumption']}
        - Physical Activity: {context['lifestyle_factors']['physical_activity']}
        - Diet Quality: {context['lifestyle_factors']['diet_quality']}
        - Sleep Quality: {context['lifestyle_factors']['sleep_quality']}

        Please create a personalized treatment plan in JSON format with the following structure:
        {{
            "immediate_actions": ["string"],
            "lifestyle_interventions": ["string"],
            "medical_management": ["string"],
            "support_services": ["string"],
            "monitoring_schedule": {{
                "cognitive_assessment": "string",
                "medical_follow_up": "string",
                "lifestyle_review": "string",
                "caregiver_check_in": "string"
            }},
            "personalized_recommendations": ["string"],
            "risk_specific_interventions": ["string"],
            "caregiver_guidance": ["string"]
        }}

        Tailor the plan specifically to this patient's risk level, symptoms, and lifestyle factors. Include personalized recommendations and risk-specific interventions.
        """
        
        try:
            if self.llm_provider == "openai":
                return self._call_openai_api(prompt)
            else:
                # Add other LLM providers here
                return None
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None
    
    def _call_openai_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI API for LLM analysis"""
        
        try:
            headers = {
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant specializing in Alzheimer's disease diagnosis and treatment planning. Provide accurate, evidence-based medical analysis in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract JSON from the response
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json.loads(json_match.group())
                    return None
            else:
                print(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            return None
    
    def _generate_structured_diagnosis_analysis(self, patient_data: Dict[str, Any], 
                                              prediction_result: Dict[str, Any], 
                                              risk_level: str) -> Dict[str, Any]:
        """Fallback structured diagnosis analysis when LLM is not available"""
        
        return {
            "predicted_diagnosis": prediction_result.get("diagnosis_label"),
            "risk_level": risk_level,
            "confidence_score": max(prediction_result.get("probability_alzheimers", 0), 
                                  prediction_result.get("probability_no_alzheimers", 0)),
            "key_indicators": {
                "cognitive_impairment": patient_data.get("MMSE", 30) < 24,
                "memory_complaints": patient_data.get("MemoryComplaints") == 1,
                "behavioral_changes": patient_data.get("BehavioralProblems") == 1,
                "confusion": patient_data.get("Confusion") == 1,
                "disorientation": patient_data.get("Disorientation") == 1,
                "personality_changes": patient_data.get("PersonalityChanges") == 1,
                "task_difficulty": patient_data.get("DifficultyCompletingTasks") == 1,
                "forgetfulness": patient_data.get("Forgetfulness") == 1
            },
            "severity_assessment": {
                "mmse_severity": self._assess_mmse_severity(patient_data.get("MMSE", 30)),
                "functional_independence": self._assess_functional_independence(patient_data.get("ADL", 100))
            },
            "clinical_insights": f"Patient shows {risk_level.lower()} risk for Alzheimer's disease based on ML prediction and clinical indicators.",
            "differential_considerations": ["Mild Cognitive Impairment", "Vascular Dementia", "Depression-related cognitive changes"],
            "recommended_follow_up": ["Neuropsychological evaluation", "Neurology consultation", "Cognitive monitoring"]
        }
    
    def _generate_structured_treatment_plan(self, patient_data: Dict[str, Any], 
                                          prediction_result: Dict[str, Any], 
                                          risk_level: str) -> Dict[str, Any]:
        """Fallback structured treatment plan when LLM is not available"""
        
        # Base treatment plan
        treatment_plan = {
            "immediate_actions": [
                "Schedule comprehensive neuropsychological evaluation",
                "Consult with neurologist for detailed assessment",
                "Begin cognitive monitoring and tracking"
            ],
            "lifestyle_interventions": [
                "Implement Mediterranean diet recommendations",
                "Establish regular physical exercise routine",
                "Optimize sleep hygiene and quality",
                "Engage in cognitive stimulation activities"
            ],
            "medical_management": [
                "Review current medications for cognitive impact",
                "Consider cholinesterase inhibitors if appropriate",
                "Monitor and manage cardiovascular risk factors",
                "Address depression and anxiety if present"
            ],
            "support_services": [
                "Connect with Alzheimer's Association resources",
                "Establish caregiver support network",
                "Plan for future care needs and legal considerations",
                "Implement safety measures at home"
            ],
            "monitoring_schedule": {
                "cognitive_assessment": "Every 6 months",
                "medical_follow_up": "Every 3 months",
                "lifestyle_review": "Monthly",
                "caregiver_check_in": "Weekly"
            },
            "personalized_recommendations": [],
            "risk_specific_interventions": [],
            "caregiver_guidance": []
        }
        
        # Customize based on risk level and specific patient factors
        if risk_level == "High":
            treatment_plan["immediate_actions"].insert(0, "Urgent neurology consultation")
            treatment_plan["medical_management"].insert(0, "Consider immediate medication intervention")
            treatment_plan["monitoring_schedule"]["cognitive_assessment"] = "Every 3 months"
            treatment_plan["monitoring_schedule"]["medical_follow_up"] = "Monthly"
            treatment_plan["risk_specific_interventions"].append("Intensive cognitive monitoring")
            treatment_plan["risk_specific_interventions"].append("Early intervention protocols")
        
        # Add specific interventions based on patient factors
        if patient_data.get("Depression") == 1:
            treatment_plan["medical_management"].append("Address depression with appropriate therapy/medication")
            treatment_plan["personalized_recommendations"].append("Consider antidepressant therapy")
        
        if patient_data.get("CardiovascularDisease") == 1:
            treatment_plan["medical_management"].append("Optimize cardiovascular health management")
            treatment_plan["personalized_recommendations"].append("Cardiovascular risk factor optimization")
        
        if patient_data.get("FamilyHistoryAlzheimers") == 1:
            treatment_plan["support_services"].append("Genetic counseling consideration")
            treatment_plan["personalized_recommendations"].append("Family education and support")
        
        # Add caregiver guidance
        treatment_plan["caregiver_guidance"] = [
            "Education about Alzheimer's disease progression",
            "Communication strategies for cognitive changes",
            "Safety planning and home modifications",
            "Respite care planning"
        ]
        
        return treatment_plan
    
    def is_predictor_available(self) -> bool:
        """Check if the Alzheimer's predictor is available"""
        return self.predictor is not None
    
    def get_prediction_confidence(self, patient_data: Dict[str, Any]) -> Optional[float]:
        """Get prediction confidence for given patient data"""
        if not self.is_predictor_available():
            return None
        
        try:
            prepared_data = self._prepare_patient_data(patient_data)
            prediction_result = self.predictor.predict_diagnosis(prepared_data)
            return max(prediction_result.get("probability_alzheimers", 0), 
                      prediction_result.get("probability_no_alzheimers", 0))
        except Exception:
            return None
    
    def _convert_to_chat_activities(self, treatment_items: list) -> list:
        """Convert treatment plan items into chat-executable activities"""
        chat_activities = []
        
        for item in treatment_items:
            if isinstance(item, str):
                # Convert treatment item to chat activity
                chat_activity = {
                    "id": f"activity_{len(chat_activities) + 1}",
                    "title": item,
                    "type": self._categorize_activity(item),
                    "chat_prompts": self._generate_chat_prompts(item),
                    "frequency": self._determine_frequency(item),
                    "difficulty": self._assess_difficulty(item),
                    "success_metrics": self._define_success_metrics(item),
                    "follow_up_questions": self._generate_follow_up_questions(item)
                }
                chat_activities.append(chat_activity)
        
        return chat_activities
    
    def _categorize_activity(self, item: str) -> str:
        """Categorize treatment item by type"""
        item_lower = item.lower()
        
        if any(word in item_lower for word in ["medication", "drug", "prescription", "medicine"]):
            return "medication"
        elif any(word in item_lower for word in ["exercise", "physical", "activity", "walk", "gym"]):
            return "physical_activity"
        elif any(word in item_lower for word in ["diet", "food", "nutrition", "meal", "eating"]):
            return "nutrition"
        elif any(word in item_lower for word in ["sleep", "rest", "bedtime"]):
            return "sleep"
        elif any(word in item_lower for word in ["memory", "cognitive", "brain", "mental"]):
            return "cognitive"
        elif any(word in item_lower for word in ["social", "family", "friend", "community"]):
            return "social"
        elif any(word in item_lower for word in ["doctor", "appointment", "medical", "clinic"]):
            return "medical"
        elif any(word in item_lower for word in ["safety", "emergency", "alert", "monitor"]):
            return "safety"
        else:
            return "general"
    
    def _generate_chat_prompts(self, item: str) -> list:
        """Generate chat prompts for executing the treatment item"""
        category = self._categorize_activity(item)
        
        prompts = {
            "medication": [
                f"Let's talk about {item}. Have you taken your medication today?",
                f"I want to help you with {item}. Can you tell me about your current medication routine?",
                f"Regarding {item}, are you experiencing any side effects or concerns?"
            ],
            "physical_activity": [
                f"Let's discuss {item}. How are you feeling about starting an exercise routine?",
                f"I'd like to help you with {item}. What physical activities do you enjoy?",
                f"About {item}, have you been able to stay active this week?"
            ],
            "nutrition": [
                f"Let's talk about {item}. How has your eating been lately?",
                f"I want to help you with {item}. What foods do you typically eat?",
                f"Regarding {item}, are you getting enough fruits and vegetables?"
            ],
            "sleep": [
                f"Let's discuss {item}. How has your sleep been recently?",
                f"I'd like to help you with {item}. What time do you usually go to bed?",
                f"About {item}, are you having any trouble falling asleep?"
            ],
            "cognitive": [
                f"Let's talk about {item}. How are you feeling mentally today?",
                f"I want to help you with {item}. Would you like to try a memory exercise?",
                f"Regarding {item}, have you noticed any changes in your thinking?"
            ],
            "social": [
                f"Let's discuss {item}. How are your relationships with family and friends?",
                f"I'd like to help you with {item}. Do you feel connected to others?",
                f"About {item}, have you been spending time with loved ones?"
            ],
            "medical": [
                f"Let's talk about {item}. Do you have any upcoming medical appointments?",
                f"I want to help you with {item}. Are you keeping track of your health?",
                f"Regarding {item}, have you spoken with your doctor recently?"
            ],
            "safety": [
                f"Let's discuss {item}. Do you feel safe at home?",
                f"I'd like to help you with {item}. Are there any safety concerns?",
                f"About {item}, do you have emergency contacts readily available?"
            ],
            "general": [
                f"Let's talk about {item}. How can I help you with this?",
                f"I want to support you with {item}. What would you like to know?",
                f"Regarding {item}, how are you feeling about this recommendation?"
            ]
        }
        
        return prompts.get(category, prompts["general"])
    
    def _determine_frequency(self, item: str) -> str:
        """Determine how often the activity should be discussed"""
        item_lower = item.lower()
        
        if any(word in item_lower for word in ["daily", "every day", "routine", "medication"]):
            return "daily"
        elif any(word in item_lower for word in ["weekly", "exercise", "appointment"]):
            return "weekly"
        elif any(word in item_lower for word in ["monthly", "review", "assessment"]):
            return "monthly"
        elif any(word in item_lower for word in ["urgent", "immediate", "emergency"]):
            return "as_needed"
        else:
            return "weekly"
    
    def _assess_difficulty(self, item: str) -> str:
        """Assess the difficulty level of the activity"""
        item_lower = item.lower()
        
        if any(word in item_lower for word in ["simple", "basic", "easy", "reminder"]):
            return "easy"
        elif any(word in item_lower for word in ["complex", "comprehensive", "detailed", "evaluation"]):
            return "hard"
        else:
            return "medium"
    
    def _define_success_metrics(self, item: str) -> list:
        """Define how to measure success for the activity"""
        category = self._categorize_activity(item)
        
        metrics = {
            "medication": ["Adherence rate", "Side effect monitoring", "Timing consistency"],
            "physical_activity": ["Activity duration", "Frequency", "Energy level"],
            "nutrition": ["Meal quality", "Hydration", "Weight stability"],
            "sleep": ["Sleep duration", "Sleep quality", "Bedtime consistency"],
            "cognitive": ["Memory performance", "Attention span", "Problem-solving"],
            "social": ["Social interactions", "Mood improvement", "Connection quality"],
            "medical": ["Appointment attendance", "Health monitoring", "Symptom tracking"],
            "safety": ["Safety incidents", "Emergency preparedness", "Risk awareness"],
            "general": ["Completion rate", "Patient satisfaction", "Goal achievement"]
        }
        
        return metrics.get(category, metrics["general"])
    
    def _generate_follow_up_questions(self, item: str) -> list:
        """Generate follow-up questions for the activity"""
        category = self._categorize_activity(item)
        
        questions = {
            "medication": [
                "How are you feeling after taking your medication?",
                "Are you experiencing any side effects?",
                "Do you need help remembering to take your medication?"
            ],
            "physical_activity": [
                "How did the exercise make you feel?",
                "What was the most challenging part?",
                "Would you like to try a different type of activity?"
            ],
            "nutrition": [
                "How did the meal taste?",
                "Are you feeling satisfied?",
                "Would you like suggestions for similar healthy meals?"
            ],
            "sleep": [
                "How did you sleep last night?",
                "Do you feel rested?",
                "Is there anything keeping you awake?"
            ],
            "cognitive": [
                "How did that exercise feel?",
                "Was it too easy or too difficult?",
                "Would you like to try something different?"
            ],
            "social": [
                "How did the interaction go?",
                "Do you feel more connected?",
                "Would you like to plan more social activities?"
            ],
            "medical": [
                "How did the appointment go?",
                "Do you have any questions about your health?",
                "Is there anything you'd like to discuss with your doctor?"
            ],
            "safety": [
                "Do you feel safe and secure?",
                "Are there any concerns you'd like to discuss?",
                "Do you need help with any safety measures?"
            ],
            "general": [
                "How are you feeling about this?",
                "Is there anything I can help you with?",
                "Would you like to discuss this further?"
            ]
        }
        
        return questions.get(category, questions["general"])
    
    def _generate_conversation_flows(self, treatment_plan: Dict[str, Any], risk_level: str) -> Dict[str, Any]:
        """Generate conversation flows for executing treatment plan"""
        
        flows = {
            "daily_check_in": {
                "purpose": "Daily wellness and treatment adherence check",
                "frequency": "daily",
                "duration": "5-10 minutes",
                "topics": [
                    "Mood and energy level",
                    "Medication adherence",
                    "Sleep quality",
                    "Physical activity",
                    "Safety concerns"
                ],
                "prompts": [
                    "Good morning! How are you feeling today?",
                    "Did you sleep well last night?",
                    "Have you taken your medications?",
                    "How is your energy level?",
                    "Is there anything you'd like to talk about?"
                ]
            },
            "treatment_progress": {
                "purpose": "Weekly treatment plan progress review",
                "frequency": "weekly",
                "duration": "15-20 minutes",
                "topics": [
                    "Treatment adherence",
                    "Symptom changes",
                    "Lifestyle modifications",
                    "Challenges and successes",
                    "Goal adjustments"
                ],
                "prompts": [
                    "Let's review how your week went with your treatment plan.",
                    "What went well this week?",
                    "What challenges did you face?",
                    "How are you feeling about your progress?",
                    "Would you like to adjust any of your goals?"
                ]
            },
            "crisis_support": {
                "purpose": "Emergency support and crisis intervention",
                "frequency": "as_needed",
                "duration": "variable",
                "topics": [
                    "Immediate safety concerns",
                    "Severe symptom changes",
                    "Emergency contacts",
                    "Caregiver notification",
                    "Medical intervention needs"
                ],
                "prompts": [
                    "I'm here to help. What's going on?",
                    "Are you safe right now?",
                    "Do you need to contact someone?",
                    "Would you like me to notify your caregiver?",
                    "Is this a medical emergency?"
                ]
            },
            "cognitive_engagement": {
                "purpose": "Cognitive stimulation and memory exercises",
                "frequency": "daily",
                "duration": "10-15 minutes",
                "topics": [
                    "Memory exercises",
                    "Orientation questions",
                    "Problem-solving activities",
                    "Reminiscence therapy",
                    "Attention training"
                ],
                "prompts": [
                    "Let's do a fun memory exercise together.",
                    "What day of the week is it today?",
                    "Can you tell me about a happy memory?",
                    "Let's work on a puzzle together.",
                    "How did you sleep last night?"
                ]
            }
        }
        
        # Customize flows based on risk level
        if risk_level == "High":
            flows["daily_check_in"]["frequency"] = "twice_daily"
            flows["crisis_support"]["frequency"] = "immediate"
            flows["cognitive_engagement"]["frequency"] = "twice_daily"
        elif risk_level == "Medium":
            flows["daily_check_in"]["frequency"] = "daily"
            flows["cognitive_engagement"]["frequency"] = "daily"
        else:
            flows["daily_check_in"]["frequency"] = "every_other_day"
            flows["cognitive_engagement"]["frequency"] = "every_other_day"
        
        return flows
    
    def _extract_treatment_goals(self, treatment_plan: Dict[str, Any]) -> list:
        """Extract and format treatment goals from the treatment plan"""
        goals = []
        
        # Extract goals from different sections
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
                            "target_date": "ongoing",
                            "success_criteria": self._define_success_metrics(item)
                        }
                        goals.append(goal)
        
        return goals
    
    def _simplify_for_cognitive_level(self, treatment_execution: Dict[str, Any], level: str) -> Dict[str, Any]:
        """Simplify treatment execution based on cognitive level"""
        simplified = treatment_execution.copy()
        
        if level == "severe":
            # Simplify all activities for severe cognitive impairment
            for category, activities in simplified.items():
                if isinstance(activities, list):
                    simplified[category] = [
                        {
                            **activity,
                            "title": f"Simple {activity['title']}",
                            "difficulty": "easy",
                            "frequency": "daily",
                            "chat_prompts": [
                                f"Let's do {activity['title']} together.",
                                f"I'll help you with {activity['title']}.",
                                f"Ready for {activity['title']}?"
                            ]
                        }
                        for activity in activities[:3]  # Limit to 3 activities per category
                    ]
        elif level == "mild":
            # Moderate simplification for mild cognitive impairment
            for category, activities in simplified.items():
                if isinstance(activities, list):
                    simplified[category] = [
                        {
                            **activity,
                            "difficulty": "easy" if activity.get("difficulty") == "hard" else activity.get("difficulty", "medium"),
                            "chat_prompts": [
                                prompt for prompt in activity.get("chat_prompts", [])[:2]  # Limit prompts
                            ]
                        }
                        for activity in activities[:5]  # Limit to 5 activities per category
                    ]
        
        return simplified
    
    def _generate_original_chatbot_config(self, patient_data: Dict[str, Any], 
                                        prediction_result: Dict[str, Any], 
                                        risk_level: str) -> Dict[str, Any]:
        """Generate original chatbot configuration without LLM enhancement"""
        
        # Base configuration (original version)
        config = {
            "personality": "Supportive, patient, and encouraging",
            "communication_style": "Simple, clear language with repetition for important information",
            "daily_activities": [
                "Morning routine reminders",
                "Medication reminders",
                "Meal planning assistance",
                "Exercise encouragement",
                "Memory games and cognitive exercises"
            ],
            "safety_features": [
                "Emergency contact integration",
                "Location tracking for disorientation episodes",
                "Medication adherence monitoring",
                "Fall risk assessment"
            ],
            "personalization": {
                "adapt_to_cognitive_level": True,
                "use_visual_cues": True,
                "provide_positive_reinforcement": True,
                "maintain_routine_consistency": True
            }
        }
        
        # Customize based on cognitive level
        mmse_score = patient_data.get("MMSE", 30)
        if mmse_score < 18:
            config["communication_style"] = "Very simple language, frequent repetition, visual cues essential"
            config["daily_activities"].extend([
                "Basic orientation questions",
                "Simple memory exercises",
                "Daily routine reinforcement"
            ])
        elif mmse_score < 24:
            config["communication_style"] = "Simple language with occasional repetition"
            config["daily_activities"].extend([
                "Moderate cognitive exercises",
                "Social interaction prompts",
                "Hobby and interest reminders"
            ])
        
        # Add risk-specific features
        if risk_level == "High":
            config["safety_features"].extend([
                "24/7 monitoring alerts",
                "Caregiver notification system",
                "Emergency response integration"
            ])
            config["personalization"]["frequent_check_ins"] = True
        
        return config


# Global instance for easy access
# Initialize without LLM API key by default - can be configured later
diagnosis_planner = DiagnosisTreatmentPlanner()

def configure_llm(api_key: str, provider: str = "openai"):
    """Configure LLM for the global diagnosis planner instance"""
    global diagnosis_planner
    diagnosis_planner.llm_api_key = api_key
    diagnosis_planner.llm_provider = provider
    print(f"✓ LLM configured with provider: {provider}")

# ---------- FastAPI Router for Analysis Endpoints ----------
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# ---------- Request/Response Models ----------
class DirectAnalysisRequest(BaseModel):
    patient_data: Dict[str, Any]  # Raw patient data for analysis

class DirectAnalysisResponse(BaseModel):
    patient_portfolio: Dict[str, Any]
    diagnosis_analysis: Dict[str, Any]
    treatment_plan: Dict[str, Any]
    companion_chatbot_config: Dict[str, Any]
    analysis_timestamp: str
    analysis_method: str
    alzheimers_prediction: Dict[str, Any]

# ---------- Analysis Endpoints ----------
@router.post("/direct", response_model=DirectAnalysisResponse)
def direct_analysis_using_planner(req: DirectAnalysisRequest):
    """
    Direct analysis endpoint using DiagnosisTreatmentPlanner
    Returns patient portfolio, diagnosis analysis, and treatment plan
    """
    
    if not diagnosis_planner.is_predictor_available():
        raise HTTPException(
            status_code=503, 
            detail="Alzheimer's predictor model not available. Please ensure model files are properly loaded."
        )
    
    try:
        # Use the diagnosis planner to analyze patient data directly
        analysis_result = diagnosis_planner.analyze_intake_data(req.patient_data)
        
        return DirectAnalysisResponse(
            patient_portfolio=analysis_result["patient_portfolio"],
            diagnosis_analysis=analysis_result["diagnosis_analysis"],
            treatment_plan=analysis_result["treatment_plan"],
            companion_chatbot_config=analysis_result["companion_chatbot_config"],
            analysis_timestamp=analysis_result["analysis_timestamp"],
            analysis_method=analysis_result["analysis_method"],
            alzheimers_prediction=analysis_result["alzheimers_prediction"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in direct analysis: {str(e)}"
        )

@router.get("/health")
def analysis_health_check():
    """Health check for analysis module"""
    return {
        "status": "healthy",
        "alzheimers_predictor": "available" if diagnosis_planner.is_predictor_available() else "not_available",
        "llm_configured": diagnosis_planner.llm_api_key is not None,
        "llm_provider": diagnosis_planner.llm_provider if diagnosis_planner.llm_api_key else None
    }
