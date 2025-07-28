def generate_filled_1040(
  file_buffers: List[tuple[str, bytes]],
  input_pdf_path: Path,
  output_pdf_path: Path
) -> None:
  # Extract tax data
  extractor = FormExtractor()
  tax_form_data: TaxFormData = extractor.extract_from_pdfs(file_buffers)

  generator = Form1040Generator(SingleFiler2024Config)

  # Calculate tax summary
  generator.generate_pdf(
    input_pdf_path = input_pdf_path,
    data = tax_form_data
    output_pdf_path = output_pdf_path
  )
