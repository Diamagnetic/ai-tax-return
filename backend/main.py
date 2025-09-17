from fastapi import FastAPI
from api import endpoints
from core import config

app = FastAPI(
  title       = "AI Tax Return Agent",
  docs_url    = "/api/docs",
  redoc_url   = "/api/redoc",
  openapi_url = "/api/openapi.json"
)

app.include_router(endpoints.router)
config.api_middleware(app)
