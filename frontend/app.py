import streamlit as st
import io
import base64
from typing import List, Optional
import time
import re
from decimal import Decimal, InvalidOperation

from api_client import submit_tax_form, get_form_from_server
from user_pii_model import FrontUserPII, FilingType, US_STATE_ABBRS

# Configure page
st.set_page_config(
  page_title = "AI Tax Return",
  layout = "wide"
)

# Initialize session state
if "tax_summary" not in st.session_state:
  st.session_state.tax_summary = None
if "uploaded_files" not in st.session_state:
  st.session_state.uploaded_files = []
if "processing_status" not in st.session_state:
  st.session_state.processing_status = None
if "form_data" not in st.session_state:
  st.session_state.form_data = None
if "document_id" not in st.session_state:
  st.session_state.document_id = None

def display_pdf_preview(pdf_data: bytes):
  base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
  pdf_display = f"""
  <iframe src="data:application/pdf;base64,{base64_pdf}"
          width="100%" height="600" type="application/pdf">
  </iframe>
  """
  st.markdown(pdf_display, unsafe_allow_html = True)

# Helper to submit files + PII together
def submit_files_and_pii(files, pii : FrontUserPII) -> bool:
  result = submit_tax_form(files, pii)

  if result:
    st.session_state.document_id = result.get("document_id")
    st.session_state.tax_summary = result.get("tax_return_summary")
    st.session_state.processing_status = "completed"
    return True

  st.session_state.processing_status = "failed"

  return False

def _to_decimal(v) -> Decimal:
  try:
    return v if isinstance(v, Decimal) else Decimal(str(v))
  except Exception:
    return Decimal("0")

def _fmt_money(v) -> str:
  d = _to_decimal(v).quantize(Decimal("0.01"))
  return f"${d}"

def main():
  st.title("AI Tax Return")
  st.markdown("---")

  # Step 1: Upload files + Enter PII
  st.header("1. Upload PDF Files & Enter Personal Information")
  st.markdown("Upload **W-2**, **1099-NEC**, and/or **1099-INT** (PDF). Then enter your details.")
  
  left, right = st.columns(2)
  
  with left:
    uploaded_files = st.file_uploader(
      "Choose up to 3 PDF files",
      type = ["pdf"],
      accept_multiple_files = True,
      help = "Only PDF files are accepted"
    )

    if uploaded_files:
      st.session_state.uploaded_files = uploaded_files
      st.success(f"Selected {len(uploaded_files)} file(s)")
  
  with right:
    with st.form("pii_form"):
      c1, c2 = st.columns(2)
      with c1:
        first_name_middle_initial = st.text_input(
          "First name and middle initial"
        )
      with c2:
        last_name = st.text_input("Last name")
  
      c3, c4 = st.columns(2)
      with c3:
        ssn = st.text_input("SSN (9 digits, numbers only)")
      with c4:
        filing = st.radio(
          "Filing status",
          [ft.value for ft in FilingType],
          index = 0,
          disabled = True,
          help = "Only 'Single' Filing Status is supported right now."
        )
  
      address = st.text_input("Home address (street and number)")
      apt_no = st.text_input("Apartment number (optional)")
  
      c5, c6, c7 = st.columns([1, 1, 1])
      with c5:
        city = st.text_input("City")
      with c6:
        state = st.selectbox(
          "State (2-letter)",
          US_STATE_ABBRS,
          index = US_STATE_ABBRS.index("CA")
        )
      with c7:
        zip_code = st.text_input(
          "ZIP code (5 digits)"
        )
  
      submit_btn = st.form_submit_button(
        "Submit",
        type = "primary",
        disabled = len(st.session_state.uploaded_files) == 0
      )
  
      if submit_btn:
        ssn = re.sub(r"\D", "", ssn or "")
        zip_code = re.sub(r"\D", "", zip_code or "")

        # Build PII model and validate on the frontend
        try:
          pii = FrontUserPII(
            first_name_middle_initial = first_name_middle_initial,
            last_name                 = last_name,
            ssn                       = ssn,
            address                   = address,
            apt_no                    = apt_no or None,
            city                      = city,
            state                     = state,
            zip_code                  = zip_code,
            filing_status             = FilingType.single
          )
        except Exception as e:
          # Pydantic error object pretty-print
          from pydantic import ValidationError
          if isinstance(e, ValidationError):
            for err in e.errors():
              st.error(f"{err['loc'][0]}: {err['msg']}")
          else:
            st.error(str(e))
        else:
          with st.spinner("Calculating your tax return..."):
            is_ok = submit_files_and_pii(st.session_state.uploaded_files, pii)
          if is_ok:
            st.success("Submitted successfully!")
          else:
            st.error("Submission failed. Please check inputs and try again.")
  
  st.markdown("---")

  if st.session_state.get("tax_summary"):
    tax_summary = st.session_state.tax_summary
    st.subheader("Submission Summary")

    top_left, top_right = st.columns([1, 1])
  
    with top_left:
      st.markdown("**Calculated Amounts**")
      st.markdown(
        f"- Estimated tax due: {_fmt_money(tax_summary.get('estimated_tax_due'))}\n"
        f"- Refund: {_fmt_money(tax_summary.get('estimated_refund'))}\n"
        f"- Amount owed: {_fmt_money(tax_summary.get('amount_owed'))}\n"
        f"- Total income: {_fmt_money(tax_summary.get('total_income'))}\n"
        f"- Taxable income: {_fmt_money(tax_summary.get('taxable_income'))}\n"
        f"- Total tax withheld: {_fmt_money(tax_summary.get('total_tax_withheld'))}"
      )
  
    with top_right:
      # Forms submitted
      forms = tax_summary.get("forms_submitted") or []
      if forms:
        st.markdown("**Forms Uploaded**")
        st.write(", ".join(forms))

    st.markdown("---")
  
  # Form Retrieval Section
  st.header("2. Get Form 1040")
  
  if not st.session_state.form_data:
    col1, col2 = st.columns([1, 4])
    with col1:
      get_form_button = st.button(
        "Get Form 1040",
        type = "secondary",
        disabled = st.session_state.document_id is None
      )
    
    # Handle form retrieval
    if get_form_button and st.session_state.document_id:
      with st.spinner("Retrieving Form 1040 from server..."):
        progress_bar = st.progress(0)
        
        # Simulate processing progress
        for i in range(100):
          time.sleep(0.02)  # Small delay for visual effect
          progress_bar.progress(i + 1)
        
        form_data = get_form_from_server(st.session_state.document_id)
        
        if form_data:
          st.session_state.form_data = form_data
          st.success("Form 1040 retrieved successfully!")
          st.rerun()
        else:
          st.error("Failed to retrieve form. Please try again.")
  else:
    # Show option to get new form when one already exists
    col1, col2 = st.columns([1, 4])
    with col1:
      if st.button("Get New Form", type = "secondary"):
        st.session_state.form_data = None
        st.rerun()
  
  # Display form preview and download option
  if st.session_state.form_data:
    st.markdown("---")
    st.header("3. Form Preview")
    
    # Preview and download buttons
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
      st.download_button(
        label = "Download Form",
        data = st.session_state.form_data,
        file_name = "form_1040.pdf",
        mime = "application/pdf",
        type = "primary"
      )
    
    with col2:
      if st.button("Refresh Preview"):
        st.rerun()
    
    # PDF Preview
    st.subheader("Preview:")
    try:
      display_pdf_preview(st.session_state.form_data)
    except Exception as e:
      st.error(f"Could not display PDF preview: {str(e)}")
      st.info("You can still download the file using the download button above.")
  
  # Footer
  st.markdown("---")

  st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: gray;'>
      Built by <b>Chirag Dhamange</b> · 
      <a href='https://github.com/Diamagnetic/ai-tax-return' target='_blank'>Source Code</a>
    </div>
    """,
    unsafe_allow_html=True
  )
 
if __name__ == "__main__":
  main()
