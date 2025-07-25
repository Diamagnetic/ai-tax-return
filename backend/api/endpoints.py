from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def home():
  return { "message" : "AI Tax Return Agent backend is running" }
