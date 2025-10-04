# Please add an authentication token to the request header to get the response.

# Please compare token provided by the user with the token provided by the system (system token: 111-1111-11111).

# if token is not correct give forbidden error.




from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from flask_restx import Api, Resource, fields
import json
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
import os
import logging
from colorama import Fore, Style, init

# Load environment variables from .env file
load_dotenv()
import re
from langchain_community.vectorstores import FAISS
import json
import markdown
import numpy as np
from datetime import datetime, timedelta
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from faiss_lib_mistral import load_file, json_to_documents, csv_to_documents, split_documents, get_mistral_api_key, store_embeddings_in_faiss, get_formatted_response


# Initialize Colorama for colored logging
init(autoreset=True)

# Set up logging
logging.basicConfig(filename='myapp.log', level=logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)


# Create API instance for Swagger documentation
api = Api(
    app,
    version="1.0",
    title="BeyondBabyBlues RAG API",
    description="REST API for Retrieval-Augmented Generation (RAG) Powered Searchable Database for BeyondBabyBlues to answer the questions raised by users in the ChatBot.",
    doc="/swagger",  # Swagger UI URL endpoint
    defaultModelsExpandDepth=1,  # Expand default namespace
    defaultModelExpandDepth=1    # Expand model definitions
)

# Enable CORS for all domains on all routes
CORS(app)

# Add simple health check endpoint
@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "BeyondBabyBlues Server is running!",
        "agent_ready": agent_executor is not None,
        "version": "1.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "agent_initialized": agent_executor is not None,
        "timestamp": datetime.now().isoformat()
    })

# Google Calendar API Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'  # OAuth2 credentials file
TOKEN_FILE = 'token.pickle'  # Refresh token storage

# Global variables for agent and vector store
agent_executor = None
vector_store = None

def authenticate_google_calendar():
    """Authenticate with Google Calendar API using OAuth2"""
    creds = None
    # Load existing token
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, get them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print(f"{Fore.GREEN}✅ Refreshed existing credentials")
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️ Failed to refresh credentials: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"{Fore.RED}❌ Error: {CREDENTIALS_FILE} not found. Please download it from Google Cloud Console.")
                return None
            
            try:
                # Check if it's a web application or desktop application credentials
                with open(CREDENTIALS_FILE, 'r') as f:
                    cred_data = json.load(f)
                
                if 'web' in cred_data:
                    # Web application credentials - use manual flow
                    print(f"{Fore.CYAN}🌐 [OAUTH] Detected web application credentials")
                    oauth_port = 8000
                    redirect_uri = f"http://localhost:{oauth_port}"
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_FILE, 
                        SCOPES,
                        redirect_uri=redirect_uri
                    )
                    creds = flow.run_local_server(
                        port=oauth_port, 
                        open_browser=True,
                        authorization_prompt_message=f"Please visit this URL to authorize the application:\n{{url}}\n",
                        success_message="Authentication successful! You can close this browser tab."
                    )
                elif 'installed' in cred_data:
                    # Desktop application credentials - use standard flow
                    print(f"{Fore.CYAN}�️ [OAUTH] Detected desktop application credentials")
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=8000, open_browser=True)
                else:
                    print(f"{Fore.RED}❌ Invalid credentials format")
                    return None
                
                print(f"{Fore.GREEN}✅ Successfully authenticated with Google Calendar")
                
            except Exception as e:
                print(f"{Fore.RED}❌ Authentication failed: {e}")
                print(f"{Fore.YELLOW}💡 Error details:")
                print(f"{Fore.YELLOW}   - Make sure http://localhost:8000 is in your Google Console redirect URIs")
                print(f"{Fore.YELLOW}   - For web app: Make sure it's configured as 'Web application' with correct redirect URIs")
                print(f"{Fore.YELLOW}   - For desktop app: Download 'Desktop application' credentials instead")
                import traceback
                print(f"{Fore.RED}   - Full error: {traceback.format_exc()}")
                return None
        
        # Save the credentials for the next run
        try:
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print(f"{Fore.GREEN}✅ Credentials saved for future use")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Failed to save credentials: {e}")
    
    return creds

def create_calendar_appointment(summary, start_time, end_time, attendee_email, description="", specialist_email=""):
    """Create an appointment in Google Calendar"""
    try:
        print(f"{Fore.CYAN}📅 [CALENDAR] Starting appointment creation...")
        print(f"{Fore.CYAN}📋 [CALENDAR] Summary: {summary}")
        print(f"{Fore.CYAN}🕒 [CALENDAR] Start: {start_time}")
        print(f"{Fore.CYAN}🕒 [CALENDAR] End: {end_time}")
        print(f"{Fore.CYAN}📧 [CALENDAR] Attendee: {attendee_email}")
        
        creds = authenticate_google_calendar()
        if not creds:
            error_msg = "Failed to authenticate with Google Calendar"
            print(f"{Fore.RED}❌ [CALENDAR] {error_msg}")
            return {"error": error_msg}
        
        print(f"{Fore.GREEN}✅ [CALENDAR] Authentication successful")
        
        service = build('calendar', 'v3', credentials=creds)
        print(f"{Fore.GREEN}✅ [CALENDAR] Calendar service built")
        
        # Create event
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Los_Angeles',
            },
            'attendees': [
                {'email': attendee_email},
            ],
        }
        
        if specialist_email:
            event['attendees'].append({'email': specialist_email})
            print(f"{Fore.CYAN}👥 [CALENDAR] Added specialist: {specialist_email}")
        
        print(f"{Fore.YELLOW}🔄 [CALENDAR] Creating event in Google Calendar...")
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        result = {
            "success": True,
            "event_id": created_event.get('id'),
            "event_link": created_event.get('htmlLink'),
            "message": f"Appointment scheduled successfully: {summary}"
        }
        
        print(f"{Fore.GREEN}✅ [CALENDAR] Event created successfully!")
        print(f"{Fore.GREEN}🎫 [CALENDAR] Event ID: {result['event_id']}")
        print(f"{Fore.GREEN}🔗 [CALENDAR] Event Link: {result['event_link']}")
        
        return result
        
    except HttpError as error:
        error_msg = f"Google Calendar API error: {error}"
        print(f"{Fore.RED}❌ [CALENDAR] {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Failed to create appointment: {str(e)}"
        print(f"{Fore.RED}❌ [CALENDAR] {error_msg}")
        import traceback
        print(f"{Fore.RED}📋 [CALENDAR] Full traceback: {traceback.format_exc()}")
        return {"error": error_msg}

def search_knowledge_base(query):
    """Search the knowledge base using vector similarity"""
    print(f"🔍 [TOOL CALL] search_knowledge_base called with query: '{query}'")
    global vector_store
    if not vector_store:
        print("❌ [TOOL ERROR] Knowledge base not available")
        return "Knowledge base not available"
    
    try:
        # Perform similarity search
        docs = vector_store.similarity_search(query, k=3)
        print(f"📚 [TOOL RESULT] Found {len(docs)} relevant documents")
        
        # Combine relevant documents
        context = "\n\n".join([doc.page_content for doc in docs])
        print(f"✅ [TOOL SUCCESS] search_knowledge_base returning {len(context)} characters")
        return context
    except Exception as e:
        print(f"❌ [TOOL ERROR] search_knowledge_base failed: {str(e)}")
        return f"Error searching knowledge base: {str(e)}"

def book_appointment_tool(appointment_details):
    """Tool for booking appointments with specialists"""
    print(f"📅 [TOOL CALL] book_appointment_tool called with details: '{appointment_details}'")
    try:
        # Parse appointment details (expected format: "specialist_name|date|time|patient_email|patient_name")
        parts = appointment_details.split("|")
        print(f"📋 [TOOL PARSING] Split into {len(parts)} parts: {parts}")
        if len(parts) < 5:
            print("❌ [TOOL ERROR] Insufficient appointment details provided")
            return "Error: Please provide appointment details in format: specialist_name|date|time|patient_email|patient_name"
        
        specialist_name, date, time, patient_email, patient_name = parts[:5]
        
        # Get specialist email mapping
        specialist_emails = {
            "Dr. Rachel Chen": "dr.chen@BeyondBabyBlues.com",
            "Dr. Priya Sharma": "dr.sharma@BeyondBabyBlues.com", 
            "Dr. Michael Rodriguez": "dr.rodriguez@BeyondBabyBlues.com",
            "Dr. Jennifer Thompson": "dr.thompson@BeyondBabyBlues.com",
            "Dr. Amanda Foster": "amanda.foster@BeyondBabyBlues.com",
            "Sarah Mitchell": "sarah.mitchell@BeyondBabyBlues.com",
            "Dr. Robert Kim": "dr.kim@BeyondBabyBlues.com",
            "Dr. Lisa Park": "crisis@BeyondBabyBlues.com"
        }
        
        specialist_email = specialist_emails.get(specialist_name, "specialist@BeyondBabyBlues.com")
        
        # Create datetime objects
        start_datetime = f"{date}T{time}:00"
        end_time = datetime.fromisoformat(start_datetime) + timedelta(hours=1)
        end_datetime = end_time.isoformat()
        
        # Create appointment
        print(f"📅 [CALENDAR] Creating appointment: {specialist_name} on {date} at {time}")
        result = create_calendar_appointment(
            summary=f"Consultation with {specialist_name} - {patient_name}",
            start_time=start_datetime,
            end_time=end_datetime,
            attendee_email=patient_email,
            description=f"Postpartum mental health consultation for {patient_name}",
            specialist_email=specialist_email
        )
        
        print(f"📅 [CALENDAR] Appointment result: {result}")
        
        if result.get("success"):
            success_msg = f"✅ Appointment booked successfully!\n📅 {specialist_name} consultation scheduled\n🔗 Event link: {result.get('event_link', 'N/A')}\n📧 Calendar invites sent to {patient_email} and {specialist_email}"
            print(f"✅ [TOOL SUCCESS] book_appointment_tool completed successfully")
            return success_msg
        else:
            error_msg = f"❌ Failed to book appointment: {result.get('error', 'Unknown error')}"
            print(f"❌ [TOOL ERROR] book_appointment_tool failed: {result.get('error', 'Unknown error')}")
            return error_msg
            
    except Exception as e:
        print(f"❌ [TOOL ERROR] book_appointment_tool exception: {str(e)}")
        return f"Error booking appointment: {str(e)}"

def get_available_specialists():
    """Get list of available specialists"""
    print("👥 [TOOL CALL] get_available_specialists called")
    specialists = {
        "Dr. Rachel Chen": "Depression & Anxiety Specialist - Available Mon-Fri 9 AM-6 PM",
        "Dr. Priya Sharma": "Medications & Bipolar Specialist - Available Tue-Sat 8 AM-5 PM",
        "Dr. Michael Rodriguez": "Trauma & PTSD Specialist - Available Mon-Thu 10 AM-7 PM", 
        "Dr. Jennifer Thompson": "High-Risk Pregnancy Specialist - Available Mon-Fri 7 AM-4 PM",
        "Dr. Amanda Foster": "Family Therapy Specialist - Various availability",
        "Sarah Mitchell": "Anxiety & OCD Therapy Specialist - Various availability",
        "Dr. Robert Kim": "Psychological Testing Specialist - Various availability",
        "Dr. Lisa Park": "Crisis Emergency Specialist - Available 24/7"
    }
    
    result = "Available Specialists:\n"
    for name, details in specialists.items():
        result += f"• {name}: {details}\n"
    
    print(f"✅ [TOOL SUCCESS] get_available_specialists returning {len(specialists)} specialists")
    return result

# Define models for Swagger documentation
query_model = api.model('Query', {
    'query': fields.String(required=True, description="User's query from the chatbot.", example="Who is CTO of BeyondBabyBlues?")
})

# Define the response model
response_model = api.model('Response', {
    'content': fields.String(required=True, description='Detailed response content', example=""),
    'role': fields.String(required=True, description='Role of the responder', example="assistant")
})

# System token for authentication
SYSTEM_TOKEN = "111-1111-11111"

# API Endpoint
@api.route('/query')
class QueryEndpoint(Resource):
    @api.expect(query_model)
    @api.doc(description="Executes a query using Retrieval-Augmented Generation (RAG) for BeyondBabyBlues Data to provide accurate answers to user questions based on the organization's knowledge base.")
    def post(self):
        try:
            print(Fore.CYAN + "🌐 [API] POST request received on /query endpoint")
            logging.info(Fore.CYAN + "##[section] Received a request from Chatbot App...")
            
            # Parse request data
            try:
                data = request.json
                question = data.get('query', '') if data else ''
                print(Fore.CYAN + f"🌐 [API] Parsed question: '{question}'")
            except Exception as parse_error:
                print(Fore.RED + f"❌ [API ERROR] Failed to parse request: {parse_error}")
                return jsonify({"error": "Invalid JSON data"}), 400

            logging.info(Fore.YELLOW + f"##[debug] User query: {question}")
            
            '''
            # Get the token from request headers
            auth_token = request.headers.get('Authorization')

            # Check if token matches the system token
            if auth_token != SYSTEM_TOKEN:
                logging.error(Fore.RED + "##[error] Invalid token provided.")
                return jsonify({"error": "Forbidden: Invalid token"}), 403

            '''
            global agent_executor
            if not agent_executor:
                return jsonify({"error": "Agent not initialized. Please restart the server."}), 500

            # Execute the query using the ReAct agent
            try:
                print(Fore.CYAN + f"🤖 [AGENT] Executing query: '{question}'")
                results = agent_executor.invoke({"input": question})
                raw_response = results.get("output", "")
                
                # Parse and clean the response to remove ReAct reasoning steps
                response_content = parse_agent_response(raw_response)
                
                print(Fore.CYAN + f"🤖 [AGENT] Raw Results: {results}\n")
                print(Fore.GREEN + f"🤖 [AGENT] Cleaned Response: {response_content}\n")
                
                # Log intermediate steps for debugging
                if "intermediate_steps" in results:
                    print(Fore.YELLOW + f"🔧 [AGENT DEBUG] Intermediate steps: {len(results['intermediate_steps'])} steps")
                    for i, step in enumerate(results["intermediate_steps"]):
                        action, observation = step
                        print(Fore.YELLOW + f"  Step {i+1}: Action={action.tool}, Input='{action.tool_input}', Output='{observation[:100]}...'")
                else:
                    print(Fore.YELLOW + "🔧 [AGENT DEBUG] No intermediate steps found")
                
                # For sources, we'll extract from the agent's intermediate steps if available
                sources = []
                if "intermediate_steps" in results:
                    sources = [step[1] for step in results["intermediate_steps"] if isinstance(step[1], str)]
                
                # Analyze response for consultation needs
                consultation_info = analyze_consultation_need(response_content)
                
            except Exception as agent_error:
                print(Fore.RED + f"❌ [AGENT ERROR] Agent execution failed: {agent_error}")
                print(Fore.RED + f"❌ [AGENT ERROR] Error type: {type(agent_error)}")
                import traceback
                print(Fore.RED + f"❌ [AGENT ERROR] Full traceback: {traceback.format_exc()}")
                
                # Check for specific Mistral API errors
                error_str = str(agent_error).lower()
                if "429" in error_str or "service_tier_capacity_exceeded" in error_str or "quota" in error_str:
                    response_content = """🚨 Service Temporarily Unavailable

Mistral AI API Quota Exceeded - We're currently experiencing high demand and have reached our API usage limits.

What you can do:
• Please try again in a few minutes
• For urgent medical questions, please contact our support team directly
• Consider scheduling an appointment through our booking system

Note: Appointment booking is still available even when this happens.

We apologize for the inconvenience and are working to resolve this issue."""
                elif "rate_limit" in error_str or "too_many_requests" in error_str:
                    response_content = """⏱️ Rate Limit Reached

Too many requests in a short time period. Please wait a moment and try again."""
                elif "api" in error_str and ("key" in error_str or "auth" in error_str):
                    response_content = """🔑 Authentication Issue

There's an issue with our API authentication. Please contact our technical support team."""
                else:
                    response_content = """⚠️ Technical Difficulties

I apologize, but I'm experiencing technical difficulties. Please try again in a few moments, or contact our support team if the issue persists.

Appointment booking is still available if you need to schedule a consultation."""
                sources = []
                consultation_info = {"needed": False, "type": "general", "specialist": "general"}
                
                # Try to provide basic information from knowledge base if possible
                if "429" in error_str or "service_tier_capacity_exceeded" in error_str:
                    try:
                        print(Fore.YELLOW + f"🔄 [FALLBACK] Attempting basic knowledge search for: '{question}'")
                        basic_info = search_knowledge_base(question)
                        if basic_info and len(basic_info.strip()) > 50:  # Only if we get meaningful content
                            response_content += f"""

📚 Basic Information Available:

{basic_info[:500]}{'...' if len(basic_info) > 500 else ''}

Note: This is basic information from our knowledge base. For detailed consultation, please try again later or book an appointment."""
                            sources = ["BeyondBabyBlues Knowledge Base"]
                            print(Fore.GREEN + f"✅ [FALLBACK] Added basic knowledge info")
                    except Exception as fallback_error:
                        print(Fore.YELLOW + f"⚠️ [FALLBACK] Basic search also failed: {fallback_error}")
            
            print(Fore.GREEN + "##[debug]RAG completed successfully!")
            # Return the formatted result as JSON, including sources and consultation info
            return jsonify({
                    "role": "assistant",
                    "content": md_to_html(response_content),
                    "sources": sources,
                    "consultation_needed": consultation_info["needed"],
                    "consultation_type": consultation_info["type"],
                    "recommended_specialist": consultation_info["specialist"]
                })

        except Exception as e:
            print(Fore.RED + f"❌ [API ERROR] Critical error in API endpoint: {e}")
            print(Fore.RED + f"❌ [API ERROR] Error type: {type(e)}")
            import traceback
            print(Fore.RED + f"❌ [API ERROR] Full traceback: {traceback.format_exc()}")
            logging.error(Fore.RED + f"##[error] Error processing query: {e}")
            return jsonify({"error": f"Internal server error: {str(e)}"}), 500

def get_chat_context(question):
    # Define a more concise and professional prompt template
    template = f"""
            You are a compassionate support assistant for BeyondBabyBlues, a pregnancy help organization specializing in mental health and emotional well-being support for expectant mothers.
            Your primary role is to provide empathetic, clear, and accurate guidance for pregnant women experiencing mental health challenges, distress, or emotional difficulties.
    
            Core Responsibilities:
            - Provide supportive, non-judgmental responses to mental health concerns during pregnancy
            - Recognize signs of prenatal depression, anxiety, mood disorders, and emotional distress
            - Offer practical coping strategies and emotional support resources
            - Connect women with appropriate professional mental health services
            - Validate feelings and normalize the emotional challenges of pregnancy
            - Maintain human oversight for complex situations requiring professional judgment
    
            Mental Health Support Guidelines:
            - Always acknowledge and validate emotional struggles - pregnancy can be overwhelming
            - Recognize symptoms of prenatal depression: persistent sadness, anxiety, mood swings, sleep issues, loss of interest
            - Identify anxiety disorders: excessive worry, panic attacks, fear about pregnancy/childbirth, social withdrawal
            - Watch for signs of severe distress: thoughts of self-harm, inability to function, severe mood changes
            - Provide immediate crisis intervention guidance when needed
            - Emphasize that seeking mental health support is a sign of strength, not weakness
    
            Human-in-the-Loop Guidelines & Specialist Referrals:
            - For complex mental health situations, always recommend human consultation: "I'd like to connect you with our human specialist for personalized guidance"
            - When uncertain about advice or treatment recommendations: "Let me have our mental health professional review this situation and get back to you"
            - For medication-related questions: "This requires professional medical evaluation - I'll connect you with our healthcare team"
            - For crisis situations: "I'm immediately connecting you with our crisis specialist" + provide crisis contact info
            - For personalized treatment plans: "Our licensed therapist will work with you to create a personalized plan"
            - When legal or ethical concerns arise: "I need to involve our supervisor to ensure we provide the best support"
            - For cases requiring specialized expertise: "Let me connect you with our specialist who has experience with this specific situation"
            
            Available Specialist Doctors for Human Consultation:
            - **Dr. Rachel Chen, MD, PhD** - Perinatal Mental Health Specialist (Postpartum Depression, Anxiety): dr.chen@BeyondBabyBlues.com | (123) 456-7891
            - **Dr. Priya Sharma, MD** - Reproductive Psychiatrist (Postpartum Psychosis, Bipolar, Medications): dr.sharma@BeyondBabyBlues.com | (123) 456-7892
            - **Dr. Michael Rodriguez, MD** - Trauma Specialist (Birth Trauma, PTSD): dr.rodriguez@BeyondBabyBlues.com | (123) 456-7893
            - **Dr. Jennifer Thompson, MD** - High-Risk Pregnancy Specialist: dr.thompson@BeyondBabyBlues.com | (123) 456-7894
            - **Dr. Amanda Foster, LCSW** - Clinical Social Worker (Support Groups, Family Therapy): amanda.foster@BeyondBabyBlues.com | (123) 456-7895
            - **Sarah Mitchell, LPC** - Licensed Counselor (Anxiety, Postpartum OCD, CBT): sarah.mitchell@BeyondBabyBlues.com | (123) 456-7896
            - **Dr. Robert Kim, PhD** - Clinical Psychologist (Testing, Severe Disorders): dr.kim@BeyondBabyBlues.com | (123) 456-7897
            - **Dr. Lisa Park, MD** - Crisis Psychiatrist (24/7 Emergency): crisis@BeyondBabyBlues.com | (123) 456-7999
            
            Specialist Matching Guidelines:
            - Depression/Mood Disorders → Recommend Dr. Rachel Chen or Dr. Priya Sharma
            - Anxiety/Panic Attacks → Recommend Dr. Rachel Chen or Sarah Mitchell
            - Trauma/PTSD → Recommend Dr. Michael Rodriguez
            - Medication Questions → Recommend Dr. Priya Sharma or Dr. Jennifer Thompson
            - High-Risk Pregnancy → Recommend Dr. Jennifer Thompson
            - Family/Relationship Issues → Recommend Dr. Amanda Foster
            - Crisis/Suicidal Thoughts → Immediately recommend Dr. Lisa Park
            - Psychological Testing → Recommend Dr. Robert Kim
    
            Human Escalation Triggers:
            - Suicidal ideation or self-harm thoughts
            - Severe depression with inability to function
            - Domestic violence or abuse situations
            - Substance abuse during pregnancy
            - Complex trauma or PTSD symptoms
            - Medication management questions
            - Legal concerns or mandatory reporting situations
            - Requests for specific medical advice or diagnosis
    
            Important Safety & Support Notes:
            - If you don't know the answer, simply state that you don't know, and always offer human consultation
            - For immediate mental health crisis or suicidal thoughts: "I'm immediately connecting you with our crisis team. Please also contact 988 (Suicide & Crisis Lifeline) or 911"
            - For severe depression/anxiety symptoms: "This sounds really difficult. I'm arranging for our mental health specialist to contact you immediately at counseling@BeyondBabyBlues.com"
            - Always encourage professional human support alongside AI assistance
            - Obey HIPAA regulations and maintain strict patient confidentiality at all times
            - Ask for basic details (name, pregnancy stage) only when necessary for personalized support
            - Document when human intervention is needed for follow-up
    
            Contact Information for Support:
            - Mental Health Crisis: 988 (Suicide & Crisis Lifeline) or 911
            - Crisis Psychiatrist: Dr. Lisa Park at crisis@BeyondBabyBlues.com | (123) 456-7999
            - General Specialist Consultation: specialist@BeyondBabyBlues.com
            - EMR Support (Health Records): emr-support@BeyondBabyBlues.com
            - Patient Portal: portal.BeyondBabyBlues.com
            - Privacy Officer: privacy@BeyondBabyBlues.com
            - General Information: info@BeyondBabyBlues.com
            
            HIPAA-Compliant EMR Process:
            - All specialist consultations include secure, encrypted transfer of health records
            - Patient consent obtained before any record sharing
            - BeyondBabyBlues Secure Health Portal (BBSHP) used for all transfers
            - Full audit trail maintained for compliance
            - Patient can access their own records via patient portal
    
            RESPONSE FORMAT REQUIREMENTS:
            When human consultation is needed, you MUST include one of these specific phrases in your response:
            
            For Crisis Situations:
            - "I'm immediately connecting you with our crisis specialist"
            - "Let me connect you with Dr. Lisa Park, our crisis psychiatrist"
            
            For Depression/Mood Disorders:
            - "I'd like to connect you with Dr. Rachel Chen, our depression specialist"
            - "Let me arrange a consultation with our mental health specialist"
            
            For Anxiety/Panic:
            - "I recommend connecting with Sarah Mitchell, our anxiety specialist"
            - "Let me connect you with our anxiety treatment specialist"
            
            For Trauma/PTSD:
            - "I'd like to connect you with Dr. Michael Rodriguez, our trauma specialist"
            
            For Medication Questions:
            - "Let me connect you with Dr. Priya Sharma for medication consultation"
            
            For High-Risk Pregnancy:
            - "I recommend consulting with Dr. Jennifer Thompson, our high-risk pregnancy specialist"
            
            For Family/Relationship Issues:
            - "Let me connect you with Dr. Amanda Foster for family therapy"
            
            For General Specialist Need:
            - "I'd like to connect you with our human specialist"
            - "Let me have our mental health professional review this"
            
            IMPORTANT: Always include these exact phrases when specialist consultation is needed so the system can detect and provide appropriate specialist buttons.
    
            Question: {question}
    
            Please provide a compassionate, supportive response. If human consultation is needed, include the appropriate specialist connection phrase from above:
            Supportive Response:
        """

    # Generate the final prompt with the user's question
    prompt = template.format(question=question)

    # Display the generated prompt
    print(Fore.GREEN + f"Prompt generated: {prompt}")

    # Create the chat message context, with the system messages guiding the assistant
    messages = [
        {"role": "system", "content": "BeyondBabyBlues is a dedicated medical group providing comprehensive support to pregnant women and their families. Our mission is to ensure that every mother receives the care and guidance she needs throughout her pregnancy journey. We offer a range of services designed to meet the physical, emotional, and educational needs of expectant mothers."},
        {"role": "system", "content": prompt},
        {"role": "user", "content": question},
    ]

    # Display the chat message for debugging/logging purposes
    print(Fore.YELLOW + f"Chat message generated: {messages}")

    return messages


def analyze_consultation_need(response_content):
    """
    Analyze the LLM response to determine if specialist consultation is needed
    and identify the appropriate specialist type.
    """
    content_lower = response_content.lower()
    
    consultation_info = {
        "needed": False,
        "type": "general",
        "specialist": "general"
    }
    
    # Crisis situations
    if any(phrase in content_lower for phrase in [
        "crisis specialist", "dr. lisa park", "crisis psychiatrist",
        "immediately connecting", "crisis team", "emergency"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "crisis",
            "specialist": "Dr. Lisa Park - Crisis Emergency"
        })
    
    # Depression/Mood specialists
    elif any(phrase in content_lower for phrase in [
        "dr. rachel chen", "depression specialist", "mental health specialist",
        "mood disorder", "depression treatment"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "depression",
            "specialist": "Dr. Rachel Chen - Depression & Anxiety"
        })
    
    # Anxiety specialists
    elif any(phrase in content_lower for phrase in [
        "sarah mitchell", "anxiety specialist", "anxiety treatment",
        "panic disorder", "anxiety therapy"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "anxiety",
            "specialist": "Sarah Mitchell - Anxiety & OCD Therapy"
        })
    
    # Trauma specialists
    elif any(phrase in content_lower for phrase in [
        "dr. michael rodriguez", "trauma specialist", "ptsd",
        "birth trauma", "trauma therapy"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "trauma",
            "specialist": "Dr. Michael Rodriguez - Trauma & PTSD"
        })
    
    # Medication specialists
    elif any(phrase in content_lower for phrase in [
        "dr. priya sharma", "medication consultation", "psychiatric medication",
        "bipolar", "medication management"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "medication",
            "specialist": "Dr. Priya Sharma - Medications & Bipolar"
        })
    
    # High-risk pregnancy specialists
    elif any(phrase in content_lower for phrase in [
        "dr. jennifer thompson", "high-risk pregnancy", "pregnancy complications",
        "maternal-fetal medicine"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "high_risk",
            "specialist": "Dr. Jennifer Thompson - High-Risk Pregnancy"
        })
    
    # Family therapy specialists
    elif any(phrase in content_lower for phrase in [
        "dr. amanda foster", "family therapy", "family support",
        "relationship issues"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "family",
            "specialist": "Dr. Amanda Foster - Family Therapy"
        })
    
    # General specialist consultation phrases
    elif any(phrase in content_lower for phrase in [
        "connect you with our human specialist", "mental health professional",
        "licensed therapist", "specialist consultation", "human consultation",
        "professional evaluation", "let me connect you", "i'd like to connect you"
    ]):
        consultation_info.update({
            "needed": True,
            "type": "general",
            "specialist": "general"
        })
    
    return consultation_info


def md_to_html(md_content):
    """
    Convert Markdown content to HTML.

    Args:
    - md_content (str): A string containing Markdown formatted text.

    Returns:
    - str: The HTML representation of the Markdown content.
    """
    html_content = markdown.markdown(md_content)
    return html_content

def parse_agent_response(raw_response):
    """
    Parse the agent response to extract only the final answer, 
    removing ReAct reasoning steps like Action:, Observation:, etc.
    """
    if not raw_response:
        return ""
    
    # Split by lines and look for patterns
    lines = raw_response.split('\n')
    
    # Remove ReAct reasoning patterns
    clean_lines = []
    skip_until_final_answer = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip ReAct reasoning patterns
        if any(pattern in line_lower for pattern in [
            'action:', 'observation:', 'thought:', 'i need to', 'action input:', 
            'next steps:', 'key compliance notes:', 'would you like me to proceed',
            'i understand you\'d like', 'to connect you with the best support',
            'fetching real-time availability', 'example specialist availability',
            'awaiting user confirmation'
        ]):
            skip_until_final_answer = True
            continue
            
        # Look for final answer indicators
        if any(indicator in line_lower for indicator in [
            'final answer:', 'answer:', 'response:', 'my recommendation:', 
            'here\'s what i found:', 'based on your question'
        ]):
            skip_until_final_answer = False
            # Take everything after the indicator
            if ':' in line:
                clean_lines.append(line.split(':', 1)[1].strip())
            continue
        
        # If we're not skipping and it's substantial content, keep it
        if not skip_until_final_answer and line.strip() and len(line.strip()) > 10:
            # Skip bullet points that look like reasoning steps
            if not any(pattern in line_lower for pattern in [
                '- dr.', '- sarah', '- if you\'re in crisis', 'please reply with:',
                'used exact referral phrases', 'fetched availability first'
            ]):
                clean_lines.append(line.strip())
    
    # Join the clean lines
    result = '\n'.join(clean_lines).strip()
    
    # If we didn't find a good extraction, try to find the most user-relevant part
    if not result or len(result) < 50:
        # Look for the most conversational/user-facing parts
        conversational_parts = []
        for line in lines:
            if line.strip() and any(pattern in line.lower() for pattern in [
                'i recommend', 'based on', 'you may be experiencing', 
                'it sounds like', 'here are some', 'i suggest'
            ]):
                conversational_parts.append(line.strip())
        
        if conversational_parts:
            result = '\n'.join(conversational_parts)
        else:
            # Fallback: return the original but try to clean obvious ReAct patterns
            result = raw_response
            for pattern in ['Action:', 'Observation:', 'Thought:', 'Action Input:']:
                result = result.replace(pattern, '')
    
    return result.strip()

def create_react_agent_executor(api_key, vector_store):
    """Create a ReAct agent with tools for knowledge search and appointment booking"""
    try:
        # Initialize the LLM
        llm = ChatMistralAI(
            model="mistral-large-latest",
            mistral_api_key=api_key,
            temperature=0.3
        )
        
        # Create tools for the agent
        tools = [
            Tool(
                name="knowledge_search",
                func=search_knowledge_base,
                description="Search the BeyondBabyBlues knowledge base for information about services, specialists, medical advice, and company details. Use this tool to answer questions about pregnancy, postpartum care, specialists, or any medical information."
            ),
            Tool(
                name="book_appointment",
                func=book_appointment_tool,
                description="Book an appointment with a specialist. Format: specialist_name|date|time|patient_email|patient_name. Example: 'Dr. Rachel Chen|2025-10-05|14:00|patient@email.com|Jane Doe'. Use this tool when a patient wants to schedule a consultation."
            ),
            Tool(
                name="get_specialists",
                func=get_available_specialists,
                description="Get a list of all available specialists with their specializations and availability. Use this tool when patients want to know about available doctors or specialists."
            )
        ]
        
        # Create the ReAct prompt template
        react_prompt = PromptTemplate.from_template("""
You are a compassionate support assistant for BeyondBabyBlues, a pregnancy help organization specializing in mental health and emotional well-being support for expectant and new mothers.

Your primary role is to provide empathetic, clear, and accurate guidance for pregnant women and new mothers experiencing mental health challenges, distress, or emotional difficulties.

Core Responsibilities:
- Provide supportive, non-judgmental responses to mental health concerns during pregnancy and postpartum
- Recognize signs of prenatal and postpartum depression, anxiety, mood disorders, and emotional distress
- Offer practical coping strategies and emotional support resources
- Connect women with appropriate professional mental health services
- Validate feelings and normalize the emotional challenges of pregnancy and new motherhood
- Book appointments with specialists when requested
- Maintain human oversight for complex situations requiring professional judgment

Mental Health Support Guidelines:
- Always acknowledge and validate emotional struggles - pregnancy and postpartum can be overwhelming
- Recognize symptoms of postpartum depression: persistent sadness, anxiety, mood swings, sleep issues, loss of interest
- Identify anxiety disorders: excessive worry, panic attacks, fear about pregnancy/childbirth, social withdrawal
- Watch for signs of severe distress: thoughts of self-harm, inability to function, severe mood changes
- Provide immediate crisis intervention guidance when needed
- Emphasize that seeking mental health support is a sign of strength, not weakness

Human-in-the-Loop Guidelines & Specialist Referrals:
When specialist consultation is needed, you MUST include one of these specific phrases in your response:

For Crisis Situations:
- "I'm immediately connecting you with our crisis specialist"
- "Let me connect you with Dr. Lisa Park, our crisis psychiatrist"

For Depression/Mood Disorders:
- "I'd like to connect you with Dr. Rachel Chen, our depression specialist"
- "Let me arrange a consultation with our mental health specialist"

For Anxiety/Panic:
- "I recommend connecting with Sarah Mitchell, our anxiety specialist"
- "Let me connect you with our anxiety treatment specialist"

For Trauma/PTSD:
- "I'd like to connect you with Dr. Michael Rodriguez, our trauma specialist"

For Medication Questions:
- "Let me connect you with Dr. Priya Sharma for medication consultation"

For High-Risk Pregnancy:
- "I recommend consulting with Dr. Jennifer Thompson, our high-risk pregnancy specialist"

For Family/Relationship Issues:
- "Let me connect you with Dr. Amanda Foster for family therapy"

Available Tools:
- knowledge_search: Search for information in the BeyondBabyBlues knowledge base
- book_appointment: Schedule appointments with specialists
- get_specialists: Get list of available specialists

IMPORTANT: Always use these exact phrases when specialist consultation is needed so the system can detect and provide appropriate specialist buttons.

CRITICAL RESPONSE GUIDELINES:
- Your Final Answer should be conversational, warm, and directly address the user
- Do NOT include your reasoning process (Thought/Action/Observation) in the Final Answer
- Only provide clean, user-friendly responses in the Final Answer section
- Keep responses focused and helpful without overwhelming technical details
- Always end with a clear next step or invitation for further questions

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}
""")
        
        # Create the ReAct agent
        agent = create_react_agent(llm, tools, react_prompt)
        
        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,  # Set to False to hide internal reasoning from users
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True
        )
        
        return agent_executor
        
    except Exception as e:
        print(Fore.RED + f"Error creating ReAct agent: {e}")
        return None

def init_qa_chain():
    global vector_store
    try:
        # Define file paths and flags for loading
        knowledgebases = [
            {
                "path": "./datasets/BeyondBabyBlues.txt",
                "use": True,
                "type": "company"
            },
            {
                "path": "./datasets/pregnancy.txt",
                "use": True,
                "type": "medical"
            }, {
                "path": "./datasets/post-natal.csv",
                "use": True,
                "type": "medical"
            }
        ]

        # Ensure vector_store is defined before this block
        vector_store = None  # or the appropriate logic to obtain the vector_store
        index_name = "medical_faiss_index_mistral"
        api_key = get_mistral_api_key()

        for kb in knowledgebases:
            if kb["use"]:
                chunks = []
                print(Fore.BLUE + f"Loading {kb['type']} data...")
                if kb["type"] == "product":
                    documents = json_to_documents(kb["path"])
                else:
                    file_extension = os.path.splitext(kb["path"])[1].lower()
                    if file_extension == ".json":
                        documents = json_to_documents(kb["path"])
                    elif file_extension in [".txt", ".csv", ".xlsx"]:  # Add other extensions as needed
                        documents = load_file(kb["path"])
                    else:
                        raise ValueError(f"Unsupported file extension: {file_extension}")
                if documents is not None and len(documents) > 0:
                    # Split Documents into Chunks
                    document_chunks = split_documents(documents)
                    print(Fore.YELLOW + f"Number of {kb['type']} chunks: {len(document_chunks)}")
                    print(Fore.MAGENTA + f"First 2 {kb['type']} chunks: {document_chunks[:2]}")
                    chunks.extend(document_chunks)

                if not chunks:
                    print(Fore.RED + f"##[warning] No chunks loaded for {kb['path']}. Exiting initialization.")
                    #exit if loop and go to while loop
                    continue


                batch_size = 500  # Adjust the batch size based on your rate limits
                start_index = 0
                total_chunks = len(chunks)
                print(Fore.CYAN + f"##[debug]Number of chunks: {len(chunks)} in {kb['path']}")

                while start_index < total_chunks:
                    # Get the current batch
                    end_index = min(start_index + batch_size, total_chunks)
                    current_batch = chunks[start_index:end_index]
                    # Store embeddings for the current batch
                    vector_store = store_embeddings_in_faiss(api_key, current_batch, index_name, kb["path"])
                    print(Fore.CYAN + f"Processed batch of {kb['path']}:{start_index} to {end_index}")

                    # Move to the next batch
                    start_index = end_index

                print(Fore.GREEN + f"COMPLETED: Stored embeddings for {kb['type']} from {kb['path']}.")

        if vector_store:
            agent_executor = create_react_agent_executor(api_key, vector_store)
            if agent_executor:
                print(Fore.GREEN + "##[debug]ReAct Agent initialized successfully!")
                return agent_executor
            else:
                print(Fore.RED + "##[error] Failed to initialize ReAct Agent.")
                return None
    except Exception as e:
        logging.error(Fore.RED + f"##[error] An error occurred during initialization: {e}")
        raise


# Initialize the ReAct Agent
try:
    print(Fore.YELLOW + "##[debug] Initializing ReAct Agent...")
    agent_executor = init_qa_chain()
    if agent_executor:
        print(Fore.GREEN + "##[debug] Agent executor successfully created!")
        print(Fore.CYAN + f"##[debug] Agent type: {type(agent_executor)}")
    else:
        print(Fore.RED + "##[error] Agent executor is None!")
except Exception as e:
    print(Fore.RED + f"##[error] Failed to initialize agent executor: {e}")
    import traceback
    traceback.print_exc()
    agent_executor = None


# Start Flask app
if __name__ == '__main__':
    try:
        print(Fore.CYAN + f"##[debug] Agent executor status: {agent_executor is not None}")
        if agent_executor is None:
            print(Fore.RED + "##[error] Cannot start server - agent executor not initialized")
            exit(1)
        
        logging.info(Fore.CYAN + "##[section] Starting Flask application...")
        print(Fore.CYAN + f"##[debug] Running REST API on port: 5000...")
        print(Fore.GREEN + "##[debug] Server starting in development mode...")
        print(Fore.CYAN + f"##[debug] About to start Flask server...")
        print(Fore.YELLOW + "##[info] Press CTRL+C to stop the server")
        app.run(host='localhost', port=5000, debug=True, use_reloader=False, threaded=True)
    except Exception as e:
        logging.error(Fore.RED + f"##[error] An error occurred while starting the Flask application: {e}")
        import traceback
        traceback.print_exc()