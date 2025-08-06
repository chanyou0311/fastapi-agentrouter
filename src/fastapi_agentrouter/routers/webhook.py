"""Generic webhook router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..dependencies import check_webhook_enabled

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/", dependencies=[Depends(check_webhook_enabled)])
async def webhook_status() -> JSONResponse:
    """Webhook endpoint status."""
    return JSONResponse(content={"status": "ok"})
