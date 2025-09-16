from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def api_middleware(app: FastAPI) -> None:
  app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:8501"
    ],
    allow_credentials = True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
  )
