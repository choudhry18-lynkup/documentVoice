# Architecture & Design Choices

This document explains the architectural decisions and design choices made in building the HVAC Voice Agent.

## High-Level Architecture

```
User Voice Input
    ↓
LiveKit Voice Pipeline
    ↓
[STT] → Transcription → [LLM] → Response → [TTS] → Voice Output
         (OpenAI)      (OpenAI)            (OpenAI)
                          ↑
                    Document Context
                    (PDF Manuals)
```

## Component Breakdown

### 1. Document Processor (`document_processor.py`)

**Purpose**: Extract and prepare PDF content for LLM context window.

**Key Design Decisions**:
- **PyPDF2 for PDF extraction**: Simple, reliable library for text extraction
- **Caching**: Documents are cached in memory to avoid re-reading on each request
- **Token estimation**: Uses rough 4:1 character-to-token ratio (OpenAI's approximation)
- **Smart truncation**: Truncates at sentence boundaries when possible to preserve context

**Why this approach?**
- Full document context (not RAG) provides better understanding of document structure
- Modern models (GPT-4o) have 128K token context windows, sufficient for most manuals
- Simpler than vector databases - no additional infrastructure needed

### 2. LLM Service (`llm_service.py`)

**Purpose**: Manage OpenAI API interactions and system prompt creation.

**Key Design Decisions**:
- **System prompt engineering**: Creates detailed HVAC-specific prompts with document context
- **Conversation history**: Maintains last 10 messages for context-aware responses
- **Model flexibility**: Supports different OpenAI models (configurable via env var)
- **Error handling**: Graceful error messages if API calls fail

**Why this approach?**
- Centralized LLM logic makes it easy to switch providers or models
- System prompt includes safety instructions and HVAC-specific guidance
- Conversation history enables follow-up questions

### 3. Voice Agent (`voice_agent.py`)

**Purpose**: LiveKit integration for real-time voice processing.

**Key Design Decisions**:
- **VoicePipelineAgent**: Uses LiveKit's built-in voice pipeline for simplicity
- **OpenAI plugins**: Uses LiveKit's OpenAI STT, LLM, and TTS plugins
- **System prompt injection**: Injects document context via system prompt in chat context
- **Automatic conversation management**: LiveKit handles turn-taking and audio processing

**Why this approach?**
- **LiveKit's VoicePipelineAgent**: Handles complex audio processing automatically
  - Voice Activity Detection (VAD)
  - Speech-to-text streaming
  - Turn-taking logic
  - Text-to-speech synthesis
- **System prompt with documents**: Simpler than custom LLM wrapper
  - Documents are included in the system prompt
  - LLM sees full document context on every request
  - No need for complex RAG retrieval logic
- **OpenAI integration**: Native support for OpenAI's Whisper (STT) and TTS models

### 4. Main Entry Point (`main.py`)

**Purpose**: Application startup and environment validation.

**Key Design Decisions**:
- **Environment validation**: Checks for required API keys before starting
- **Dotenv support**: Easy configuration via `.env` file
- **Clear error messages**: Guides users to fix configuration issues

## Design Choices Explained

### Why LiveKit?

1. **Real-time Processing**: Built for low-latency voice applications
2. **Production-Ready**: Handles audio streaming, network issues, reconnection
3. **Python SDK**: Easy integration with Python ecosystem
4. **Built-in Components**: VAD, STT, TTS all integrated
5. **Scalable**: Can handle multiple concurrent sessions

### Why Full Document Context (Not RAG)?

**Advantages**:
- **Simplicity**: No vector database needed
- **Full Context**: LLM sees entire document structure and relationships
- **No Retrieval Errors**: Can't miss relevant information
- **Modern Models**: GPT-4o's 128K context window handles large documents

**Trade-offs**:
- **Token Usage**: Uses more tokens per request
- **Cost**: Higher API costs for large documents
- **Latency**: Slightly higher latency with very large contexts

**For HVAC Use Case**: Full context is better because:
- Technicians need comprehensive understanding
- Manuals have interconnected procedures
- Safety information must always be available

### Why OpenAI?

1. **Quality**: Excellent understanding of technical documentation
2. **Large Context**: GPT-4o supports 128K tokens (sufficient for 2 manuals)
3. **Voice Integration**: Native STT (Whisper) and TTS support
4. **Reliability**: Production-ready API with good uptime
5. **Model Flexibility**: Easy to switch models via configuration

### Why System Prompt Approach?

Instead of using a custom LLM wrapper, we inject document context via system prompt:

**Advantages**:
- **Simplicity**: Works with LiveKit's built-in LLM plugin
- **Reliability**: Less custom code = fewer bugs
- **Performance**: LiveKit optimizes LLM calls
- **Maintenance**: Easier to update and debug

**How it works**:
1. Documents are loaded and truncated to fit context window
2. System prompt is created with document text embedded
3. LiveKit's OpenAI LLM plugin uses this system prompt
4. Every user message gets full document context automatically

## Data Flow

1. **Startup**:
   - Load PDFs from `documents/` directory
   - Extract text from PDFs
   - Truncate to fit model's context window
   - Create system prompt with document context

2. **User Speaks**:
   - LiveKit VAD detects speech
   - OpenAI STT transcribes speech to text
   - Text sent to LLM with system prompt (includes documents)

3. **LLM Response**:
   - OpenAI LLM generates response using:
     - System prompt (with full document context)
     - Conversation history
     - Current user message
   - Response text returned

4. **Voice Output**:
   - OpenAI TTS converts response to speech
   - Audio streamed back to user via LiveKit

## Configuration

### Environment Variables

- `LIVEKIT_URL`: WebSocket URL for LiveKit server
- `LIVEKIT_API_KEY`: API key for LiveKit authentication
- `LIVEKIT_API_SECRET`: API secret for LiveKit authentication
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: Model to use (default: `gpt-4o`)

### Model Selection

**Recommended**: `gpt-4o`
- 128K token context window
- Fast responses
- Good understanding of technical content

**Alternatives**:
- `gpt-4-turbo`: Similar to gpt-4o, slightly different pricing
- `gpt-4`: 8K context (may need more aggressive truncation)
- `gpt-3.5-turbo`: Cheaper but lower quality

## Future Enhancements

Potential improvements (not implemented):

1. **RAG for Very Large Documents**: If documents exceed context window
2. **Document Chunking**: Split documents intelligently
3. **Multi-Document RAG**: Vector search across multiple manuals
4. **Custom LLM Wrapper**: Direct control over API calls
5. **Streaming Responses**: Real-time response generation
6. **Document Versioning**: Track which manual versions are loaded
7. **Conversation Persistence**: Save conversations for review

## Performance Considerations

- **Document Loading**: Happens once at startup (cached in memory)
- **Token Usage**: ~3000 tokens reserved for system prompt + conversation
- **Latency**: Typically 1-3 seconds for LLM response
- **Concurrent Sessions**: LiveKit handles multiple users automatically

## Security Considerations

- **API Keys**: Stored in `.env` file (not committed to git)
- **Document Privacy**: Documents processed locally, only text sent to OpenAI
- **No Data Persistence**: Conversations not stored (can be added if needed)
- **Access Control**: LiveKit handles authentication and authorization

