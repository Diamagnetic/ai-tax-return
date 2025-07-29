import streamlit as st
import requests
import io
import base64
from typing import List, Optional
import time

# Configure page
st.set_page_config(
  page_title = "AI Tax Return",
  layout = "wide"
)

# Initialize session state
if "uploaded_files" not in st.session_state:
  st.session_state.uploaded_files = []
if "processing_status" not in st.session_state:
  st.session_state.processing_status = None
if "form_data" not in st.session_state:
  st.session_state.form_data = None
if "document_id" not in st.session_state:
  st.session_state.document_id = None

# Server configuration
SERVER_URL = "https://ai-tax-return-backend-92e5b1232028.herokuapp.com"
UPLOAD_ENDPOINT = f"{SERVER_URL}/upload_documents"

def upload_files_to_server(files: List) -> Optional[str]:
  try:
    files_data = []
    for file in files:
      files_data.append(("files", (file.name, file.getvalue(), file.type)))
    
    response = requests.post(UPLOAD_ENDPOINT, files = files_data, timeout = 30)
    if response.status_code == 200:
      response_json = response.json()
      return response_json.get("document_id")
    else:
      st.error(f"Upload failed with status code: {response.status_code}")
      return None
  except requests.exceptions.RequestException as e:
    st.error(f"Upload failed: {str(e)}")
    return None
  except Exception as e:
    st.error(f"Error parsing response: {str(e)}")
    return None

def get_form_from_server(document_id: str) -> Optional[bytes]:
  try:
    form_endpoint = f"{SERVER_URL}/documents/{document_id}"
    response = requests.get(form_endpoint, timeout = 30)
    if response.status_code == 200:
      return response.content
    else:
      st.error(f"Failed to get form: {response.status_code}")
      return None
  except requests.exceptions.RequestException as e:
    st.error(f"Request failed: {str(e)}")
    return None

def display_pdf_preview(pdf_data: bytes):
  base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
  pdf_display = f"""
  <iframe src="data:application/pdf;base64,{base64_pdf}"
          width="100%" height="600" type="application/pdf">
  </iframe>
  """
  st.markdown(pdf_display, unsafe_allow_html = True)

def main():
  st.title("AI Tax Return")
  st.markdown("---")
  
  # File Upload Section
  st.header("1. Upload PDF Files")

  st.markdown("Please upload tax documents such as **W-2**, **1099-NEC**, and **1099-INT** in PDF format.")  

  # File uploader
  uploaded_files = st.file_uploader(
    "Choose PDF files",
    type = ["pdf"],
    accept_multiple_files = True,
    help = "Select one or more PDF files to process"
  )
  
  # Display currently selected files
  if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    st.success(f"Selected {len(uploaded_files)} file(s)")
  
  # Upload button
  col1, col2 = st.columns([1, 4])
  with col1:
    upload_button = st.button(
      "Upload Files",
      disabled = len(st.session_state.uploaded_files) == 0,
      type = "primary"
    )
  
  # Handle upload
  if upload_button and st.session_state.uploaded_files:
    with st.spinner("Uploading files to server..."):
      progress_bar = st.progress(0)
      
      # Simulate upload progress
      for i in range(100):
        time.sleep(0.01)  # Small delay for visual effect
        progress_bar.progress(i + 1)
      
      document_id = upload_files_to_server(st.session_state.uploaded_files)
      
      if document_id:
        st.session_state.document_id = document_id
        st.success("Files uploaded successfully!")
        st.session_state.processing_status = "completed"
      else:
        st.error("Upload failed. Please try again.")
        st.session_state.processing_status = "failed"
  
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
