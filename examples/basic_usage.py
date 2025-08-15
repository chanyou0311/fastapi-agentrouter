"""Basic usage example with FastAPI AgentRouter.

Environment variables required:
- VERTEXAI__PROJECT_ID: GCP project ID
- VERTEXAI__LOCATION: GCP location (e.g., us-central1)
- VERTEXAI__STAGING_BUCKET: GCS bucket for staging
- VERTEXAI__AGENT_NAME: Display name of the Vertex AI Agent
"""

import uvicorn
from fastapi import FastAPI

import fastapi_agentrouter

app = FastAPI()

app.dependency_overrides[fastapi_agentrouter.get_agent] = (
    fastapi_agentrouter.get_vertex_ai_agent_engine
)
app.include_router(fastapi_agentrouter.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
