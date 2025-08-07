"""Discord integration router."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .dependencies import check_discord_enabled

router = APIRouter(prefix="/discord", tags=["discord"])


@router.get("/", dependencies=[Depends(check_discord_enabled)])
async def discord_status() -> JSONResponse:
    """Discord endpoint status."""
    return JSONResponse(content={"status": "ok"})
