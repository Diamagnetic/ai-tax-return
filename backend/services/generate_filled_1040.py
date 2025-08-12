from pathlib import Path
from typing import List, Dict, Type
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "models"))
TAX_POLICY_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "tax_policy"))

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

if TAX_POLICY_DIR not in sys.path:
    sys.path.insert(0, TAX_POLICY_DIR)

from form_extractor import FormExtractor
from form_generator import Form1040Generator
from tax_schema import TaxFormData, TaxReturnSummary
from tax_policy_config import SingleFiler2024Config
from user_pii import UserPII, FilingType

def generate_filled_1040(
  file_buffers: List[tuple[str, bytes]],
  pii: UserPII,
  input_pdf_path: Path,
  output_pdf_path: Path
) -> TaxReturnSummary:
  # Extract tax data
  extractor = FormExtractor()
  tax_form_data: TaxFormData = extractor.extract_from_pdfs(file_buffers)

  filing_type : FilingType = pii.filing_status

  config_map : Dict[FilingType, Type[TaxPolicyConfigBase]] = {
    FilingType.single: SingleFiler2024Config,
    # Add more mappings when other configs exist
  }

  tax_config_cls : FilingType = config_map[filing_type]

  generator = Form1040Generator(tax_config_cls)

  # Calculate tax summary
  tax_return_summary : TaxReturnSummary = generator.generate_pdf(
    input_pdf_path = input_pdf_path,
    pii = pii,
    data = tax_form_data,
    output_pdf_path = output_pdf_path
  )

  return tax_return_summary
