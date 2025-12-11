# Health Symptom Portal

An AI-powered medical symptom analysis portal that integrates with Ollama's qwen3:30b model to provide preliminary medical assessments. This system features an interactive body diagram, symptom tracking, real-time AI analysis, and a doctor review workflow.

## Features

- 🏥 **Interactive Body Diagram**: Click on anatomical areas to select affected regions
- 📝 **Detailed Symptom Input**: Track symptom type, duration, severity, and location  
- 🤖 **Real AI Analysis**: Integration with Ollama qwen3:30b for medical assessments
- ⏱️ **Progress Tracking**: Visual progress bar with 2.5-minute countdown timer
- 👨‍⚕️ **Doctor Review Portal**: Medical professionals can review and approve AI suggestions
- 📊 **Patient History**: Complete tracking of all consultations and outcomes
- 🔒 **Medical Disclaimers**: Appropriate warnings that this is preliminary assessment only

## Prerequisites

- **Ollama**: Local AI model server
- **Modern Web Browser**: Chrome, Firefox, Safari, or Edge
- **8GB+ RAM**: Recommended for qwen3:30b model

## Installation & Setup

### 1. Install Ollama

#### macOS/Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows:
Download from [ollama.ai](https://ollama.ai) and run the installer.

### 2. Download the AI Model

```bash
# Download the qwen3:30b model (this may take some time)
ollama pull qwen3:30b

# Verify the model is installed
ollama list
```

### 3. Start Ollama Server

```bash
ollama serve
```

The server will start on `http://localhost:11434`. Keep this terminal window open while using the portal.

### 4. Launch the Health Portal

Simply open `health_symptom_portal.html` in your web browser:

```bash
# Option 1: Direct file opening
open health_symptom_portal.html

# Option 2: Using a local server (recommended)
python3 -m http.server 8000
# Then visit: http://localhost:8000/health_symptom_portal.html
```

## Usage Guide

### For Patients

1. **Enter Your Name**: Fill in the patient name field
2. **Select Body Area**: Click on the interactive body diagram to highlight affected areas
3. **Describe Symptoms**: Choose symptom type, duration, and severity (1-10 scale)
4. **Add Multiple Symptoms**: Repeat steps 2-3 for additional symptoms
5. **Submit for Analysis**: Click "Submit to AI Analysis" button
6. **Wait for Results**: Progress bar shows estimated 2.5-minute analysis time
7. **Review Assessment**: Read the AI-generated preliminary medical assessment

### For Medical Professionals

1. **Switch to Doctor Portal**: Click the "Doctor Portal" tab
2. **Enter Your Name**: Provide your professional credentials
3. **Review Pending Cases**: See all submitted patient cases awaiting review
4. **Add Professional Notes**: Include your assessment and any modifications
5. **Approve or Reject**: Approve suitable cases or reject inappropriate submissions
6. **Track History**: View all completed consultations in the History tab

## System Architecture

### AI Integration
- **Model**: Ollama qwen3:30b (30 billion parameter medical AI)
- **API Endpoint**: `http://localhost:11434/api/generate`
- **Response Time**: ~2.5 minutes average
- **Temperature**: 0.7 (balanced accuracy/creativity)
- **Top-p**: 0.9 (high-quality responses)

### Data Flow
1. Patient inputs symptoms via web interface
2. System creates structured medical prompt
3. Ollama API processes request with qwen3:30b model
4. AI response is filtered (removes thinking tags)
5. Results displayed with medical disclaimers
6. Doctor reviews and approves/modifies assessment
7. Final recommendations stored in patient history

## Troubleshooting

### "Unable to connect to Ollama AI model"

**Check Ollama Status:**
```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve
```

**Verify Model Installation:**
```bash
ollama list | grep qwen3
```

**Test API Connection:**
```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3:30b","prompt":"Test","stream":false}'
```

### Slow Response Times

**Options to improve speed:**

1. **Use a smaller model:**
   ```bash
   ollama pull qwen2:7b
   # Then update the model name in the HTML file
   ```

2. **Check system resources:**
   ```bash
   # Monitor CPU/RAM usage
   ollama ps
   ```

3. **GPU Acceleration** (if available):
   Ollama automatically uses GPU when available, significantly improving speed.

### CORS Issues

If accessing from `file://` protocol, use a local web server instead:

```bash
# Python
python3 -m http.server 8000

# Node.js
npx http-server

# PHP
php -S localhost:8000
```

## Security & Privacy

⚠️ **Important Medical Disclaimers:**

- This system provides **preliminary assessments only**
- **NOT a substitute** for professional medical diagnosis
- **Always consult** qualified healthcare providers
- **Seek emergency care** for severe or worsening symptoms
- AI suggestions should be **reviewed by medical professionals**

🔒 **Data Privacy:**

- All data stored locally in browser memory
- No data transmitted to external servers
- Ollama runs entirely on your local machine
- No patient data leaves your system

## Model Information

**qwen3:30b Specifications:**
- **Parameters**: 30.5 billion
- **Family**: Qwen3 MoE (Mixture of Experts)
- **Quantization**: Q4_K_M (balanced speed/quality)
- **Size**: ~18.6 GB
- **Specialization**: General knowledge including medical domains

## Alternative Models

For faster responses, consider these alternatives:

```bash
# Faster but less detailed
ollama pull qwen2:7b        # ~7B parameters
ollama pull llama3:8b       # ~8B parameters  
ollama pull deepseek-coder  # ~1B parameters (very fast)
```

Update the model name in `health_symptom_portal.html` line 706.

## Contributing

To modify or enhance the portal:

1. **Edit HTML/CSS/JavaScript** in `health_symptom_portal.html`
2. **Test with different models** by changing the model name
3. **Adjust prompts** to improve AI response quality
4. **Add new symptom types** in the dropdown options
5. **Enhance UI/UX** with additional styling or features

## Support

For issues related to:
- **Ollama**: Check [Ollama documentation](https://ollama.ai)
- **Model performance**: Try different models or adjust parameters
- **Web interface**: Inspect browser console for JavaScript errors
- **Medical accuracy**: Always consult healthcare professionals

---

**⚕️ Medical Disclaimer**: This tool is for educational and preliminary assessment purposes only. It does not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical concerns.