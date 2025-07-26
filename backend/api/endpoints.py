from fastapi import APIRouter, UploadFile, File
from typing import List

router = APIRouter()

@router.get("/")
async def home():
  return { "message" : "AI Tax Return Agent backend is running" }

# Upload files, extract data, calculate taxes, and return Form 1040
@router.post("/extract-and-calculate")
async def extract_and_calculate(files : List[UploadFile] = File(...)):
  results = []

  for file in files:
    file_name = file.filename
    content = await file.read()

    # TODO: logic for redaction, extraction, calculation

    results.append({ "file_name" : file_name, "size" : len(content) })

  # TODO: Return a pdf
  return { "status" : "ok", "uploaded" : results }
