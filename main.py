"""
Main entry point for the HVAC Voice Agent application.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def validate_environment():
    """Validate that required environment variables are set."""
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "OPENAI_API_KEY",
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and fill in the values")
        return False
    
    return True


if __name__ == "__main__":
    logger.info("Starting HVAC Voice Agent")
    
    if not validate_environment():
        exit(1)
    
    # Import and run the voice agent
    from voice_agent import cli
    
    logger.info("Voice agent CLI ready. Use 'python main.py dev' to start in development mode.")
    logger.info("Or use 'python -m voice_agent dev' directly")
    
    # The cli.run_app is called from voice_agent.py
    # For direct execution, we can import the entrypoint
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        from livekit.agents import cli as livekit_cli
        from voice_agent import entrypoint, WorkerOptions
        
        livekit_cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
    else:
        logger.info("Run with 'python main.py dev' to start the agent")

