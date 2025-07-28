from pydantic import BaseModel, Field
from decimal import Decimal

class Form1040(BaseModel):
  wages: Decimal = Field(
    alias = "1a",
    description = "Wages, salaries, tips from Form W-2, Box 1"
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
