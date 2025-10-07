# 🌿 EcoWallet - AI-Powered Sustainability Assistant

**Human + AI One-Day Hackathon Submission**  
_Date: October 4th, 2025 | Location: Bellevue City Hall_  
_Theme: Human-in-the-Loop (HITL)_

## 👥 Team Members

- **Abhishek Vishwakarma**
- **Aaditya Bajpai**

## 🎯 Project Overview

EcoWallet is an innovative AI-powered sustainability assistant that helps users make more environmentally conscious spending decisions. By analyzing receipt images using Google's Gemini AI, the application provides personalized sustainability scores, actionable eco-friendly alternatives, and potential savings estimates.

### Key Features

- 📸 **Receipt Analysis**: Upload receipt images to get instant sustainability insights
- 🎯 **Sustainability Scoring**: Get a score from 1-100 based on your purchases
- 💡 **Smart Suggestions**: Receive personalized eco-friendly alternatives
- 💰 **Savings Calculator**: See potential monthly savings from sustainable swaps
- 🤖 **AI Chat Assistant**: Interactive chatbot for sustainability tips and advice
- 📊 **Dashboard Analytics**: Track your sustainability journey over time

## 🏗️ Architecture

### Backend (Python Flask)

- **Framework**: Flask with CORS support
- **AI Integration**: Google Gemini 2.5 Flash for multimodal analysis
- **Data Storage**: JSON-based file system for user data
- **File Handling**: Secure file upload and processing

### Frontend (Next.js)

- **Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS for modern, responsive design
- **State Management**: React hooks for local state
- **UI Components**: Custom components with drag-and-drop file upload

## 📁 Project Structure

```
ecowallet/
├── ecowallet-backend/           # Python Flask Backend
│   ├── app.py                   # Main Flask application
│   ├── requirements.txt         # Python dependencies
│   ├── database/
│   │   └── users.json          # User data storage
│   └── uploads/                # Receipt image storage
│       ├── IMG_0726.png
│       └── IMG_0727.png
├── ecowallet-frontend/          # Next.js Frontend
│   ├── app/
│   │   ├── page.tsx            # Main application component
│   │   ├── layout.tsx          # App layout
│   │   ├── globals.css         # Global styles
│   │   └── favicon.ico
│   ├── public/                 # Static assets
│   ├── package.json            # Node.js dependencies
│   ├── next.config.ts          # Next.js configuration
│   ├── tsconfig.json           # TypeScript configuration
│   └── tailwind.config.js      # Tailwind CSS configuration
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- Google Gemini API key

### Backend Setup

1. **Navigate to backend directory**

   ```bash
   cd ecowallet-backend
   ```

2. **Create and activate virtual environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the backend directory:

   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the backend server**
   ```bash
   python app.py
   ```
   The backend will be available at `http://localhost:5001`

### Frontend Setup

1. **Navigate to frontend directory**

   ```bash
   cd ecowallet-frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:3000`

## 🔧 Configuration

### Backend Configuration

- **Port**: 5001 (configurable in `app.py`)
- **CORS**: Enabled for cross-origin requests
- **File Upload**: Supports PNG, JPG, JPEG formats
- **Database**: JSON file-based storage in `database/users.json`

### Frontend Configuration

- **Port**: 3000 (default Next.js port)
- **API Endpoint**: Configured to connect to backend at `http://10.0.0.14:5001`
- **File Upload**: Drag-and-drop interface with multiple file support

## 📡 API Endpoints

### Backend API Routes

| Endpoint                      | Method | Description                      |
| ----------------------------- | ------ | -------------------------------- |
| `/api/analyze-receipt`        | POST   | Analyze multiple receipt images  |
| `/api/analyze-receipt-single` | POST   | Analyze single receipt image     |
| `/api/user/<username>`        | GET    | Retrieve user's analysis history |

### Request/Response Format

**POST /api/analyze-receipt**

```json
// Request (multipart/form-data)
{
  "files": ["receipt1.jpg", "receipt2.png"],
  "username": "Abhishek"
}

// Response
[
  {
    "sustainabilityScore": 45,
    "potentialMonthlySavings": 20,
    "summary": "This spending includes a mix of fresh produce...",
    "suggestions": [
      {
        "original": "Fast Fashion Item",
        "alternative": "Sustainable clothing option",
        "reasoning": "Environmental impact explanation"
      }
    ]
  }
]
```

## 🤖 AI Integration

### Google Gemini Integration

- **Model**: Gemini 2.5 Flash
- **Capabilities**: Multimodal analysis (text + image)
- **Analysis**: Receipt parsing, sustainability scoring, alternative suggestions
- **Output**: Structured JSON with actionable insights

### AI Prompt Engineering

The system uses carefully crafted prompts to:

- Extract purchase information from receipt images
- Calculate sustainability scores (1-100 scale)
- Generate specific, actionable alternatives
- Estimate potential monthly savings
- Provide environmental impact reasoning

## 🎨 User Interface

### Dashboard Features

- **File Upload**: Drag-and-drop interface with visual feedback
- **Analysis Display**: Clean, card-based layout for results
- **Score Visualization**: Large, prominent sustainability scores
- **Suggestions**: Organized list of eco-friendly alternatives
- **Error Handling**: User-friendly error messages

### Chat Interface

- **AI Assistant**: Interactive chatbot for sustainability advice
- **Real-time Messaging**: Smooth chat experience with typing indicators
- **Fallback Logic**: Mock responses when backend is unavailable

## 🔒 Security & Best Practices

- **File Validation**: Secure filename handling with Werkzeug
- **CORS Configuration**: Proper cross-origin resource sharing
- **Environment Variables**: API keys stored securely
- **Error Handling**: Comprehensive error catching and user feedback
- **Input Sanitization**: Safe handling of user inputs

## 🚀 Deployment

### Backend Deployment

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

### Frontend Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🧪 Testing

### Manual Testing

1. Upload sample receipt images
2. Verify AI analysis accuracy
3. Test chat functionality
4. Check responsive design on different devices

### Sample Data

The project includes sample receipt images in `ecowallet-backend/uploads/` for testing purposes.

## 🔮 Future Enhancements

- **User Authentication**: Secure user accounts and data persistence
- **Advanced Analytics**: Historical trends and sustainability insights
- **Social Features**: Community challenges and leaderboards
- **Mobile App**: Native iOS/Android applications
- **Integration**: Connect with banking APIs for automatic receipt processing
- **Gamification**: Points, badges, and sustainability achievements

## 📊 Technical Specifications

### Backend Dependencies

```
Flask==2.3.3
Flask-Cors==4.0.0
google-generativeai==0.3.2
python-dotenv==1.0.0
Werkzeug==2.3.7
```

### Frontend Dependencies

```
React 19.1.0
Next.js 15.5.4
TypeScript 5
Tailwind CSS 4
```

## 🤝 Contributing

This project was developed for the Human + AI One-Day Hackathon. For contributions or questions, please contact the team members.

## 📄 License

This project is developed for educational and hackathon purposes.

---

**Built with ❤️ for a more sustainable future** 🌍
