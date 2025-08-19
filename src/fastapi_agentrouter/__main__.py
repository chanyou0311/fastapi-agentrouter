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
