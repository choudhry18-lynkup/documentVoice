# HVAC Voice Agent with LiveKit

A real-time voice agent for HVAC servicing that uses OpenAI's LLM with PDF manual context. Built with LiveKit for voice processing and OpenAI for intelligent responses.

## Features

- 🎤 **Real-time Voice Interaction**: LiveKit-powered voice agent with speech-to-text and text-to-speech
- 📚 **Document Context**: Loads up to 2 PDF HVAC manuals into the LLM context window
- 🤖 **OpenAI Integration**: Uses GPT-4o (or configurable model) for intelligent responses
- 🔧 **HVAC-Specific**: Tailored system prompts for HVAC service and repair guidance
- 💬 **Conversational**: Maintains conversation history for context-aware responses

## Architecture

### Components

1. **Document Processor** (`document_processor.py`)
   - Extracts text from PDF manuals
   - Manages document caching
   - Handles context window truncation

2. **LLM Service** (`llm_service.py`)
   - OpenAI API integration
   - Manages system prompts with document context
   - Handles conversation history

3. **Voice Agent** (`voice_agent.py`)
   - LiveKit voice pipeline integration
   - Real-time transcription and TTS
   - Connects user speech to LLM responses

4. **Main Entry Point** (`main.py`)
   - Environment validation
   - Application startup

## Setup

### Prerequisites

- Python 3.9 or higher
- LiveKit server (cloud or self-hosted)
- OpenAI API key
- PDF HVAC manuals

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd Document_Voice
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in:
   - `LIVEKIT_URL`: Your LiveKit server WebSocket URL (e.g., `wss://your-project.livekit.cloud` for LiveKit Cloud)
   - `LIVEKIT_API_KEY`: Your LiveKit API key
   - `LIVEKIT_API_SECRET`: Your LiveKit API secret
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `OPENAI_MODEL`: Model to use (default: `gpt-4o`)
   
   **For LiveKit Cloud**: Get your credentials from https://cloud.livekit.io → Project Settings → API Keys

5. **Add PDF manuals:**
   ```bash
   mkdir documents
   # Copy your HVAC PDF manuals into the documents/ directory
   cp /path/to/manual1.pdf documents/
   cp /path/to/manual2.pdf documents/
   ```

## Usage

### Development Mode

Run the agent in development mode:

```bash
python main.py dev
```

Or directly:

```bash
python -m voice_agent dev
```

### Production Deployment

For production, you'll need to:
1. Deploy to a server with LiveKit agent support
2. Configure the agent as a LiveKit service
3. Set up proper logging and monitoring

## How It Works

1. **Document Loading**: On startup, the agent loads up to 2 PDF files from the `documents/` directory
2. **Text Extraction**: PDFs are processed to extract all text content
3. **Context Preparation**: Document text is truncated to fit within the LLM's context window (reserving space for prompts and responses)
4. **Voice Processing**: 
   - User speaks → LiveKit transcribes speech to text
   - Text is sent to OpenAI LLM with document context
   - LLM generates response based on manuals
   - Response is converted to speech via TTS
5. **Conversation**: The agent maintains conversation history for context-aware follow-up questions

## Configuration

### Model Selection

The default model is `gpt-4o` which has a 128K token context window. You can change this in `.env`:

```
OPENAI_MODEL=gpt-4-turbo  # or gpt-4, gpt-3.5-turbo, etc.
```

### Document Limits

- Maximum 2 documents are loaded (newest first by modification time)
- Documents are automatically truncated to fit the model's context window
- Reserved tokens: ~3000 tokens for system prompt, conversation, and responses

### Voice Settings

Voice settings can be modified in `voice_agent.py`:
- TTS voice: Change `voice="alloy"` to other OpenAI voices (alloy, echo, fable, onyx, nova, shimmer)
- STT model: Uses OpenAI Whisper by default
- VAD (Voice Activity Detection): Uses LiveKit's built-in VAD

## Troubleshooting

### No Documents Loaded
- Ensure PDF files are in the `documents/` directory
- Check file permissions
- Verify PDFs are not corrupted

### API Errors
- Verify API keys are correct in `.env`
- Check OpenAI API quota/limits
- Ensure LiveKit server is accessible

### Context Window Issues
- If documents are too large, they'll be automatically truncated
- Consider using a model with larger context (gpt-4o: 128K tokens)
- Reduce number of documents or use document chunking

## Deployment

This agent works with both **LiveKit Cloud** and self-hosted LiveKit servers.

### LiveKit Cloud (Recommended)

✅ **Fully compatible!** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

Quick setup:
1. Get credentials from https://cloud.livekit.io
2. Set `LIVEKIT_URL` to your Cloud project URL (e.g., `wss://project.livekit.cloud`)
3. Deploy agent (see DEPLOYMENT.md for options)

### Self-Hosted

Works with any LiveKit server. Just point `LIVEKIT_URL` to your server.

## Project Structure

```
Document_Voice/
├── documents/              # Place PDF manuals here
├── .env                    # Environment variables (create manually)
├── .gitignore
├── requirements.txt        # Python dependencies
├── document_processor.py   # PDF text extraction
├── llm_service.py         # OpenAI LLM integration
├── voice_agent.py         # LiveKit voice agent
├── main.py                # Application entry point
├── test_documents.py      # Test document loading
├── setup.sh               # Setup script
├── README.md              # This file
├── ARCHITECTURE.md        # Architecture documentation
└── DEPLOYMENT.md          # Deployment guide (including LiveKit Cloud)
```

## Design Choices Explained

### Why LiveKit?
- **Real-time Processing**: LiveKit provides low-latency voice processing
- **Built-in STT/TTS**: Integrated speech-to-text and text-to-speech pipelines
- **Scalable**: Designed for production voice applications
- **Python SDK**: Easy integration with Python ecosystem

### Why Full Document Context (not RAG)?
- **Simplicity**: Easier to implement and debug
- **Context Awareness**: LLM sees full document structure and relationships
- **No Vector DB**: Reduces infrastructure complexity
- **Modern Models**: GPT-4o's 128K context window can handle large documents

### Why OpenAI?
- **High Quality**: Excellent for technical documentation understanding
- **Large Context**: GPT-4o supports 128K tokens
- **Reliable API**: Production-ready with good uptime
- **Voice Integration**: Native STT/TTS support

## License

MIT License - feel free to use and modify for your HVAC service needs.

## Support

For issues or questions:
1. Check LiveKit documentation: https://docs.livekit.io/
2. Check OpenAI API documentation: https://platform.openai.com/docs
3. Review logs for error messages

