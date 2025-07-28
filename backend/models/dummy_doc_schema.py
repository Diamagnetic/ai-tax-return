from pydantic import BaseModel, Field

class TaxFiler(BaseModel):
  name: str = Field(alias = "name", description = "Filer's full name")
  street: str = Field(alias = "street", description = "Filer's street address")
  city_etc: str = Field(
    alias = "city_etc",
    description = "Filer's city, state, and ZIP"
  )
  recipient_tin: str = Field(
    alias = "recipient_tin",
    description = "Recipient's TIN"
  )

class Form1099INT(TaxFiler):
  interest_income: str = Field(alias = "1", description = "Interest income")

  model_config = { "populate_by_name": True }

class Form1099NEC(TaxFiler):
  nonemployee_compensation: str = Field(
    alias = "1",
    description = "Nonemployee compensation"
  )
  federal_income_tax_withheld: str = Field(
    alias = "4",
    description = "Federal income tax withheld"
  )

  model_config = { "populate_by_name": True }

class FormW2(BaseModel):
  ssn: str = Field(alias = "a", description = "Employee's SSN")
  name: str = Field(alias = "e", description = "Filer's full name")
  address: str = Field(alias = "f", description = "Filer's street address")
  wages: str = Field(
    alias = "1",
    description = "Wages, tips, other compensation"
  )
  federal_income_tax_withheld: str = Field(
    alias = "2",
    description = "Federal income tax withheld"
  )

  model_config = { "populate_by_name": True }
