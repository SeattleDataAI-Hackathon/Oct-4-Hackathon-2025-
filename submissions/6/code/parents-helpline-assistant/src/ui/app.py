"""Streamlit UI for Parents Healthline Assistant."""
import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.database.connection import SessionLocal
from src.services import ConversationService, SymptomService, DiagnosisService, RemedyService, AuthService
from src.agents import HealthAssistant
from src.utils.logger import setup_logger
from src.ui.auth_pages import show_auth_page
import asyncio

# Setup logger
logger = setup_logger()

# Page configuration
st.set_page_config(
    page_title="Parents Healthline Assistant",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .safety-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    # Check if user is authenticated
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = None  # None means not checked yet

    if "user" not in st.session_state:
        st.session_state.user = None

    if "app_session" not in st.session_state:
        st.session_state.app_session = None

    if "db_session" not in st.session_state:
        st.session_state.db_session = None

    if "current_conversation" not in st.session_state:
        st.session_state.current_conversation = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "child_age_months" not in st.session_state:
        st.session_state.child_age_months = None

    if "child_name" not in st.session_state:
        st.session_state.child_name = None

    if "health_assistant" not in st.session_state:
        try:
            st.session_state.health_assistant = HealthAssistant()
        except ValueError as e:
            st.error(f"⚠️ {str(e)}\n\nPlease set your ANTHROPIC_API_KEY in the .env file.")
            st.stop()


def start_new_conversation():
    """Start a new conversation."""
    from datetime import datetime

    db = st.session_state.db_session
    conv_service = ConversationService()

    # Create conversation title with timestamp
    timestamp = datetime.now().strftime("%b %d, %Y - %I:%M %p")
    title = f"Chat - {timestamp}"

    # Create new conversation
    conversation = conv_service.create_conversation(
        db=db,
        session_id=st.session_state.app_session.id,
        title=title,
        child_age_months=st.session_state.child_age_months,
        child_name=st.session_state.child_name,
    )

    st.session_state.current_conversation = conversation
    st.session_state.messages = []

    # Add welcome message
    welcome_msg = """👋 Hello! I'm here to help you with your baby's health concerns.

I understand how stressful it can be when your little one isn't feeling well. I'm here to listen, gather information about the symptoms, and provide guidance on next steps.

**Before we begin:**
- This is an AI assistant providing general information only
- Always consult with your pediatrician for professional medical advice
- If you believe this is an emergency, please call 911 or go to the nearest emergency room

**How can I help you today?**"""

    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

    # Save welcome message to database
    conv_service.add_message(
        db=db,
        conversation_id=conversation.id,
        role="assistant",
        content=welcome_msg,
    )


async def send_message(user_message: str):
    """Send a message and get AI response."""
    db = st.session_state.db_session
    conv_service = ConversationService()
    assistant = st.session_state.health_assistant

    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": user_message})

    # Save user message to database
    conv_service.add_message(
        db=db,
        conversation_id=st.session_state.current_conversation.id,
        role="user",
        content=user_message,
    )

    # Get conversation history for AI
    history = conv_service.get_conversation_history(
        db=db,
        conversation_id=st.session_state.current_conversation.id,
    )

    # Get AI response
    response = await assistant.chat(
        message=user_message,
        conversation_history=history[:-1],  # Exclude the message we just added
        child_age_months=st.session_state.child_age_months,
        include_safety_disclaimer=False,  # We'll add this selectively
        is_authenticated=st.session_state.is_authenticated,
    )

    assistant_message = response.get("content", "I apologize, but I encountered an error. Please try again.")

    # Add assistant message to UI
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})

    # Save assistant message to database
    conv_service.add_message(
        db=db,
        conversation_id=st.session_state.current_conversation.id,
        role="assistant",
        content=assistant_message,
        metadata={
            "response_time": response.get("response_time"),
            "model": response.get("model"),
            "tokens_used": response.get("tokens_used"),
        },
    )


def display_chat():
    """Display chat messages."""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(content)


def sidebar():
    """Render sidebar with conversation history and settings."""
    with st.sidebar:
        st.title("👶 Parents Healthline")

        # Hackathon mode: Simple header
        st.markdown("**Parents Healthline** 🏥")
        st.caption("Hackathon Demo Version")

        st.markdown("---")

        # New conversation button
        if st.button("🆕 Start New Conversation", use_container_width=True):
            start_new_conversation()
            st.rerun()

        st.markdown("---")

        # Conversation history for hackathon demo
        st.subheader("Conversation History")
        conv_service = ConversationService()
        conversations = conv_service.get_conversations_by_session(
            db=st.session_state.db_session,
            session_id=st.session_state.app_session.id,
        )

        if conversations:
            for conv in conversations[:10]:  # Show last 10 conversations
                # Show full title if short, truncate if long
                display_title = conv.title if len(conv.title) <= 35 else f"{conv.title[:32]}..."

                if st.button(
                    f"📝 {display_title}",
                    key=f"conv_{conv.id}",
                    use_container_width=True,
                ):
                    # Load conversation
                    st.session_state.current_conversation = conv
                    st.session_state.child_age_months = conv.child_age_months
                    st.session_state.child_name = conv.child_name

                    # Load messages
                    history = conv_service.get_conversation_history(
                        db=st.session_state.db_session,
                        conversation_id=conv.id,
                    )
                    st.session_state.messages = history
                    st.rerun()
        else:
            st.caption("No conversations yet")

        st.markdown("---")

        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Parents Healthline Assistant**

            This AI-powered assistant helps parents with babies (0-3 years) get quick health guidance when their little ones are sick.

            **Features:**
            - Empathetic symptom intake
            - Preliminary condition assessment
            - Home care recommendations
            - Clear guidance on when to seek professional help

            **Remember:** This is not a substitute for professional medical advice.
            """)

        # Emergency notice
        st.info("🆘 **If you think this is an emergency:** Take a deep breath, stay calm, and call 911 or go to your nearest ER. You've got this.")


def main():
    """Main application."""
    initialize_session_state()

    # For hackathon: Skip auth and go straight to guest mode
    if st.session_state.is_authenticated is None:
        # Auto-create guest session
        db = SessionLocal()
        try:
            auth_service = AuthService()
            app_session, token = auth_service.create_session(
                db, user_id=None, role="parent"
            )
            st.session_state.user = None
            st.session_state.app_session = app_session
            st.session_state.access_token = token
            st.session_state.is_authenticated = False
            st.session_state.db_session = db
        except Exception as e:
            st.error(f"Error starting session: {str(e)}")
            st.stop()

    # User is in guest mode - show main app
    # Sidebar
    sidebar()

    # Main chat area
    st.title("💬 Chat with Healthcare Assistant")

    # Start conversation if none exists
    if not st.session_state.current_conversation:
        start_new_conversation()

    # Display chat history
    display_chat()

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Run async function
        asyncio.run(send_message(prompt))
        st.rerun()


if __name__ == "__main__":
    main()
