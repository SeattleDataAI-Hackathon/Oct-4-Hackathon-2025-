import pandas as pd
import os
from openai import OpenAI
try:
    from config import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = None
    print("Warning: config.py not found. Please create it with your API key.")

class CarePath:
    def __init__(self, csv_path, api_key=None):
        """Initialize CarePath with disorder dataset"""
        self.df = pd.read_csv(csv_path)
        self.api_key = api_key or OPENAI_API_KEY or os.getenv('OPENAI_API_KEY')

        if not self.api_key or self.api_key == "paste-your-api-key-here":
            raise ValueError("Please set your OpenAI API key in config.py")

        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []
        self.collected_info = {
            'symptoms': [],
            'age_group': None,
            'gender': None,
            'lifestyle_factors': []
        }

    def get_system_prompt(self):
        """System prompt for the LLM"""
        return f"""You are CarePath, a medical triage assistant that helps diagnose health conditions.

Your role:
1. Have a natural conversation to understand the patient's symptoms
2. Ask follow-up questions to gather more details
3. Ask about age, gender, and lifestyle factors when relevant
4. Be empathetic and professional

Available disorders in database: {len(self.df)} conditions

Keep responses concise and focused. Ask one or two questions at a time.
When you have enough information, say "DIAGNOSIS_READY" to trigger the matching process.
"""

    def start_conversation(self):
        """Start the initial conversation"""
        initial_message = "Hello! I'm CarePath, your medical guidance assistant. I'm here to help understand your symptoms and guide you to the right care.\n\nWhat brings you here today? Please describe any symptoms you're experiencing."
        print(f"\nCarePath: {initial_message}\n")
        self.conversation_history.append({
            "role": "assistant",
            "content": initial_message
        })
        return initial_message

    def chat(self, user_message):
        """Process user message and get AI response"""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.get_system_prompt()}
            ] + self.conversation_history,
            temperature=0.7,
            max_tokens=300
        )

        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def extract_symptoms_from_conversation(self):
        """Use LLM to extract symptoms from conversation history"""
        extraction_prompt = f"""Based on this conversation, extract:
1. All mentioned symptoms (as a comma-separated list)
2. Age group (Children/Adolescents/Adults 20-40/Adults 40+/Elderly)
3. Gender (Male/Female/Equal)
4. Lifestyle factors mentioned (Stress/Obesity/Smoking/Alcohol/Sedentary lifestyle/Trauma history)

Conversation:
{self._format_conversation()}

Return in this exact format:
SYMPTOMS: symptom1, symptom2, symptom3
AGE_GROUP: age group
GENDER: gender
LIFESTYLE: factor1, factor2
"""

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3,
            max_tokens=200
        )

        return self._parse_extraction(response.choices[0].message.content)

    def _format_conversation(self):
        """Format conversation history for extraction"""
        conv_text = ""
        for msg in self.conversation_history:
            if msg['role'] == 'user':
                conv_text += f"Patient: {msg['content']}\n"
            elif msg['role'] == 'assistant' and 'CarePath' not in msg['content'][:20]:
                conv_text += f"Assistant: {msg['content']}\n"
        return conv_text

    def _parse_extraction(self, extraction_text):
        """Parse extracted information"""
        lines = extraction_text.strip().split('\n')
        info = {}

        for line in lines:
            if line.startswith('SYMPTOMS:'):
                info['symptoms'] = [s.strip().lower() for s in line.replace('SYMPTOMS:', '').split(',')]
            elif line.startswith('AGE_GROUP:'):
                info['age_group'] = line.replace('AGE_GROUP:', '').strip()
            elif line.startswith('GENDER:'):
                info['gender'] = line.replace('GENDER:', '').strip()
            elif line.startswith('LIFESTYLE:'):
                info['lifestyle'] = [s.strip() for s in line.replace('LIFESTYLE:', '').split(',') if s.strip()]

        return info

    def match_symptoms(self, patient_info):
        """Match symptoms against disorder database"""
        matches = []

        patient_symptoms = set(patient_info.get('symptoms', []))

        for idx, row in self.df.iterrows():
            disorder_symptoms = set([s.strip().lower() for s in row['Common_Symptoms'].split(',')])

            # Calculate symptom overlap
            overlap = patient_symptoms.intersection(disorder_symptoms)
            match_score = len(overlap) / len(disorder_symptoms) if len(disorder_symptoms) > 0 else 0

            # Partial matching for flexibility
            partial_matches = sum(
                1 for ps in patient_symptoms
                for ds in disorder_symptoms
                if ps in ds or ds in ps
            )

            if match_score > 0 or partial_matches > 0:
                matches.append({
                    'disorder_id': row['Disorder_ID'],
                    'disorder_name': row['Disorder_Name'],
                    'category': row['Category'],
                    'match_score': match_score,
                    'partial_matches': partial_matches,
                    'symptoms': row['Common_Symptoms'],
                    'specialist': row['Recommended_Specialist'],
                    'emergency': row['Emergency_Flag'],
                    'followup_questions': row['Suggested_Followup_Questions']
                })

        # Sort by match score and partial matches
        matches.sort(key=lambda x: (x['match_score'], x['partial_matches']), reverse=True)

        return matches[:5]  # Return top 5 matches

    def generate_recommendation(self, matches):
        """Generate doctor recommendation based on matches"""
        if not matches:
            return {
                'diagnosis': 'Unable to determine',
                'recommended_action': 'Please consult a General Practitioner for evaluation',
                'specialist': 'General Practitioner',
                'emergency': False
            }

        top_match = matches[0]

        # Determine urgency level
        if top_match['emergency'] == 'Yes':
            recommended_action = 'EMERGENCY: Seek immediate medical attention at the nearest emergency room'
            urgency = 'Emergency'
        elif top_match['match_score'] > 0.5:
            recommended_action = f"Urgent Care: Schedule an appointment with a {top_match['specialist']} soon"
            urgency = 'Urgent Care'
        else:
            recommended_action = f"Normal: Consider consulting a {top_match['specialist']} for evaluation"
            urgency = 'Normal'

        return {
            'possible_condition': top_match['disorder_name'],
            'category': top_match['category'],
            'confidence': f"{top_match['match_score']*100:.1f}%",
            'recommended_specialist': top_match['specialist'],
            'urgency_level': urgency,
            'action': recommended_action,
            'emergency': top_match['emergency'] == 'Yes',
            'other_possibilities': [m['disorder_name'] for m in matches[1:3]] if len(matches) > 1 else []
        }

    def run(self):
        """Main conversation loop"""
        print("="*60)
        print("  CAREPATH - Your Medical Guidance Assistant")
        print("="*60)

        self.start_conversation()

        conversation_count = 0
        max_turns = 10

        while conversation_count < max_turns:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\nCarePath: Take care! If symptoms worsen, please seek medical attention.")
                break

            # Get AI response
            response = self.chat(user_input)
            print(f"\nCarePath: {response}\n")

            conversation_count += 1

            # Check if ready for diagnosis (after 3-4 exchanges)
            if conversation_count >= 3:
                # Ask if ready to diagnose
                ready = input("\n[Ready for diagnosis? (yes/no)]: ").strip().lower()
                if ready == 'yes':
                    print("\nAnalyzing your symptoms...\n")

                    # Extract info and match
                    patient_info = self.extract_symptoms_from_conversation()
                    matches = self.match_symptoms(patient_info)
                    recommendation = self.generate_recommendation(matches)

                    # Display results
                    print("="*60)
                    print("  ASSESSMENT RESULTS")
                    print("="*60)
                    print(f"Possible Condition: {recommendation['possible_condition']}")
                    print(f"Category: {recommendation['category']}")
                    print(f"Confidence: {recommendation['confidence']}")
                    print(f"\nRecommended Specialist: {recommendation['recommended_specialist']}")
                    print(f"Urgency Level: {recommendation['urgency_level']}")
                    print(f"\n{recommendation['action']}")

                    if recommendation['other_possibilities']:
                        print(f"\nOther possibilities: {', '.join(recommendation['other_possibilities'])}")

                    print("\n" + "="*60)
                    print("DISCLAIMER: This is not a medical diagnosis. Please consult")
                    print("a healthcare professional for proper evaluation.")
                    print("="*60)
                    break

        if conversation_count >= max_turns:
            print("\nCarePath: I recommend speaking with a healthcare professional for a proper evaluation.")


if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, "common_disorders_dataset_full.csv")

    # Initialize CarePath
    carepath = CarePath(csv_path=csv_path)

    # Run the application
    carepath.run()
