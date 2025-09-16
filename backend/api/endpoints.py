from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Annotated
from pathlib import Path
from tempfile import NamedTemporaryFile
from pydantic import ValidationError
import sys
import uuid

CURRENT_DIR = Path(__file__).resolve().parent
SERVICES_DIR = (CURRENT_DIR / "../services").resolve()
MODELS_DIR = (CURRENT_DIR / "../models").resolve()

sys.path.append(str(SERVICES_DIR))
sys.path.append(str(MODELS_DIR))

from generate_filled_1040 import generate_filled_1040
from user_pii import UserPII, FilingType

router = APIRouter()

OUTPUT_DIR = (CURRENT_DIR / "../static/generated_documents/").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/")
async def home():
  return { "message" : "AI Tax Return Agent backend is running" }

# Upload files, post user PII, extract data, calculate taxes, and
# generate Form 1040 (do not send to user yet)
@router.post("/api/submit_tax_form", response_class = JSONResponse)
async def upload_documents(
  background_tasks          : BackgroundTasks,
 
  # Individual form fields
  # because using UserPII causes 422 error after POST request
  first_name_middle_initial : Annotated[str, Form()],
  last_name                 : Annotated[str, Form()],
  ssn                       : Annotated[str, Form()],
  address                   : Annotated[str, Form()],
  city                      : Annotated[str, Form()],
  state                     : Annotated[str, Form()],
  zip_code                  : Annotated[str, Form()],
  filing_status             : Annotated[str, Form()] = FilingType.single,
  apt_no                    : Annotated[str | None, Form()] = None,

  files                     : List[UploadFile] = File(...),
):
  temp_pdf_paths = []
  
  if not (1 <= len(files) <= 3):
    return JSONResponse(
        status_code = 400,
        content = { "error" : "You must upload between 1 and 3 PDF files." }
    )

  for file in files:
    if file.content_type != "application/pdf" or not file.filename.endswith(".pdf"):
      return JSONResponse(
        status_code = 400,
        content = {
          "error": f"Invalid file type: {file.filename}. Only PDF files are accepted."
        }
      )
    content = await file.read()
    with NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
      tmp.write(content)
      temp_path = Path(tmp.name)
      temp_pdf_paths.append(temp_path)
      background_tasks.add_task(temp_path.unlink, missing_ok=True)

  try:
    pii = UserPII.model_validate({
      "first_name_middle_initial" : first_name_middle_initial,
      "last_name"                 : last_name,
      "ssn"                       : ssn,
      "address"                   : address,
      "apt_no"                    : apt_no,
      "city"                      : city,
      "state"                     : state,
      "zip_code"                  : zip_code,
      "filing_status"             : filing_status,
    })
  except ValidationError as e:
    return JSONResponse(
        status_code = 422,
        content = {
          "error" : "Invalid personal information.",
          "details" : e.errors()
        }
    )

  input_pdf_path = (
    CURRENT_DIR / "../static/templates/f1040_2024.pdf"
  ).resolve(strict=True)

  document_id = f"{uuid.uuid4().hex}.pdf"
  output_pdf_path = OUTPUT_DIR / document_id

  try:
    tax_return_summary : TaxReturnSummary = generate_filled_1040(
      file_buffers = temp_pdf_paths,
      pii = pii,
      input_pdf_path = input_pdf_path,
      output_pdf_path = output_pdf_path
    )
  except Exception as e:
    return JSONResponse(
        status_code = 500,
        content = {
          "error" : "An unexpected error occurred during tax form processing. Please try again later"
        }
    )

  return JSONResponse(content = {
    "document_id" : document_id,
    "tax_return_summary" : tax_return_summary.model_dump(mode = "json")
  })

# return form 1040 generated
@router.get("/api/documents/{document_id}", response_class = FileResponse)
async def get_generated_form1040(
  background_tasks: BackgroundTasks,
  document_id: str
):
  file_path = OUTPUT_DIR / document_id

  if not file_path.exists():
    return JSONResponse(
      status_code = 404,
      content = { "error" : "Document not found" }
    )

  background_tasks.add_task(file_path.unlink, missing_ok = True)

  return FileResponse(
    path = file_path,
    media_type = "application/pdf",
    filename = "filled_1040.pdf"
  )
