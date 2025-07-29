from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List
from pathlib import Path
from tempfile import NamedTemporaryFile
import sys
import uuid

CURRENT_DIR = Path(__file__).resolve().parent
SERVICES_DIR = (CURRENT_DIR / "../services").resolve()

sys.path.append(str(SERVICES_DIR))

from generate_filled_1040 import generate_filled_1040

router = APIRouter()

OUTPUT_DIR = (CURRENT_DIR / "../static/generated_documents/").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/")
async def home():
  return { "message" : "AI Tax Return Agent backend is running" }

# Upload files, extract data, calculate taxes, and generate Form 1040
@router.post("/upload_documents", response_class = FileResponse)
async def upload_documents(
  background_tasks: BackgroundTasks,
  files : List[UploadFile] = File(...)
):
  temp_pdf_paths = []
  for file in files:
    content = await file.read()
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
      tmp.write(content)
      temp_path = Path(tmp.name)
      temp_pdf_paths.append(temp_path)
      background_tasks.add_task(temp_path.unlink, missing_ok=True)

  input_pdf_path = (
    CURRENT_DIR / "../static/templates/f1040_2024.pdf"
  ).resolve(strict=True)

  document_id = f"{uuid.uuid4().hex}.pdf"
  output_pdf_path = OUTPUT_DIR / document_id

  generate_filled_1040(temp_pdf_paths, input_pdf_path, output_pdf_path)

  return JSONResponse(content = { "document_id": document_id })
