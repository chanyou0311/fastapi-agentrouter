"""Generic webhook router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import Agent, check_webhook_enabled

router = APIRouter(tags=["webhook"])


@router.get("/webhook", dependencies=[Depends(check_webhook_enabled)])
async def webhook_status() -> JSONResponse:
    """Webhook endpoint status."""
    return JSONResponse(content={"status": "ok"})


@router.post("/webhook", dependencies=[Depends(check_webhook_enabled)])
async def handle_webhook(agent: Agent) -> JSONResponse:
    """Handle webhook requests (mock implementation)."""
    return JSONResponse(content={"status": "ok", "platform": "webhook"})
