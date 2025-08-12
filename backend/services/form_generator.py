from decimal import Decimal
from typing import Type
import pymupdf
from pydantic import BaseModel
from functools import wraps
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "models"))
TAX_POLICY_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "tax_policy"))

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

if TAX_POLICY_DIR not in sys.path:
    sys.path.insert(0, TAX_POLICY_DIR)

from tax_calculator import TaxCalculator, TaxReturnSummary, TaxFormData
from tax_policy_config import SingleFiler2024Config
from tax_schema import TaxBracket
from doc_schema import Form1040
from user_pii import UserPII, FilingType

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
    pii: UserPII,
    summary: TaxReturnSummary
  ) -> Form1040:
    total_income = summary.total_income

    return Form1040(
      pii                   = pii,
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

  @staticmethod
  def _checkbox_decorator(mapping: dict, field_attr: str):
    def decorator(func):
      @wraps(func)
      def wrapper(self, doc: pymupdf.Document, data: BaseModel):
        result = func(self, doc, data)
        checkbox_field = mapping.get(getattr(data, field_attr, None))

        if checkbox_field:
          for page in doc:
            for widget in page.widgets():
              if widget.field_name == checkbox_field:
                widget.field_value = "Yes"
                widget.update()

        return result
      return wrapper
    return decorator

  @_checkbox_decorator(
    mapping = {
      FilingType.single            : "filing_status_single_checkbox",
      FilingType.married_joint     : "filing_status_married_joint_checkbox",
      FilingType.married_separate  : "filing_status_married_separate_checkbox",
      FilingType.head_of_household : "filing_status_head_checkbox",
      FilingType.qualifying_spouse : "filing_status_qualifying_spouse_checkbox"
    },
    field_attr = "filing_status"
  )
  def _fill_filing_status_checkbox(
    self,
    doc: pymupdf.Document,
    data: BaseModel
  ):
    # Decorator does the work
    pass

  def generate_pdf(
    self,
    input_pdf_path: str,
    data: TaxFormData,
    pii: UserPII,
    output_pdf_path: str
  ) -> TaxReturnSummary:
    # Calculate tax summary
    summary : TaxReturnSummary = self.calculator.summarize(data)

    # Create the form model using summary
    form = self._create_form_1040(data, pii, summary)

    # Load PDF and fill text fields
    doc = pymupdf.open(input_pdf_path)

    # Fill tax form data
    self._fill_textfields(doc, form)

    # Fill PII
    self._fill_textfields(doc, pii)

    # Tick checkbox
    self._fill_filing_status_checkbox(doc, pii)

    doc.save(output_pdf_path)
    doc.close()

    return summary
