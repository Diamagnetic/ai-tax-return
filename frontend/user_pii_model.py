import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator

US_STATE_ABBRS = [
  "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
]

class FilingType(str, Enum):
  single = "Single"
  married_joint = "Married Filing Jointly"
  married_separate = "Married Filing Separately"
  head_of_household = "Head of Household"
  qualifying_spouse = "Qualifying Surviving Spouse"

class FrontUserPII(BaseModel):
  first_name_middle_initial : str = Field(
    description = "First name and middle initial"
  )
  last_name : str = Field(
    description = "Last name"
  )
  ssn : str = Field(
    description = "Social Security Number, 9 digits"
  )
  address : str = Field(
    description = "Home address (street and number)"
  )
  apt_no : Optional[str] = Field(
    default = None,
    description = "Apartment number (optional)"
  )
  city : str = Field(
    description = "City"
  )
  state : str = Field(
    description = "State (2-letter abbreviation)"
  )
  zip_code : str = Field(
    description = "ZIP code, 5 digits"
  )
  filing_status : FilingType = Field(
    default = FilingType.single,
    description = "Filing status"
  )

  @field_validator("ssn")
  @classmethod
  def validate_ssn(cls, v : str) -> str:
    digits = re.sub(r"\D", "", v or "")
 
    if not re.fullmatch(r"\d{9}", digits):
      raise ValueError("SSN must be 9 digits (numbers only)")

    return digits

  @field_validator("zip_code")
  @classmethod
  def validate_zip(cls, v : str) -> str:
    digits = re.sub(r"\D", "", v or "")

    if not re.fullmatch(r"\d{5}", digits):
      raise ValueError("ZIP code must be 5 digits")

    return digits

  @field_validator("state")
  @classmethod
  def validate_state(cls, v : str) -> str:
    abbr = (v or "").strip().upper()

    if abbr not in US_STATE_ABBRS:
      raise ValueError("Invalid U.S. state abbreviation")

    return abbr
