from pydantic import BaseModel, Field
from decimal import Decimal
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from user_pii import UserPII

class Form1040(BaseModel):
  pii: UserPII = Field(
    description = "Personally identifiable information of the taxpayer"
  )
  wages: Decimal = Field(
    alias = "1a",
    description = "Wages, salaries, tips"
  )
  wages_total: Decimal = Field(
    alias = "1z",
    description = "Add lines 1a–1h"
  )
  taxable_interest: Decimal = Field(
    alias = "2b",
    description = "Taxable interest from Form 1099-INT"
  )
  other_income: Decimal = Field(
    alias = "8",
    description = "Other income from 1099-NEC"
  )
  total_income: Decimal = Field(
    alias = "9",
    description = "Total income = sum of lines 1a, 2b, and 8"
  )
  adjusted_gross_income: Decimal = Field(
    alias = "11",
    description = "Adjusted gross income"
  )
  standard_deduction: Decimal = Field(
    alias = "12",
    description = "Standard deduction based on filing status"
  )
  taxable_income: Decimal = Field(
    alias = "15",
    description = "Taxable income = total income minus standard deduction"
  )
  tax: Decimal = Field(
    alias = "16",
    description = "Income tax calculated using 2024 tax brackets"
  )
  federal_tax_withheld: Decimal = Field(
    alias = "25a",
    description = "Federal income tax withheld from Form W-2"
  )
  total_payments: Decimal = Field(
    alias = "33",
    description = "Total payments same as tax withheld if no credits"
  )
  refund: Decimal = Field(
    alias = "34",
    description = "Refund if total payments exceed tax due"
  )
  amount_owed: Decimal = Field(
    alias = "37",
    description = "Amount you owe if tax due exceeds total payments"
  )

  model_config = { "populate_by_name": True }
