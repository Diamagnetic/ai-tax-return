from fastapi import FastAPI
from api import endpoints

app = FastAPI(title = "AI Tax Return Agent")

app.include_router(endpoints.router)
