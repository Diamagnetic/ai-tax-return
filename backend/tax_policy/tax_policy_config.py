from typing import List
from decimal import Decimal

class SingleFiler2024Config:
  @staticmethod
  def get_brackets() -> List[TaxBracket]:
    return [
      TaxBracket(
        lower_limit = Decimal("0"),
        upper_limit = Decimal("11600"),
        rate = Decimal("0.10")
      ),
      TaxBracket(
        lower_limit = Decimal("11600"),
        upper_limit = Decimal("47150"),
        rate = Decimal("0.12")
      ),
      TaxBracket(
        lower_limit = Decimal("47150"),
        upper_limit = Decimal("100525"),
        rate = Decimal("0.22")
      ),
      TaxBracket(
        lower_limit = Decimal("100525"),
        upper_limit = Decimal("191950"),
        rate = Decimal("0.24")
      ),
      TaxBracket(
        lower_limit = Decimal("191950"),
        upper_limit = Decimal("243725"),
        rate = Decimal("0.32")
      ),
      TaxBracket(
        lower_limit = Decimal("243725"),
        upper_limit = Decimal("609350"),
        rate = Decimal("0.35")
      ),
      TaxBracket(
        lower_limit = Decimal("609350"),
        upper_limit = None,
        rate = Decimal("0.37")
      )
    ]

  @staticmethod
  def get_standard_deduction() -> Decimal:
    return Decimal("14600")
