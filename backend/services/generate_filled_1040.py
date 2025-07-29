from pathlib import Path
from typing import List
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TAX_POLICY_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "tax_policy"))

if TAX_POLICY_DIR not in sys.path:
    sys.path.insert(0, TAX_POLICY_DIR)

from form_extractor import FormExtractor
from tax_calculator import TaxFormData
from tax_policy_config import SingleFiler2024Config

def generate_filled_1040(
  file_buffers: List[tuple[str, bytes]],
  input_pdf_path: Path,
  output_pdf_path: Path
) -> None:
  # Extract tax data
  extractor = FormExtractor()
  tax_form_data: TaxFormData = extractor.extract_from_pdfs(file_buffers)

  generator = Form1040Generator(SingleFiler2024Config)

  # Calculate tax summary
  generator.generate_pdf(
    input_pdf_path = input_pdf_path,
    data = tax_form_data,
    output_pdf_path = output_pdf_path
  )
