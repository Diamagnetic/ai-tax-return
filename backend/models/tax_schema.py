from pydantic import BaseModel, Field, field_validator
from typing import Any
from decimal import Decimal

class DecimalSanitizer(BaseModel):
  @field_validator("*", mode = "before")
  @classmethod
  def _sanitize(cls, v: Any) -> Decimal:
    if isinstance(v, str):
      v = v.replace(",", "").strip()
      if v == "":
        return Decimal("0")
    return Decimal(v)

class W2Data(DecimalSanitizer):
  wages: Decimal = Field(ge = 0)
  federal_income_tax_withheld : Decimal = Field(ge = 0)

class NECData(DecimalSanitizer):
  nonemployee_compensation: Decimal = Field(default = Decimal("0"), ge = 0)

class INTData(DecimalSanitizer):
  interest_income: Decimal = Field(default = Decimal("0"))

class TaxFormData(BaseModel):
  forms_submitted: list[str] = Field(default_factory = list)
  w2: W2Data = Field(alias = "w2")
  nec_1099: NECData = Field(default_factory = NECData, alias = "1099_nec")
  int_1099: INTData = Field(default_factory = INTData, alias = "1099_int")

class TaxReturnSummary(BaseModel):
  forms_submitted: list[str] = Field(default_factory = list)
  total_income: Decimal = Field(ge = 0)
  taxable_income: Decimal = Field(ge = 0)
  total_tax_withheld: Decimal = Field(ge = 0)
  estimated_tax_due: Decimal = Field(ge = 0)
  estimated_refund: Decimal = Field(ge = 0)
  amount_owed: Decimal = Field(ge = 0)

class TaxBracket(BaseModel):
  lower_limit: Decimal = Field(ge = 0)
  upper_limit: Decimal | None = Field(default = None)
  rate: Decimal = Field(ge = 0, le = 1)
