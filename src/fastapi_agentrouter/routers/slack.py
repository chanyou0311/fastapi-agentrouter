"""Slack integration router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import Agent, check_slack_enabled

router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("/", dependencies=[Depends(check_slack_enabled)])
async def slack_status() -> JSONResponse:
    """Slack endpoint status."""
    return JSONResponse(content={"status": "ok"})


@router.post("/events", dependencies=[Depends(check_slack_enabled)])
async def handle_slack_events(agent: Agent) -> JSONResponse:
    """Handle Slack events (mock implementation)."""
    return JSONResponse(content={"status": "ok", "platform": "slack"})
