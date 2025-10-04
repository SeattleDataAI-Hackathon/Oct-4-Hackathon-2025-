# Implementation Plan

## Tech Stack Decisions

### LLM Provider
**Chosen**: Anthropic Claude 3.5 Sonnet
- Reason: Best for empathetic, nuanced healthcare conversations

### Authentication
**Chosen**: Optional login (anonymous OR authenticated for history)
- Anonymous users can chat without login
- Authenticated users get conversation history

### Home Remedies Database
**Chosen**: Predefined list in PostgreSQL
- Pre-approved by medical guidelines
- Age-filtered (0-36 months)

### Healthcare Professional Portal
**Chosen**: Database access only in MVP
- No separate UI in initial version
- Data accessible via database queries

### Diagnosis Approach
**Chosen**: Hybrid (LLM + Medical Knowledge Base)
- Claude AI for conversational flow
- Structured symptom checking
- Integration with CDC/WebMD guidelines

### Deployment
**Chosen**: Local development with Docker
- PostgreSQL in Docker container
- Easy setup for hackathon demo

## Architecture

### Technology Stack
- **Backend**: Python 3.10+ with FastAPI (optional API layer)
- **Frontend**: Streamlit (rapid prototyping)
- **AI**: Anthropic Claude API
- **Database**: PostgreSQL 15 (Docker)
- **ORM**: SQLAlchemy with Alembic migrations
- **Testing**: pytest with coverage
- **Package Manager**: UV (10-100x faster than pip)

### System Design

```
┌─────────────────┐
│   Streamlit UI  │  ← Parent interacts
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Health Agent   │  ← Claude AI + Logic
│  (Claude API)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Services      │  ← Business Logic
│  - Auth         │
│  - Conversation │
│  - Symptoms     │
│  - Diagnosis    │
│  - Remedies     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL DB  │  ← Data Persistence
│  (Docker)       │
└─────────────────┘
```

### Database Schema

**Tables:**
1. `users` - User accounts (id, username, email, password_hash)
2. `sessions` - User sessions (authenticated or anonymous)
3. `conversations` - Chat threads
4. `messages` - Individual messages
5. `symptoms` - Tracked symptoms
6. `diagnoses` - AI diagnoses with confidence scores
7. `recommendations` - Treatment suggestions
8. `home_remedies` - Pre-approved remedies database
9. `conversation_access_log` - Healthcare professional access audit

**Relationships:**
```
users (1) ──── (N) sessions
sessions (1) ──── (N) conversations
conversations (1) ──── (N) messages
conversations (1) ──── (N) symptoms
conversations (1) ──── (N) diagnoses
diagnoses (1) ──── (N) recommendations
```

## Implementation Phases

### Phase 1: Setup & Infrastructure
- [x] Project structure setup
- [x] Docker Compose for PostgreSQL
- [x] SQLAlchemy models
- [x] Alembic migrations
- [x] Environment configuration

### Phase 2: Core Services
- [x] Authentication service
- [x] Conversation service
- [x] Symptom service
- [x] Diagnosis service
- [x] Remedy service

### Phase 3: AI Integration
- [x] Claude API integration
- [x] System prompts (empathetic, healthcare-focused)
- [x] Context management
- [x] Red flag detection
- [x] Safety disclaimers

### Phase 4: User Interface
- [x] Streamlit app setup
- [x] Chat interface
- [x] Conversation history
- [x] Session management
- [x] Baby age input

### Phase 5: Testing
- [x] Unit tests (services)
- [x] Integration tests (full flow)
- [x] Test fixtures
- [x] Coverage reporting

### Phase 6: Documentation & Deployment
- [x] README documentation
- [x] Makefile automation
- [x] Environment setup guide
- [x] Security guidelines
- [x] VSCode configuration

## Development Workflow

1. **Setup Environment**
   ```bash
   uv venv && source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```

2. **Start Database**
   ```bash
   make db-start
   make db-migrate
   make db-seed
   ```

3. **Run Application**
   ```bash
   make run
   ```

4. **Test**
   ```bash
   make test
   make test-coverage
   ```

## Key Features Implementation

### 1. Empathetic Chat Agent
- Custom system prompts for warm, supportive tone
- Context-aware responses
- Age-appropriate language

### 2. Symptom Intake
- Conversational symptom gathering
- Severity tracking
- Parent verification loop

### 3. Diagnosis Engine
- Hybrid approach: AI + rules
- Confidence scoring
- Multiple data sources (CDC, WebMD references)

### 4. Safety Features
- Red flag detection (emergency symptoms)
- AI-generated content disclaimers
- Professional referral guidance
- Age validation for remedies

### 5. Home Remedies
- Pre-approved database (19+ remedies)
- Age filtering (0-36 months)
- Safety notes included
- Conditions: Cold, Fever, Cough, Teething, Diaper Rash, Constipation, Gas/Colic

## Performance Considerations

- **Response Time**: < 5 seconds per AI response
- **Concurrency**: Support 1000+ concurrent users
- **Database**: Connection pooling, indexed queries
- **Caching**: Session state management

## Security Implementation

- Password hashing: bcrypt
- Session tokens: JWT
- API key management: Environment variables
- SQL injection prevention: SQLAlchemy ORM
- Input validation: Pydantic models

## Monitoring & Logging

- Comprehensive logging with loguru
- Response time tracking
- Token usage monitoring
- Error tracking and graceful degradation

## Success Metrics

- ✅ All functional requirements met
- ✅ Response time < 5 seconds
- ✅ Test coverage > 70%
- ✅ Zero critical security issues
- ✅ Smooth demo experience
