from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, Any
from decimal import Decimal

# Decorator to inject a validator
def validate_fields(fields: list[str]):
  def decorator(cls):
    # Pydantic v2 field validator for stripping commas from Decimal fields
    # This happens before the fields are further type-validated by the classes
    @field_validator(*fields, mode = "before")
    @classmethod
    def strip_commas(cls, v: Any) -> Decimal:
      # If the input is a string with commas, remove them before parsing to Decimal
      if isinstance(v, str):
        v = v.replace(",", "")
      return Decimal(v)
    # Attach the validator to the class dynamically
    setattr(cls, "strip_commas", strip_commas)
    return cls
  return decorator

@validate_fields(["wages", "federal_income_tax_withheld"])
class W2Data(BaseModel):
  wages: Decimal = Field(ge = 0)
  federal_income_tax_withheld : Decimal = Field(ge = 0)

@validate_fields(["nonemployee_compensation"])
class NECData(BaseModel):
  nonemployee_compensation: Decimal = Field(ge = 0)

@validate_fields(["interest_income"])
class INTData(BaseModel):
  interest_income: Decimal = Field()

class TaxFormData(BaseModel):
  form_type: Literal["W-2", "1099-NEC", "1099-INT"]
  data: Union[W2Data, NECData, INTData]

class TaxReturnSummary(BaseModel):
  total_income: Decimal = Field(ge = 0)
  total_tax_withheld: Decimal = Field(ge = 0)
  estimated_tax_due: Decimal = Field(ge = 0)
  estimated_refund: Decimal = Field(ge = 0)
