"""Discord integration for FastAPI AgentRouter."""

from typing import Any, Callable, Dict

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from ..core.agent import Agent


def verify_discord_signature(
    public_key: str, signature: str, timestamp: str, body: bytes
) -> bool:
    """Verify Discord request signature.
    
    Args:
        public_key: Discord application public key
        signature: Request signature from headers
        timestamp: Request timestamp from headers
        body: Raw request body
        
    Returns:
        True if signature is valid
    """
    try:
        from nacl.signing import VerifyKey
        from nacl.exceptions import BadSignatureError
    except ImportError:
        raise ImportError(
            "PyNaCl is required for Discord integration. "
            "Install with: pip install PyNaCl"
        )
    
    message = timestamp.encode() + body
    
    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))
        verify_key.verify(message, bytes.fromhex(signature))
        return True
    except (BadSignatureError, Exception):
        return False


def create_discord_handler(agent: Agent, config: Dict[str, Any]) -> Callable:
    """Create a Discord interaction handler.
    
    Args:
        agent: The AI agent instance
        config: Discord configuration with 'public_key'
        
    Returns:
        FastAPI route handler for Discord interactions
    """
    public_key = config.get("public_key")
    if not public_key:
        raise ValueError("Discord public_key is required")
    
    async def handle_discord_interactions(request: Request) -> JSONResponse:
        """Handle Discord interactions."""
        # Get request headers and body
        signature = request.headers.get("X-Signature-Ed25519", "")
        timestamp = request.headers.get("X-Signature-Timestamp", "")
        body = await request.body()
        
        # Verify request signature
        if not verify_discord_signature(public_key, signature, timestamp, body):
            raise HTTPException(status_code=401, detail="Invalid request signature")
        
        # Parse interaction data
        import json
        interaction = json.loads(body)
        
        # Handle PING (type 1)
        if interaction.get("type") == 1:
            return JSONResponse(content={"type": 1})
        
        # Process interaction with agent
        try:
            response = await agent.handle_discord(interaction)
            return JSONResponse(content=response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return handle_discord_interactions