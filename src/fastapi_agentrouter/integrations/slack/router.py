"""Slack integration router."""

import logging
from typing import TYPE_CHECKING, Annotated, Any

from fastapi import APIRouter, Depends, Request

from .dependencies import check_slack_enabled, get_slack_request_handler

if TYPE_CHECKING:
    from slack_bolt.adapter.fastapi import SlackRequestHandler

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/slack", tags=["slack"], dependencies=[Depends(check_slack_enabled)]
)


@router.post("/events")
async def slack_events(
    request: Request,
    slack_request_handler: Annotated[
        "SlackRequestHandler", Depends(get_slack_request_handler)
    ],
) -> Any:
    return await slack_request_handler.handle(request)
