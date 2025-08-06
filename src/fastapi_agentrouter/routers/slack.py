"""Slack integration router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import check_slack_enabled

router = APIRouter(prefix="/slack", tags=["slack"])


@router.get("/", dependencies=[Depends(check_slack_enabled)])
async def slack_status() -> JSONResponse:
    """Slack endpoint status."""
    return JSONResponse(content={"status": "ok"})
