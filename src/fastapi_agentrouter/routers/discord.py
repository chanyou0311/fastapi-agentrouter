"""Discord integration router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import Agent, check_discord_enabled

router = APIRouter(prefix="/discord", tags=["discord"])


@router.get("/", dependencies=[Depends(check_discord_enabled)])
async def discord_status() -> JSONResponse:
    """Discord endpoint status."""
    return JSONResponse(content={"status": "ok"})


@router.post("/interactions", dependencies=[Depends(check_discord_enabled)])
async def handle_discord_interactions(agent: Agent) -> JSONResponse:
    """Handle Discord interactions (mock implementation)."""
    return JSONResponse(content={"status": "ok", "platform": "discord"})
