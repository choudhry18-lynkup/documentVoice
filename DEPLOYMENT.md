# Deployment Guide: LiveKit Cloud

This guide explains how to deploy the HVAC Voice Agent to LiveKit Cloud.

## LiveKit Cloud Compatibility

✅ **Yes, this implementation works on LiveKit Cloud!**

The code uses LiveKit's standard Python Agents SDK, which is fully compatible with LiveKit Cloud. No code changes are needed.

## Prerequisites

1. **LiveKit Cloud Account**: Sign up at https://cloud.livekit.io
2. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
3. **Python 3.9+**: For local development/testing

## Getting LiveKit Cloud Credentials

1. **Sign in to LiveKit Cloud**: https://cloud.livekit.io
2. **Create or select a project**
3. **Get your credentials**:
   - Go to Project Settings → API Keys
   - Copy your:
     - **Server URL** (e.g., `wss://your-project.livekit.cloud`)
     - **API Key**
     - **API Secret**

## Configuration for LiveKit Cloud

### Option 1: Environment Variables (Recommended)

Set these environment variables:

```bash
export LIVEKIT_URL="wss://your-project.livekit.cloud"
export LIVEKIT_API_KEY="your-api-key"
export LIVEKIT_API_SECRET="your-api-secret"
export OPENAI_API_KEY="your-openai-key"
export OPENAI_MODEL="gpt-4o"  # Optional, defaults to gpt-4o
```

### Option 2: .env File (Local Development)

Create a `.env` file:

```bash
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-4o
```

## Deployment Options

### Option 1: LiveKit Cloud Agents (Managed)

LiveKit Cloud supports managed agent deployment:

1. **Prepare your code**:
   - Ensure all dependencies are in `requirements.txt`
   - Make sure documents are accessible (see Document Storage below)

2. **Deploy via LiveKit CLI**:
   ```bash
   # Install LiveKit CLI
   npm install -g livekit-cli
   
   # Login to LiveKit Cloud
   livekit-cli login
   
   # Deploy agent
   livekit-cli deploy agent
   ```

3. **Configure in LiveKit Cloud Dashboard**:
   - Go to Agents section
   - Set environment variables
   - Configure resource limits

### Option 2: Self-Hosted Agent (Connects to Cloud)

Run the agent on your own infrastructure that connects to LiveKit Cloud:

1. **Set up server/VM** (AWS, GCP, Azure, etc.)
2. **Install dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (use LiveKit Cloud credentials)

4. **Run the agent**:
   ```bash
   python main.py dev
   ```

5. **For production**, use a process manager like `systemd` or `supervisord`

### Option 3: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create documents directory
RUN mkdir -p documents

# Run the agent
CMD ["python", "main.py", "dev"]
```

Build and run:

```bash
docker build -t hvac-voice-agent .
docker run -d \
  --env-file .env \
  -v $(pwd)/documents:/app/documents \
  hvac-voice-agent
```

## Document Storage

### For Cloud Deployment

Documents need to be accessible to the agent. Options:

1. **Include in Docker image** (for static documents):
   ```dockerfile
   COPY documents/ /app/documents/
   ```

2. **Mount volume** (for dynamic documents):
   ```bash
   docker run -v /path/to/documents:/app/documents ...
   ```

3. **Cloud storage** (S3, GCS, etc.):
   - Modify `document_processor.py` to download from cloud storage
   - Cache locally after first download

4. **Git repository** (for version-controlled documents):
   - Include documents in repo (if not sensitive)
   - Agent downloads on startup

## Testing the Deployment

1. **Test locally first**:
   ```bash
   python test_documents.py
   python main.py dev
   ```

2. **Connect from client**:
   - Use LiveKit's web SDK or mobile SDK
   - Connect to your LiveKit Cloud project
   - The agent will automatically join when a participant connects

3. **Monitor logs**:
   - Check LiveKit Cloud dashboard for agent logs
   - Or check your server logs if self-hosting

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `LIVEKIT_URL` | Yes | LiveKit Cloud WebSocket URL | `wss://project.livekit.cloud` |
| `LIVEKIT_API_KEY` | Yes | LiveKit API Key | `APxxxxxxxxxxxxx` |
| `LIVEKIT_API_SECRET` | Yes | LiveKit API Secret | `xxxxxxxxxxxxx` |
| `OPENAI_API_KEY` | Yes | OpenAI API Key | `sk-...` |
| `OPENAI_MODEL` | No | OpenAI model to use | `gpt-4o` (default) |
| `DOCUMENTS_DIR` | No | Documents directory path | `./documents` (default) |

## Troubleshooting

### Agent Not Connecting

- ✅ Verify `LIVEKIT_URL` is correct (should start with `wss://`)
- ✅ Check API key and secret are correct
- ✅ Ensure agent has network access to LiveKit Cloud
- ✅ Check firewall rules allow outbound connections

### Documents Not Loading

- ✅ Verify `documents/` directory exists and is accessible
- ✅ Check file permissions
- ✅ Ensure PDFs are not corrupted
- ✅ Check logs for extraction errors

### OpenAI API Errors

- ✅ Verify `OPENAI_API_KEY` is set correctly
- ✅ Check OpenAI API quota/limits
- ✅ Verify model name is correct
- ✅ Check network connectivity to OpenAI API

### High Latency

- ✅ Use `gpt-4o` for faster responses
- ✅ Reduce document size (truncate more aggressively)
- ✅ Deploy agent closer to LiveKit Cloud region
- ✅ Check network latency

## Production Considerations

1. **Scaling**: LiveKit Cloud handles scaling automatically
2. **Monitoring**: Use LiveKit Cloud dashboard + your own logging
3. **Error Handling**: Already implemented in code
4. **Security**: 
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, etc.)
   - Rotate API keys regularly
5. **Cost Optimization**:
   - Use appropriate model for your needs
   - Cache documents to avoid re-processing
   - Monitor token usage

## Support

- **LiveKit Docs**: https://docs.livekit.io/agents/
- **LiveKit Cloud**: https://cloud.livekit.io
- **LiveKit Discord**: https://livekit.io/discord
