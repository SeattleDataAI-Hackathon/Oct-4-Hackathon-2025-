# BeyondBabyBlues AI Agent - Mistral Implementation

This is a Flask-based REST API that implements an intelligent **LangChain ReAct Agent** using Mistral AI for the BeyondBabyBlues pregnancy support system, specializing in **mental health and emotional well-being support** for expectant mothers with **automated appointment booking capabilities**.

## 🚀 Features

- **🤖 LangChain ReAct Agent**: Advanced reasoning and action planning with multi-tool integration
- **📅 Google Calendar Integration**: Automated appointment booking with OAuth2 authentication  
- **🧠 Mental Health Specialization**: Focused support for prenatal depression, anxiety, and emotional distress
- **🚨 Crisis Intervention**: Immediate support pathways for mental health emergencies with specialist matching
- **⚡ Mistral AI Integration**: Uses Mistral's large language model and embedding model for compassionate responses
- **🔍 RAG Implementation**: Combines document retrieval with generative AI for accurate mental health guidance
- **📊 FAISS Vector Store**: Efficient similarity search for mental health and pregnancy support content
- **👨‍⚕️ Specialist Database**: 8+ specialized healthcare providers with intelligent matching
- **🏥 HIPAA Compliant**: Maintains strict patient confidentiality standards
- **🌐 REST API**: Easy integration with chatbots and mental health support applications
- **🛠️ Multi-Tool Architecture**: Knowledge search, specialist matching, and appointment booking tools

## 📋 Prerequisites

- Python 3.8+
- Mistral AI API key
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd rag_medical-main
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements_mistral.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.mistral.example .env
   
   # Edit .env file and add your Mistral API key
   MISTRAL_API_KEY=your_actual_mistral_api_key_here
   ```

## 🔑 Getting Mistral API Key

1. Visit [Mistral AI Console](https://console.mistral.ai/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## 📁 Project Structure

```
rag_medical-main/
├── rag_medical_mistral.py      # Main Flask application (Mistral version)
├── faiss_lib_mistral.py        # Mistral-specific library functions
├── rag_medical.py              # Original Azure OpenAI version
├── faiss_lib.py                # Original Azure OpenAI library
├── requirements_mistral.txt    # Mistral implementation dependencies
├── .env.mistral.example        # Environment variables template
├── datasets/                   # Knowledge base files
│   ├── BeyondBabyBlues.txt
│   └── pregnancy.txt
└── medical_faiss_index_mistral/ # Mistral FAISS index (auto-generated)
```

## 🤖 Agent Architecture

The system uses a **LangChain ReAct (Reasoning and Acting) Agent** that can:

1. **Think**: Analyze user queries and determine appropriate actions
2. **Act**: Use tools to search knowledge base, match specialists, or book appointments  
3. **Observe**: Process tool results and plan next actions
4. **Respond**: Provide comprehensive answers with appropriate escalation

### Available Agent Tools

- **`knowledge_search`**: Searches the medical knowledge base using FAISS vector similarity
- **`book_appointment`**: Books appointments with specialists via Google Calendar API
- **`get_specialists`**: Retrieves available specialists based on consultation type

## 📅 Google Calendar Setup

For appointment booking functionality, you need to configure Google Calendar API:

1. **Follow the setup guide**: See `GOOGLE_CALENDAR_SETUP.md` for detailed instructions
2. **Verify setup**: Run `python verify_calendar_setup.py` to test the integration
3. **OAuth2 Authentication**: First run will prompt for Google account authorization

## 🧪 Testing the Agent

**Run comprehensive agent tests:**
```bash
python test_agent_mistral.py
```

This will test:
- Knowledge base search functionality
- Specialist consultation detection
- Appointment booking capabilities  
- Agent tool usage and selection
- ReAct reasoning patterns

## 🏃‍♂️ Running the Application

1. **Start the Flask server**
   ```bash
   python rag_medical_mistral.py
   ```

2. **Access the application**
   - **Chat Interface**: `http://localhost:5000` (main web interface)
   - **API Base URL**: `http://localhost:5000`
   - **Swagger Documentation**: `http://localhost:5000/swagger`

## 📡 API Usage

### Query Endpoint

**POST** `/query`

**Request Body:**
```json
{
    "query": "What services does BeyondBabyBlues offer for pregnant women?"
}
```

**Response:**
```json
{
    "role": "assistant",
    "content": "<HTML formatted response>",
    "sources": [
        {
            "index": 1,
            "page_content": "Source document content...",
            "metadata": {
                "source": "./datasets/BeyondBabyBlues.txt"
            }
        }
    ]
}
```

### Example cURL Requests

**General Support Query:**
```bash
curl -X POST "http://localhost:5000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What services does BeyondBabyBlues offer?"}'
```

**Mental Health Support Query:**
```bash
curl -X POST "http://localhost:5000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "I am feeling very anxious about my pregnancy and having trouble sleeping. Can you help?"}'
```

**Crisis Support Query:**
```bash
curl -X POST "http://localhost:5000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "I am having thoughts of harming myself. I need help."}'
```

## 🧠 Mental Health Support Capabilities

### Core Mental Health Features

- **Prenatal Depression Support**: Recognition of symptoms including persistent sadness, mood swings, sleep issues, and loss of interest
- **Anxiety Disorder Assistance**: Help with excessive worry, panic attacks, and pregnancy-related fears
- **Crisis Intervention**: Immediate support pathways for severe distress and suicidal thoughts
- **Emotional Validation**: Non-judgmental support that normalizes pregnancy emotional challenges
- **Professional Referrals**: Connections to appropriate mental health services and support groups
- **Coping Strategies**: Practical emotional support resources and techniques

### Mental Health Response Types

1. **Supportive Responses**: Validation and emotional support for common pregnancy concerns
2. **Educational Guidance**: Information about prenatal mental health conditions
3. **Crisis Intervention**: Immediate safety resources and emergency contacts
4. **Professional Referrals**: Directing users to appropriate mental health professionals
5. **Resource Sharing**: Support groups, counseling services, and self-help tools

### Safety & Crisis Support

- **Crisis Hotline**: 988 (Suicide & Crisis Lifeline)
- **Emergency Services**: 911 for immediate danger
- **24/7 Support**: Available emotional support and guidance
- **Professional Network**: Direct connections to licensed mental health professionals

## 🔧 Configuration

### Mistral Models Used

- **LLM Model**: `mistral-large-latest` - For generating compassionate, mental health-focused responses
- **Embedding Model**: `mistral-embed` - For document embeddings and mental health content retrieval

### Mental Health Support Contact System

The API provides comprehensive contact information for different types of support:

- **Mental Health Crisis**: 988 (Suicide & Crisis Lifeline) or 911
- **Counseling & Therapy**: counseling@BeyondBabyBlues.com
- **Support Groups**: support@BeyondBabyBlues.com
- **Medical Team**: medical@BeyondBabyBlues.com
- **General Information**: info@BeyondBabyBlues.com
- **24/7 Helpline**: Available for emotional support and guidance

### Customizable Parameters

In `faiss_lib_mistral.py`, you can adjust:

- **Chunk Size**: Default 512 characters
- **Chunk Overlap**: Default 50 characters
- **Temperature**: Default 0.1 (for empathetic and consistent responses)
- **Max Tokens**: Default 1000

## 📊 Performance Considerations

- **FAISS Index**: Automatically created and cached for faster subsequent queries
- **Batch Processing**: Handles large documents in batches of 500 chunks
- **Index Updates**: Smart indexing that only updates when source files change

## 🔒 Security Features

- Token-based authentication (configurable)
- CORS enabled for web integration
- Environment variable protection for API keys

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: MISTRAL_API_KEY not found in environment variables
   ```
   Solution: Ensure your `.env` file contains the correct API key

2. **Import Errors**
   ```
   Import "langchain_mistralai" could not be resolved
   ```
   Solution: Install requirements: `pip install -r requirements_mistral.txt`

3. **FAISS Index Issues**
   - Delete the `medical_faiss_index_mistral` folder to force recreation
   - Check file permissions in the project directory

4. **Mental Health Response Quality**
   - Ensure your dataset includes comprehensive mental health information
   - Check that the BeyondBabyBlues.txt file contains relevant mental health resources
   - Verify the prompt template is properly formatted for empathetic responses

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

### Mental Health Content Verification

To ensure proper mental health support responses:
1. Verify the `datasets/BeyondBabyBlues.txt` file contains mental health resources
2. Test crisis intervention responses with sample queries
3. Check that contact information is current and accessible
4. Validate that professional referral pathways are working correctly

## 🔄 Migration from Azure OpenAI

The main differences between the Azure OpenAI and Mistral implementations:

| Component | Azure OpenAI | Mistral |
|-----------|--------------|---------|
| LLM | `AzureChatOpenAI` | `ChatMistralAI` |
| Embeddings | `AzureOpenAIEmbeddings` | `MistralAIEmbeddings` |
| Authentication | Azure AD Token | API Key |
| Index Path | `medical_faiss_index` | `medical_faiss_index_mistral` |

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

### Technical Support
For technical issues and questions:
- Create an issue in the repository
- Check the troubleshooting section above
- Review the Swagger documentation at `/swagger`

### Mental Health Resources
If you or someone you know needs immediate mental health support:
- **Crisis Hotline**: 988 (Suicide & Crisis Lifeline)
- **Emergency**: 911
- **National Pregnancy Support**: 1-800-672-2296
- **Postpartum Support International**: 1-944-4-WARMLINE

### Professional Mental Health Services
The BeyondBabyBlues API is designed to provide supportive information and connect users with professional help. It is not a substitute for professional mental health treatment, therapy, or medical care. Always consult with qualified healthcare providers for serious mental health concerns.