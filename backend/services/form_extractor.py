import openai
from openai import OpenAI
import pymupdf
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
import base64
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "models"))

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

from tax_schema import TaxFormData

class FormExtractor:
  SYSTEM_INSTRUCTIONS = """You are a tax form data extraction assistant. 

You will be given documents like W-2, 1099-NEC, or 1099-INT. 

Your task is to:
- Identify the form type.
- Extract the relevant fields:
  - W-2: wages, federal income tax withheld
  - 1099-NEC: nonemployee compensation
  - 1099-INT: interest income
- Return only structured JSON format.
- Always return string values with no dollar signs, commas, or additional text.
- Do not include explanations, summaries, or comments. JSON only."""

  def __init__(self):
    self.api_key = os.getenv("OPENAI_API_KEY")
    self.client = OpenAI(api_key = self.api_key)
    self.model = "gpt-4.1-nano"

  def _pdf_to_image_files(self, pdf_path: str) -> List[Path]:
    doc = pymupdf.open(pdf_path)
    image_paths = []

    for page_num in range(len(doc)):
      page = doc.load_page(page_num)
      pix = page.get_pixmap(dpi = 300)

      image_file = NamedTemporaryFile(delete = False, suffix = ".jpg")
      image_file.write(pix.tobytes("jpg"))
      image_file.close()

      image_paths.append(Path(image_file.name))

    return image_paths

  def _encode_image(self, image_path: Path) -> str:
    with open(image_path, "rb") as image_file:
      return base64.b64encode(image_file.read()).decode("utf-8")

  def extract_from_pdfs(self, pdf_paths: List[str]) -> TaxFormData:
    all_image_paths = []

    for pdf_path in pdf_paths:
      image_paths = self._pdf_to_image_files(pdf_path)
      all_image_paths.extend(image_paths)

    # list of dicts containing image information to pass as input
    encoded_images = [
      {
        "type" : "input_image",
        "image_url" : f"data:image/jpeg;base64,{self._encode_image(path)}",
        "detail" : "high"
      }
      for path in all_image_paths
    ]

    response = self.client.responses.parse(
      model = "gpt-4.1-mini",
      instructions = self.SYSTEM_INSTRUCTIONS,
      temperature = 0,
      input = [{
        "role": "user",
        "content": encoded_images
      }],
      text_format = TaxFormData
    )

    # delete all temporary images
    for path in all_image_paths:
      os.remove(path)

    event = response.output_parsed

    return event
