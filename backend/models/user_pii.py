from pydantic import BaseModel, Field
from enum import Enum


class FilingType(str, Enum):
  single = "Single"
  married_joint = "Married Filing Jointly"
  married_separate = "Married Filing Separately"
  head_of_household = "Head of Household"
  qualifying_spouse = "Qualifying Surviving Spouse"

class UserPII(BaseModel):
  first_name_middle_initial: str = Field(
    alias = "first_name_middle_initial",
    description = "First name and middle initial"
  )
  last_name: str = Field(
    alias = "last_name",
    description = "Last name"
  )
  ssn: str = Field(
    alias = "ssn",
    description = "Social Security Number"
  )
  address: str = Field(
    alias = "address",
    description = "Home address (street and number)"
  )
  apt_no: str | None = Field(
    default = None,
    alias = "apt_no",
    description = "Apartment number (if any)"
  )
  city: str = Field(
    alias = "city",
    description = "City"
  )
  state: str = Field(
    alias = "state",
    description = "State"
  )
  # 5 digit zip code for now
  zip_code: str = Field(
    alias = "zip_code",
    description = "ZIP code"
  )
  filing_status: FilingType = Field(
    default=FilingType.single,
    alias = "filing_status",
    description = "Filing status for the tax return"
  )

  model_config = { "populate_by_name": True }
