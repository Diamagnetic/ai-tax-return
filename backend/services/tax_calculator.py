from decimal import Decimal
from typing import List
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "models"))

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

from tax_schema import TaxReturnSummary, TaxBracket, TaxFormData

class TaxCalculator:
  def __init__(self, brackets: List[TaxBracket], standard_deduction: Decimal):
    self.brackets = sorted(brackets, key = lambda b: b.lower_limit)
    self.standard_deduction = standard_deduction

  def calculate_tax(self, taxable_income: Decimal) -> Decimal:
    tax = Decimal("0")
    for bracket in self.brackets:
      if taxable_income <= bracket.lower_limit:
        break

      upper = bracket.upper_limit or taxable_income
      amount_in_bracket = min(taxable_income, upper) - bracket.lower_limit
      if amount_in_bracket > 0:
        tax += amount_in_bracket * bracket.rate
    return tax.quantize(Decimal("0.01"))

  def summarize(self, data: TaxFormData) -> TaxReturnSummary:
    total_income = (
      data.w2.wages +
      data.nec_1099.nonemployee_compensation +
      data.int_1099.interest_income
    )
    tax_withheld = data.w2.federal_income_tax_withheld

    taxable_income = max(total_income - self.standard_deduction, Decimal("0"))
    estimated_tax_due = self.calculate_tax(taxable_income)
    estimated_refund = max(tax_withheld - estimated_tax_due, Decimal("0"))

    if tax_withheld >= estimated_tax_due:
      estimated_refund = tax_withheld - estimated_tax_due
      amount_owed = Decimal("0")
    else:
      estimated_refund = Decimal("0")
      amount_owed = estimated_tax_due - tax_withheld

    return TaxReturnSummary(
      forms_submitted = data.forms_submitted,
      total_income = total_income.quantize(Decimal("0.01")),
      taxable_income = taxable_income,
      total_tax_withheld = tax_withheld.quantize(Decimal("0.01")),
      estimated_tax_due = estimated_tax_due,
      estimated_refund = estimated_refund,
      amount_owed = amount_owed
    )
