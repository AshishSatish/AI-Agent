# Company Research Assistant - Account Plan Generator

An AI-powered interactive assistant that helps research companies and generate comprehensive account plans through natural conversation. Supports both chat and voice interaction modes.

## Features

- **Conversational AI**: Natural language interaction using Groq API
- **Multi-Source Research**: Gathers information from web search (SerpAPI)
- **Intelligent Synthesis**: Consolidates findings from multiple sources
- **Conflict Detection**: Identifies contradicting information and alerts users
- **Account Plan Generation**: Creates structured account plans automatically
- **Interactive Updates**: Allows editing specific sections of account plans
- **Dual Interface**: Web-based chat and voice interaction modes
- **Real-time Updates**: WebSocket support for live research progress
- **Persistent Storage**: Saves account plans for future reference

## Architecture

```
company-research-assistant/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI web application
│   ├── agent.py              # Conversational agent (Groq integration)
│   ├── researcher.py         # Multi-source research orchestrator
│   ├── synthesizer.py        # Data synthesis engine
│   ├── account_plan.py       # Account plan generator
│   ├── voice.py              # Voice interaction module
│   └── config.py             # Configuration management
├── templates/
│   └── index.html            # Web UI
├── static/                   # Static assets
├── data/                     # Saved account plans
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── run.py                    # Application entry point
└── README.md                 # This file
```

## Prerequisites

- Python 3.8 or higher
- Groq API key ([Get one here](https://console.groq.com))
- SerpAPI key ([Get one here](https://serpapi.com))

## Installation

### 1. Clone or Download the Project

Navigate to the project directory:
```bash
cd "C:\Users\ashis\OneDrive\Desktop\AI Agent"
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note for PyAudio (Voice Mode):**
- **Windows**: PyAudio may require additional installation steps. If you encounter errors:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
- **macOS**: Install PortAudio first:
  ```bash
  brew install portaudio
  pip install pyaudio
  ```
- **Linux**: Install dependencies:
  ```bash
  sudo apt-get install python3-pyaudio portaudio19-dev
  pip install pyaudio
  ```

### 4. Configure Environment Variables

Copy the example environment file:
```bash
copy .env.example .env     # Windows
cp .env.example .env       # macOS/Linux
```

Edit `.env` and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_KEY=your_serpapi_key_here

# Optional settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
GROQ_MODEL=mixtral-8x7b-32768
MAX_RESEARCH_SOURCES=5
```

## Usage

### Web Mode (Default)

Start the web application:
```bash
python run.py --mode web
```

Or simply:
```bash
python run.py
```

Then open your browser to: **http://localhost:8000**

### Voice Mode

Start voice interaction mode:
```bash
python run.py --mode voice
```

Speak naturally to the assistant. Say "exit", "quit", or "goodbye" to end the session.

## Using the Application

### Web Interface

1. **Chat**: Type messages in the input box to converse with the assistant
2. **Quick Research**: Click "Quick Research" and enter a company name
3. **Generate Plan**: After research, click "Generate Plan" to create an account plan
4. **Update Sections**: Use the update form to modify specific plan sections
5. **View Plans**: Click "View Plans" to see all saved account plans
6. **Voice Input**: Click the microphone button for voice input (Chrome/Edge only)

### Example Workflow

1. **Start Research**:
   ```
   User: "Tell me about Microsoft"
   Assistant: "I'll research Microsoft for you..."
   ```

2. **Review Findings**:
   - Research summary appears in the left panel
   - Conflicts (if any) are highlighted

3. **Generate Account Plan**:
   ```
   User: "Generate an account plan"
   Assistant: "Creating account plan..."
   ```

4. **Update Sections**:
   - Section path: `executive_summary`
   - New content: Your updated content
   - Click "Update"

5. **Save and Export**:
   - Plans are automatically saved to the `data/` folder
   - Accessible via "View Plans"

## API Endpoints

### Chat
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Tell me about Tesla",
  "session_id": "optional_session_id"
}
```

### Research Company
```http
POST /api/research
Content-Type: application/json

{
  "company_name": "Tesla",
  "session_id": "optional_session_id"
}
```

### Generate Account Plan
```http
POST /api/generate-plan
Content-Type: application/json

{
  "company_name": "Tesla",
  "session_id": "optional_session_id"
}
```

### Update Plan Section
```http
POST /api/update-plan
Content-Type: application/json

{
  "section_path": "executive_summary",
  "new_content": "Updated content here",
  "session_id": "optional_session_id"
}
```

### List Plans
```http
GET /api/plans
```

### Get Specific Plan
```http
GET /api/plans/{filename}
```

## WebSocket Support

Connect to WebSocket for real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session_id');

ws.send(JSON.stringify({
  action: 'research',
  company_name: 'Tesla'
}));

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

## Account Plan Structure

Generated account plans include:
- **Executive Summary**: High-level overview
- **Company Background**: Overview, size, industry, location
- **Products & Services**: Offerings and differentiators
- **Market Analysis**: Position, competitors, trends
- **Key Stakeholders**: Decision makers and influencers
- **Opportunity Assessment**: Needs, pain points, opportunities
- **Engagement Strategy**: Approach, value proposition, next steps
- **Risks & Challenges**: Potential obstacles
- **Success Metrics**: KPIs and measurement criteria

## Customization

### Change AI Model

Edit `.env`:
```env
GROQ_MODEL=llama2-70b-4096  # or another supported model
```

### Adjust Research Depth

Edit `.env`:
```env
MAX_RESEARCH_SOURCES=10  # Increase for more comprehensive research
```

### Modify System Prompt

Edit `app/agent.py`, update the `system_prompt` in `ConversationalAgent.__init__()`.

## Troubleshooting

### "No module named 'app'"
- Make sure you're in the project directory
- Ensure the virtual environment is activated

### "API key not found"
- Check that `.env` file exists and contains valid API keys
- Restart the application after updating `.env`

### Voice mode not working
- Install PyAudio dependencies (see installation section)
- Check microphone permissions
- Try a different browser for web-based voice input

### Research returns no results
- Verify SerpAPI key is valid and has remaining credits
- Check internet connection
- Try a different company name

## Development

### Run in Debug Mode
```bash
# Already enabled in .env by default
DEBUG=True
```

### Add New Research Sources

Edit `app/researcher.py` and add methods to the `CompanyResearcher` class.

### Customize Account Plan Template

Edit `app/account_plan.py`, modify the `generate_plan()` method's prompt.

## Cost Considerations

- **Groq API**: Generally free tier available, check current limits
- **SerpAPI**: Free tier includes 100 searches/month
- Monitor your API usage in respective dashboards

## Security Notes

- Never commit `.env` file to version control
- Keep API keys confidential
- Use environment variables for sensitive data
- Consider rate limiting for production deployments

## Future Enhancements

Potential additions:
- Integration with company databases (Crunchbase, LinkedIn)
- Export plans to PDF/Word
- Email integration for sending plans
- Multi-user support with authentication
- Advanced analytics and visualizations
- Custom plan templates
- Integration with CRM systems

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation (Groq, SerpAPI)
3. Ensure all dependencies are installed correctly

## License

This project is provided as-is for educational and commercial use.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI powered by [Groq](https://groq.com/)
- Search powered by [SerpAPI](https://serpapi.com/)
- Voice capabilities via [SpeechRecognition](https://github.com/Uberi/speech_recognition) and [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
