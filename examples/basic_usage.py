"""Basic usage example with FastAPI AgentRouter."""

import os
from typing import TYPE_CHECKING

import uvicorn
import vertexai
from fastapi import FastAPI
from vertexai import agent_engines

import fastapi_agentrouter

if TYPE_CHECKING:
    from vertexai.agent_engines import AgentEngine


PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
STAGING_BUCKET = os.environ["STAGING_BUCKET"]
AGENT_NAME = os.environ["AGENT_NAME"]

app = FastAPI()


def get_agent() -> "AgentEngine":
    """Get the Vertex AI AgentEngine instance for the specified agent."""
    vertexai.init(
        project=PROJECT_ID,
        location=LOCATION,
        staging_bucket=STAGING_BUCKET,
    )

    apps = list(agent_engines.list(filter=f"display_name={AGENT_NAME}"))

    if len(apps) == 0:
        raise ValueError(f"Agent '{AGENT_NAME}' not found.")
    elif len(apps) > 1:
        raise ValueError(f"Multiple agents found with name '{AGENT_NAME}'.")

    app = apps[0]
    return app


app.dependency_overrides[fastapi_agentrouter.get_agent] = get_agent
app.include_router(fastapi_agentrouter.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
