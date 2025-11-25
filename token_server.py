"""
Simple token server for generating LiveKit access tokens for the web client.
Run this alongside your agent to generate tokens for web clients.
"""

import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Try to import LiveKit's official AccessToken
try:
    from livekit import api
    AccessToken = api.AccessToken
    VideoGrant = api.VideoGrants
except ImportError:
    try:
        from livekit_api import AccessToken, VideoGrant
    except ImportError:
        # Fallback: use livekit.rtc if available
        try:
            from livekit import rtc
            AccessToken = rtc.AccessToken
            VideoGrant = rtc.VideoGrant
        except (ImportError, AttributeError):
            raise ImportError(
                "Could not import AccessToken from livekit. "
                "Please install: pip install livekit-api"
            )

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for web client

logger = logging.getLogger(__name__)

# Get credentials from environment
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


@app.route("/token", methods=["POST"])
def generate_token():
    """Generate a LiveKit access token for a user."""
    try:
        data = request.json or {}
        identity = data.get("identity", "user-" + os.urandom(4).hex())
        room_name = data.get("room", "hvac-room")
        name = data.get("name", "User")
        
        # Ensure identity is a non-empty string
        if not identity or not isinstance(identity, str) or len(identity.strip()) == 0:
            identity = "user-" + os.urandom(4).hex()
        
        identity = identity.strip()
        
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            return jsonify({"error": "LiveKit credentials not configured"}), 500
        
        logger.info(f"Generating token - Identity: '{identity}', Room: '{room_name}', Name: '{name}'")
        
        # Use LiveKit's official AccessToken class
        grant = VideoGrant(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )
        
        token = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(identity) \
            .with_name(name) \
            .with_grants(grant) \
            .to_jwt()
        
        logger.info(f"Generated token successfully for identity: '{identity}', room: '{room_name}'")
        
        return jsonify({
            "token": token,
            "url": LIVEKIT_URL,
            "room": room_name,
        })
    except Exception as e:
        logger.error(f"Error generating token: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        logger.error("LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env")
        exit(1)
    
    logger.info("Starting token server on http://localhost:8080")
    logger.info("Token endpoint: http://localhost:8080/token")
    app.run(host="0.0.0.0", port=8080, debug=True)