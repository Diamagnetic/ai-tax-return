from decimal import Decimal
from typing import Type
import pymupdf
from pydantic import BaseModel
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "models"))
TAX_POLICY_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "tax_policy"))

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

if TAX_POLICY_DIR not in sys.path:
    sys.path.insert(0, TAX_POLICY_DIR)

from .tax_calculator import TaxCalculator, TaxReturnSummary, TaxFormData
from tax_policy_config import SingleFiler2024Config
from tax_schema import TaxBracket
from doc_schema import Form1040

class Form1040Generator:
  def __init__(self, tax_config_cls: Type[SingleFiler2024Config]):
    self.tax_config = tax_config_cls()
    self.calculator = TaxCalculator(
      brackets = self.tax_config.get_brackets(),
      standard_deduction = self.tax_config.get_standard_deduction()
    )

  def _create_form_1040(
    self,
    data: TaxFormData,
    summary: TaxReturnSummary
  ) -> Form1040:
    total_income = summary.total_income

    return Form1040(
      wages                 = data.w2.wages,
      taxable_interest      = data.int_1099.interest_income,
      other_income          = data.nec_1099.nonemployee_compensation,
      total_income          = total_income,
      adjusted_gross_income = total_income,
      standard_deduction    = self.tax_config.get_standard_deduction(),
      tax                   = summary.estimated_tax_due,
      federal_tax_withheld  = data.w2.federal_income_tax_withheld,
      total_payments        = summary.total_tax_withheld,
      refund                = summary.estimated_refund,
      taxable_income        = (
        total_income - self.tax_config.get_standard_deduction()
      ),
      amount_owed           = max(
        summary.estimated_tax_due - summary.total_tax_withheld,
        Decimal("0")
      )
    )

  def _fill_textfields(self, doc: pymupdf.Document, data: BaseModel) -> None:
    alias_map = {
      field.alias : getattr(data, name)
      for name, field in type(data).model_fields.items()
    }

    for page in doc:
      for field in page.widgets():
        key = field.field_name
        if key in alias_map:
          field.field_value = str(alias_map[key])
          field.update()

  def generate_pdf(
    self,
    input_pdf_path: str,
    data: TaxFormData,
    output_pdf_path: str
  ) -> None:
    # Calculate tax summary
    summary = self.calculator.summarize(data)

    # Create the form model using summary
    form = self._create_form_1040(data, summary)

    # Load PDF and fill text fields
    doc = pymupdf.open(input_pdf_path)
    self._fill_textfields(doc, form)
    doc.save(output_pdf_path)
    doc.close()
