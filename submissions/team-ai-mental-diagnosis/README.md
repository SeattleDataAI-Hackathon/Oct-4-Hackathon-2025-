# Healthcare Hackathon - AI-Powered Mental Health Platform

**Team: The Company**

A comprehensive healthcare platform built for a hackathon that combines patient information management with AI-powered mood analysis from phone call transcripts. The system provides secure patient data storage, real-time mood assessment, and comprehensive reporting capabilities.

## 🚀 Overview

This platform is designed to help healthcare providers track patient mental health through structured data collection and AI-powered analysis of phone call conversations. It features a modern React frontend with Supabase backend, including Edge Functions for AI integration.

## 🏗️ Architecture

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Supabase Client** for authentication and data management
- **Lucide React** for icons
- **Modern CSS** with responsive design

### Backend
- **Supabase** (PostgreSQL database + Edge Functions)
- **OpenAI GPT-4** for AI mood analysis
- **Row Level Security (RLS)** for data protection
- **JWT Authentication** for secure access

## 📋 Core Functionality

### 1. Patient Information Management
- **Demographic Data**: Age, gender, occupation, relationship status, living situation
- **Mental Health History**: Diagnoses, therapy history, medications, hospitalizations
- **Risk Assessment**: Past and current self-harm thoughts tracking
- **Additional Information**: Free-form notes and observations

### 2. AI-Powered Mood Analysis
- **Real-time Analysis**: Automatic mood assessment from phone call transcripts
- **Mood Rating**: 1-5 scale with detailed descriptions
- **Emotion Detection**: Specific emotions identified in conversations
- **Context-Aware**: Uses patient history for better analysis

### 3. Call Reports Dashboard
- **Report Visualization**: Comprehensive view of all call reports
- **Mood Tracking**: Historical mood trends and patterns
- **Search & Filter**: Find reports by phone number, date, mood
- **Detailed Analytics**: Summary statistics and insights

### 4. Secure Authentication
- **Email/Password Authentication** via Supabase Auth
- **Session Management** with automatic token refresh
- **Protected Routes** with authentication guards
- **User Data Isolation** with Row Level Security

## 🔌 API Endpoints

### Authentication Endpoints
All authentication is handled by Supabase Auth with the following endpoints:

```
POST /auth/v1/signup
POST /auth/v1/token?grant_type=password
POST /auth/v1/logout
```

### User Information Endpoints

#### Save User Information
```
POST /functions/v1/save-user-info
```

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <JWT_TOKEN>
apikey: <SUPABASE_ANON_KEY>
```

**Request Body:**
```json
{
  "age": "25",
  "gender": "female",
  "occupation": "Software Engineer",
  "relationship_status": "single",
  "living_situation": "alone",
  "phone_number": "+1234567890",
  "mental_health_diagnosis": "Anxiety, Depression",
  "therapy_history": "6 months of CBT",
  "psychiatric_medication": "Sertraline 50mg",
  "mental_health_hospitalization": "None",
  "past_self_harm_thoughts": "None",
  "current_self_harm_thoughts": "Occasional anxiety",
  "additional_info": "Patient prefers morning appointments"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User information saved successfully",
  "data": {
    "id": "uuid",
    "user_id": "user-uuid",
    "age": "25",
    "gender": "female",
    "created_at": "2024-12-20T...",
    "updated_at": "2024-12-20T..."
  }
}
```

#### Get User Information
```
GET /functions/v1/get-user-info
```

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
apikey: <SUPABASE_ANON_KEY>
```

**Response:**
```json
{
  "success": true,
  "message": "User information retrieved successfully",
  "data": {
    "id": "uuid",
    "user_id": "user-uuid",
    "age": "25",
    "gender": "female",
    "occupation": "Software Engineer",
    "relationship_status": "single",
    "living_situation": "alone",
    "phone_number": "+1234567890",
    "mental_health_diagnosis": "Anxiety, Depression",
    "therapy_history": "6 months of CBT",
    "psychiatric_medication": "Sertraline 50mg",
    "mental_health_hospitalization": "None",
    "past_self_harm_thoughts": "None",
    "current_self_harm_thoughts": "Occasional anxiety",
    "additional_info": "Patient prefers morning appointments",
    "created_at": "2024-12-20T...",
    "updated_at": "2024-12-20T..."
  }
}
```

### Phone Call Reports Endpoints

#### Save Phone Call Report
```
POST /functions/v1/save-phone-call-report
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "type": "phone_call_completed",
  "event_timestamp": 1703001600,
  "data": {
    "agent_id": "agent-123",
    "conversation_id": "conv-456",
    "status": "completed",
    "user_id": "user-uuid",
    "transcript": [
      {
        "role": "agent",
        "message": "Hello, how are you feeling today?",
        "time_in_call_secs": 0
      },
      {
        "role": "patient",
        "message": "I'm feeling a bit anxious about my upcoming appointment",
        "time_in_call_secs": 5
      }
    ],
    "metadata": {
      "start_time_unix_secs": 1703001600,
      "call_duration_secs": 300,
      "cost": 0.50,
      "termination_reason": "completed"
    },
    "analysis": {
      "call_successful": "true",
      "transcript_summary": "Patient expressed anxiety about upcoming appointment"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Phone call report saved successfully with AI mood analysis",
  "data": {
    "id": "uuid",
    "user_id": "user-uuid",
    "mood": 3,
    "mood_description": "Patient shows signs of anxiety and concern about upcoming medical appointment",
    "emotions": ["anxiety", "concern", "uncertainty"],
    "created_at": "2024-12-20T..."
  },
  "mood_analysis": {
    "mood": 3,
    "mood_description": "Patient shows signs of anxiety and concern about upcoming medical appointment",
    "emotions": ["anxiety", "concern", "uncertainty"]
  }
}
```

#### Get Phone Call Reports
```
GET /functions/v1/get-phone-call-reports
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 10, max: 100)
- `sort` (optional): Sort order - "asc" or "desc" (default: "desc")

**Response:**
```json
{
  "success": true,
  "message": "Phone call reports retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "user_id": "user-uuid",
      "mood": 4,
      "mood_description": "Patient appears positive and engaged",
      "emotions": ["hopeful", "engaged", "positive"],
      "created_at": "2024-12-20T..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "totalCount": 25,
    "totalPages": 3,
    "hasNextPage": true,
    "hasPrevPage": false
  }
}
```

## 🗄️ Database Schema

### User Information Table
```sql
CREATE TABLE public.user_information (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    information TEXT NOT NULL,
    -- Demographics
    age VARCHAR(10),
    gender VARCHAR(50),
    occupation VARCHAR(255),
    relationship_status VARCHAR(50),
    living_situation VARCHAR(50),
    phone_number VARCHAR(20),
    -- Mental Health
    mental_health_diagnosis TEXT,
    therapy_history TEXT,
    psychiatric_medication TEXT,
    mental_health_hospitalization TEXT,
    past_self_harm_thoughts TEXT,
    current_self_harm_thoughts TEXT,
    -- Additional Info
    additional_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id)
);
```

### Phone Call Reports Table
```sql
CREATE TABLE public.phone_call_reports (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    mood INTEGER CHECK (mood >= 1 AND mood <= 5),
    mood_description TEXT NOT NULL,
    emotions TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🔒 Security Features

### Row Level Security (RLS)
- **User Data Isolation**: Users can only access their own information
- **Automatic Policy Enforcement**: Database-level security policies
- **JWT Token Validation**: All requests require valid authentication

### Data Protection
- **Encrypted Storage**: All data encrypted at rest
- **Secure Authentication**: Supabase Auth with JWT tokens
- **CORS Protection**: Proper CORS headers on all endpoints
- **Input Validation**: Comprehensive validation on all inputs

## 🤖 AI Integration

### OpenAI GPT-4 Integration
- **Mood Analysis**: Automatic mood assessment from transcripts
- **Emotion Detection**: Identifies specific emotions
- **Context Awareness**: Uses patient history for better analysis
- **Structured Output**: JSON schema for consistent responses

### AI Features
- **Real-time Processing**: Immediate analysis of call transcripts
- **Mood Rating**: 1-5 scale with detailed descriptions
- **Emotion Tagging**: Specific emotions identified and tagged
- **Historical Context**: Uses patient data for better insights

## 🚀 Getting Started

### Prerequisites
- Docker Desktop running
- Supabase CLI installed
- Node.js 18+ installed
- OpenAI API key

### Backend Setup

1. **Start Supabase locally:**
   ```bash
   supabase start
   ```

2. **Apply database migrations:**
   ```bash
   supabase db reset
   ```

3. **Deploy Edge Functions:**
   ```bash
   supabase functions deploy save-user-info
   supabase functions deploy get-user-info
   supabase functions deploy save-phone-call-report
   supabase functions deploy get-phone-call-reports
   ```

4. **Set Environment Variables:**
   ```bash
   # In your Supabase project settings
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your Supabase credentials
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Build for production:**
   ```bash
   npm run build
   ```

## 🧪 Testing

### Test Edge Functions
```bash
# Test save-user-info function
curl -X POST http://127.0.0.1:54321/functions/v1/save-user-info \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "apikey: YOUR_ANON_KEY" \
  -d '{"age": "25", "gender": "female", "occupation": "Software Engineer"}'

# Test get-user-info function
curl -X GET http://127.0.0.1:54321/functions/v1/get-user-info \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "apikey: YOUR_ANON_KEY"
```

### Test Phone Call Report
```bash
curl -X POST http://127.0.0.1:54321/functions/v1/save-phone-call-report \
  -H "Content-Type: application/json" \
  -d '{
    "type": "phone_call_completed",
    "event_timestamp": 1703001600,
    "data": {
      "transcript": [
        {"role": "patient", "message": "I am feeling anxious today", "time_in_call_secs": 0}
      ]
    }
  }'
```

## 📱 Frontend Components

### Dashboard Component
- **Welcome Section**: Overview of platform features
- **Navigation**: Access to patient info and call reports
- **User Management**: Sign out and user profile display

### Patient Information Component
- **Demographic Form**: Age, gender, occupation, relationship status
- **Mental Health History**: Diagnoses, therapy, medications, hospitalizations
- **Risk Assessment**: Self-harm thoughts tracking
- **Edit/Save Functionality**: Real-time form editing with validation

### Calls Reports Component
- **Report List**: Paginated view of all call reports
- **Mood Visualization**: Color-coded mood ratings with icons
- **Search & Filter**: Find reports by phone number
- **Detailed Modal**: Full report details with emotions and descriptions
- **Analytics Dashboard**: Summary statistics and trends

### Authentication Component
- **Login/Signup**: Email and password authentication
- **Form Validation**: Client-side validation with error handling
- **Password Security**: Show/hide password functionality
- **Success/Error Messages**: User feedback for all actions

## 🔧 Development

### Local Development
```bash
# Start Supabase
supabase start

# View logs
supabase functions logs save-user-info

# Access Supabase Studio
open http://localhost:54323
```

### Environment Variables
```bash
# Frontend (.env.local)
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Supabase Functions
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## 📊 Features Summary

### ✅ Implemented Features
- [x] User authentication and session management
- [x] Patient information management with structured data
- [x] AI-powered mood analysis from phone call transcripts
- [x] Comprehensive call reports dashboard
- [x] Search and filtering capabilities
- [x] Responsive design with modern UI
- [x] Row Level Security for data protection
- [x] Real-time form editing and validation
- [x] Pagination for large datasets
- [x] Detailed analytics and reporting

### 🔄 Future Enhancements
- [ ] Real-time notifications for mood changes
- [ ] Advanced analytics and trend analysis
- [ ] Integration with external healthcare systems
- [ ] Mobile app development
- [ ] Voice-to-text transcription
- [ ] Automated appointment scheduling
- [ ] Multi-language support
- [ ] Advanced AI models for better analysis

## 🛠️ Technologies Used

### Frontend
- **React 18.2.0** - UI framework
- **TypeScript 5.2.2** - Type safety
- **Vite 5.2.0** - Build tool and dev server
- **Lucide React 0.544.0** - Icon library
- **CSS3** - Styling with modern features

### Backend
- **Supabase** - Backend-as-a-Service
- **PostgreSQL 17** - Database
- **Deno 1.x** - Edge Functions runtime
- **OpenAI GPT-4** - AI mood analysis
- **JWT** - Authentication tokens

### Development Tools
- **Supabase CLI** - Local development
- **Docker** - Containerization
- **Git** - Version control
- **Node.js 18+** - JavaScript runtime

## 📝 License

This project is developed for a healthcare hackathon and is intended for educational and demonstration purposes.

## 🤝 Contributing

This is a hackathon project. For questions or contributions, please contact the development team.

## 👨‍💻 Developer

**Oleksandr Khomin** - Software Engineer & Startup Enthusiast
- GitHub: [@okhomin](https://github.com/okhomin)
- Location: Seattle, United States
- Expertise: Golang, AWS, Docker, Kubernetes, PostgreSQL

---

**Built with ❤️ for Healthcare Innovation**