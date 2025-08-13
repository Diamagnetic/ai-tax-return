import requests
from typing import List, Optional, Any

from config import SUBMIT_ENDPOINT, GET_FORM_ENDPOINT
from user_pii_model import FrontUserPII

# Sends multipart/form-data with:
#   - files : between 1 to 3 PDFs
#   - PII   : fields matching backend FastAPI params
# Returns backend JSON on success, or None on error.
def submit_tax_form(
  files : List[Any],
  pii : FrontUserPII
) -> Optional[dict]:
  try:
    files_data = []

    for f in files:
      files_data.append(("files", (f.name, f.getvalue(), f.type)))

    response = requests.post( 
      SUBMIT_ENDPOINT,
      data = pii.model_dump(by_alias = True, exclude_none = True),
      files = files_data
    )

    if response.status_code == 200:
      return response.json()

    # Try to surface backend error message
    try:
      err = response.json()
    except Exception:
      err = { "error" : f"HTTP {response.status_code}" }
    # return None to let UI decide
    return None

  except requests.exceptions.RequestException:
    return None

# Downloads the generated PDF bytes by document_id, or returns None on error.
def get_form_from_server(document_id : str) -> Optional[bytes]:
  try:
    url = f"{GET_FORM_ENDPOINT}/{document_id}"

    response = requests.get(url)

    if response.status_code == 200:
      return response.content

    return None
  except requests.exceptions.RequestException:
    return None
