# CarePath - AI Medical Triage Assistant

**Modern AI-powered medical triage assistant with intelligent symptom analysis and specialist recommendations**

---

## Overview

CarePath is an intelligent medical triage assistant that helps users understand their symptoms and guides them to appropriate medical care. Built with React, FastAPI, and OpenAI's GPT-4, it provides a conversational interface similar to ChatGPT for healthcare guidance.

### Key Highlights

- AI-Powered Diagnosis using GPT-4 for intelligent symptom analysis
- Conversational Interface with natural chat experience
- Smart Triage categorizing urgency: Emergency / Urgent Care / Normal
- Specialist Recommendations suggesting appropriate doctors based on diagnosis
- Comprehensive database of 101+ physical and mental health conditions
- One-Command Start with automated setup

---

## Features

### User Experience
- **Dual Start Options**: Choose from common symptoms list or chat freely
- **Smart Diagnosis Button**: Appears after 3 follow-up questions
- **Auto-Diagnosis**: Triggers automatically at 90%+ confidence
- **Medical Disclaimer**: Prominent warning with every assessment
- **Responsive Design**: Works seamlessly on desktop and mobile

### Technical Features
- **Modern Stack**: React + TypeScript + Tailwind CSS + shadcn/ui
- **FastAPI Backend**: High-performance Python API
- **Secure API Key Storage**: Local configuration with dialog prompt
- **Auto-scroll Chat**: Smooth conversation experience
- **Keyboard Shortcuts**: Shift+Enter for new lines, auto-focus on typing

---

## Quick Start

### Prerequisites

- Python 3.8 or higher ([Download](https://www.python.org/downloads/))
- Node.js 18 or higher ([Download](https://nodejs.org/))
- OpenAI API Key ([Get yours here](https://platform.openai.com/api-keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Oct-4-Hackathon-2025-
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   cd carepath-ui
   npm install
   cd ..
   ```

### Running CarePath

#### Windows
```bash
start.bat
```

#### Mac/Linux
```bash
chmod +x start.sh
./start.sh
```

**What happens:**
- Backend server starts on `http://localhost:8000`
- Frontend app starts on `http://localhost:5173`
- Two terminal windows open
- Browser opens automatically (or manually navigate to http://localhost:5173)

**First Run:**
- API Key dialog appears
- Enter your OpenAI API key (starts with `sk-...`)
- Key is saved locally in `config.py`
- Application is ready to use

### Alternative: Manual Start

**Terminal 1 - Backend:**
```bash
python backend.py
```

**Terminal 2 - Frontend:**
```bash
cd carepath-ui
npm run dev
```

Then open: **http://localhost:5173**

---

## How It Works

### 1. Choose Your Approach

**Option A: Select Symptoms**
- Pick from 18 common symptoms (Headache, Fever, Cough, etc.)
- Add custom symptoms in text field
- Automatically starts conversation with selected symptoms

**Option B: Start Chat**
- Type symptoms freely in conversation
- Natural language understanding
- Follow-up questions adapt to your responses

### 2. Conversational Flow

```
User: I have a severe headache and chest pain
↓
CarePath: How long have you been experiencing these symptoms?
↓
User: About 2 days, and I feel dizzy
↓
CarePath: How severe is the chest pain on a scale of 1-10?
↓
[After 3 exchanges, "Ready for Diagnosis" button appears]
```

### 3. Smart Diagnosis

**Manual Trigger:** Click "Ready for Diagnosis" button after 3+ exchanges

**Auto Trigger:** Diagnosis happens automatically if confidence reaches or exceeds 90%

### 4. Assessment Results

Displays:
- **Possible Condition**: Most likely diagnosis
- **Confidence Level**: Match percentage
- **Urgency Level**: Emergency / Urgent Care / Normal
- **Recommended Specialist**: Which doctor to see
- **Other Possibilities**: Alternative diagnoses
- **Medical Disclaimer**: Important notice

---

## Technology Stack

### Frontend
- React 18 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- shadcn/ui - Component library
- Axios - HTTP client
- Lucide React - Icons

### Backend
- FastAPI - Web framework
- Python 3.8+ - Programming language
- OpenAI GPT-4 - AI model
- Pandas - Data processing
- Uvicorn - ASGI server

### Data
- 101 Disorders in comprehensive CSV database
- 60+ Physical conditions
- 40+ Mental health conditions
- Symptom mappings, specialists, and risk factors

---

## Project Structure

```
Oct-4-Hackathon-2025-/
├── backend.py                          # FastAPI server
├── carepath.py                         # CLI version (legacy)
├── config.py                           # API key (auto-generated, gitignored)
├── config.example.py                   # Template for config
├── common_disorders_dataset_full.csv   # Disorder database
├── requirements.txt                    # Python dependencies
├── start.bat                           # Windows launcher
├── start.sh                            # Mac/Linux launcher
├── README.md                           # This file
└── carepath-ui/                        # React frontend
    ├── src/
    │   ├── components/
    │   │   ├── ChatInterface.tsx       # Main chat UI
    │   │   ├── ApiKeyDialog.tsx        # API key prompt
    │   │   └── ui/                     # shadcn components
    │   ├── App.tsx                     # App entry point
    │   ├── main.tsx                    # React entry
    │   └── index.css                   # Global styles
    ├── package.json
    └── vite.config.ts
```

---

## Configuration

### API Key Setup

**Automatic (Recommended):**
1. Run the application
2. Enter API key when prompted
3. Key saved to `config.py`

**Manual:**
```bash
# Copy template
copy config.example.py config.py

# Edit config.py and add your key
OPENAI_API_KEY = "sk-your-key-here"
```

### Environment Variables (Optional)

```bash
# Alternative to config.py
export OPENAI_API_KEY="sk-your-key-here"
```

---

## User Interface Features

### Chat Experience
- **Auto-focus**: Start typing without clicking input
- **Shift+Enter**: Add new lines in messages
- **Enter**: Send message
- **Sticky Input**: Input box stays visible while scrolling
- **Auto-scroll**: Automatically scrolls to latest message
- **Loading Animation**: Typing indicator

### Visual Design
- **Blue Gradient Welcome**: First message highlighted
- **Color-coded Urgency**: Red (Emergency), Orange (Urgent), Green (Normal)
- **Responsive Layout**: Centered chat container
- **Dark Mode Support**: Built-in theme support
- **Professional UI**: shadcn/ui components

---

## Security and Privacy

- API key stored locally in `config.py`
- `config.py` in `.gitignore` - never committed to version control
- No data sent to external servers except OpenAI API
- No user data stored or logged
- All processing happens locally

---

## Disclaimer

**IMPORTANT MEDICAL DISCLAIMER**

CarePath is an AI-powered informational tool and is NOT a substitute for professional medical advice, diagnosis, or treatment.

This application:
- Is NOT a licensed medical professional
- Is NOT for emergency situations - Call 911 immediately for emergencies
- Is NOT for medical diagnosis - Consult qualified healthcare providers
- Is for educational purposes only
- Serves as a guidance tool to help understand when to seek care

**Always consult with qualified healthcare professionals for medical decisions.**

---

## Troubleshooting

### Backend Issues

**Error: Module not found**
```bash
pip install -r requirements.txt
```

**Error: config.py not found**
- Delete any existing `config.py`
- Restart app - API key dialog will appear

**Error: OpenAI API error**
- Check your API key is valid
- Verify you have credits at https://platform.openai.com/usage

### Frontend Issues

**Error: npm install fails**
```bash
cd carepath-ui
rm -rf node_modules package-lock.json
npm install
```

**Error: Port 5173 already in use**
- Close other Vite instances
- Or change port in `vite.config.ts`

**Error: Cannot connect to backend**
- Ensure backend is running on port 8000
- Check CORS settings in `backend.py`

### Common Issues

**Windows: start.bat doesn't work**
- Right-click and select "Run as Administrator"
- Check Python/Node in PATH: `python --version`, `node --version`

**Mac/Linux: Permission denied**
```bash
chmod +x start.sh
./start.sh
```

---

## Development

### Running in Development Mode

**Backend with auto-reload:**
```bash
uvicorn backend:app --reload
```

**Frontend with hot-reload:**
```bash
cd carepath-ui
npm run dev
```

### Building for Production

**Frontend:**
```bash
cd carepath-ui
npm run build
```

Output in `carepath-ui/dist/`

### API Endpoints

- `GET /` - Health check
- `GET /check-api-key` - Check if API key configured
- `POST /set-api-key` - Save API key to config
- `POST /chat` - Send chat message
- `POST /diagnose` - Get diagnosis based on conversation

---

## Contributing

Contributions are welcome. Please feel free to submit issues or pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Team

**Team 30** - Healthcare Hackathon 2025

---

## Acknowledgments

- OpenAI for GPT-4 API
- shadcn/ui for component library
- FastAPI for Python web framework
- React team for frontend library

---

## Support

For issues, questions, or feedback:
- Open an issue on GitHub
- Review the troubleshooting section above

---

**CarePath - Guiding You to Better Health**

Built for Healthcare Hackathon 2025
