"""SQLAlchemy database models for the Parents Healthline Assistant."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class User(Base):
    """User model for authenticated users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="parent")
    email_verified = Column(Boolean, default=False)  # For HIPAA compliance
    verification_token = Column(String(255), nullable=True)
    oauth_provider = Column(String(50), nullable=True)  # google, apple, etc.
    oauth_provider_id = Column(String(255), nullable=True)  # ID from OAuth provider
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sessions = relationship("Session", back_populates="user")


class Session(Base):
    """Session model for tracking user sessions (authenticated or anonymous)."""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for anonymous
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    is_authenticated = Column(Boolean, default=False)
    role = Column(String(50), default="parent")  # parent, healthcare_professional
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session")


class Conversation(Base):
    """Conversation model for chat threads."""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    title = Column(String(255), default="New Conversation")
    status = Column(String(50), default="active")  # active, completed, archived
    child_age_months = Column(Integer, nullable=True)  # Age in months (0-36)
    child_name = Column(String(100), nullable=True)  # Child's name for conversation title
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("Session", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    symptoms = relationship("Symptom", back_populates="conversation", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    """Message model for individual chat messages."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_metadata = Column(JSON, nullable=True)  # Additional data like response time, sources
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Symptom(Base):
    """Symptom model for tracking reported symptoms."""
    __tablename__ = "symptoms"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    symptom_name = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=True)  # mild, moderate, severe
    duration = Column(String(100), nullable=True)  # e.g., "2 days", "since morning"
    parent_verified = Column(Boolean, default=False)
    additional_details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="symptoms")


class Diagnosis(Base):
    """Diagnosis model for AI-generated diagnoses."""
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    condition = Column(String(255), nullable=False)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    data_sources = Column(JSON, nullable=True)  # CDC, WebMD, etc.
    reasoning = Column(Text, nullable=True)
    requires_urgent_care = Column(Boolean, default=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="diagnoses")
    recommendations = relationship("Recommendation", back_populates="diagnosis", cascade="all, delete-orphan")


class Recommendation(Base):
    """Recommendation model for treatment suggestions."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=False)
    recommendation_type = Column(String(100), nullable=False)  # monitoring, medication, home_remedy, escalation
    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)  # 1 = high, 2 = medium, 3 = low
    safety_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    diagnosis = relationship("Diagnosis", back_populates="recommendations")


class HomeRemedy(Base):
    """Home remedy database with pre-approved remedies."""
    __tablename__ = "home_remedies"

    id = Column(Integer, primary_key=True, index=True)
    condition = Column(String(255), nullable=False, index=True)
    remedy_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    safety_notes = Column(Text, nullable=True)
    min_age_months = Column(Integer, default=0)  # Minimum age in months
    max_age_months = Column(Integer, default=36)  # Maximum age in months
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ConversationAccessLog(Base):
    """Audit log for healthcare professional access."""
    __tablename__ = "conversation_access_log"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    accessed_by_session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    access_type = Column(String(50), nullable=False)  # view, comment, update
    accessed_at = Column(DateTime(timezone=True), server_default=func.now())
