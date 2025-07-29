from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def api_middleware(app: FastAPI) -> None:
  app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "https://ai-tax-return-f117a8fd9825.herokuapp.com"
    ],
    allow_credentials = True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
  )
