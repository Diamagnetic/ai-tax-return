import pymupdf
from pydantic import BaseModel
from typing import Type
from faker import Faker
import random
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "models"))

if MODELS_DIR not in sys.path:
    sys.path.insert(0, MODELS_DIR)

from dummy_doc_schema import FormW2, Form1099INT, Form1099NEC

faker = Faker()

class DummyTaxDocumentGenerator:
  def __init__(self, w2_template: str, nec_template: str,
               int_template: str, output_base_dir: str):
    self.templates = {
      "w2" : w2_template,
      "nec" : nec_template,
      "int" : int_template
    }
    self.output_base_dir = output_base_dir
    os.makedirs(output_base_dir, exist_ok = True)

  def _generate_shared_identity(self) -> dict:
    name = faker.name()
    street = faker.street_address()
    city_etc = f"{faker.city()}, {faker.state_abbr()} {faker.zipcode()}"
    full_address = f"{street}, {city_etc}"
    recipient_tin = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"
    return {
      "name" : name,
      "street" : street,
      "city_etc" : city_etc,
      "address" : full_address,
      "recipient_tin" : recipient_tin
    }

  def _generate_form_data(self, form_type: str, identity: dict) -> BaseModel:
    if form_type == "w2":
      return FormW2(
        ssn = faker.ssn(),
        name = identity["name"],
        address = identity["address"],
        wages = f"{random.uniform(100, 100000):.2f}",
        federal_income_tax_withheld = f"{random.uniform(1, 10000):.2f}"
      )
    elif form_type == "nec":
      return Form1099NEC(
        recipient_tin = identity["recipient_tin"],
        name = identity["name"],
        street = identity["street"],
        city_etc = identity["city_etc"],
        nonemployee_compensation = f"{random.uniform(5000, 30000):.2f}",
        federal_income_tax_withheld = f"{random.uniform(0, 3000):.2f}"
      )
    elif form_type == "int":
      return Form1099INT(
        recipient_tin = identity["recipient_tin"],
        name = identity["name"],
        street = identity["street"],
        city_etc = identity["city_etc"],
        interest_income = f"{random.uniform(10, 2000):.2f}"
      )

  def _fill_textfields(self, doc: pymupdf.Document, data: BaseModel):
    # Create alias to value mapping directly
    alias_map = {
      field.alias : getattr(data, name)
      # Using type(data) instead of data to avoid using deprecated code
      for name, field in type(data).model_fields.items()
    }

    for page in doc:
      for field in page.widgets():
        key = field.field_name
        # The text fields in the pdfs have been named according to the form
        # Get the value of the required field from the map
        # and update the pdf
        if key in alias_map:
          field.field_value = str(alias_map[key])
          field.update()

  def generate_documents(self, n: int):
    for i in range(n):
      identity = self._generate_shared_identity()
      folder = os.path.join(self.output_base_dir, str(i + 1))
      os.makedirs(folder, exist_ok = True)

      # fill template forms and create a triplet of dummy forms
      for form_type in ["w2", "nec", "int"]:
        sample_path = self.templates[form_type]
        doc = pymupdf.open(sample_path)
        form_data = self._generate_form_data(form_type, identity)
        self._fill_textfields(doc, form_data)
        output_path = os.path.join(folder, f"{form_type}_{i + 1}.pdf")
        doc.save(output_path)
        doc.close()

if __name__ == "__main__":
  TEMPLATE_DIR = os.path.abspath(
    os.path.join(CURRENT_DIR, "..", "sample_docs", "templates")
  )

  OUTPUT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "sample_docs"))

  generator = DummyTaxDocumentGenerator(
    w2_template = os.path.join(TEMPLATE_DIR, "2024 Form W-2.pdf"),
    nec_template = os.path.join(TEMPLATE_DIR, "Form 1099-NEC.pdf"),
    int_template = os.path.join(TEMPLATE_DIR, "Form 1099-INT.pdf"),
    output_base_dir = OUTPUT_DIR
  )

  generator.generate_documents(20)
