import pymupdf
from PIL import Image
import pytesseract
import io
import os

tessdata_path = os.getenv("TESSDATA_PREFIX")

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")

doc = pymupdf.open("D:/E/Dhamange/Chirag/MS/CSU_Chico/job_application_tasks/greengrowth-cpas/task/backend/services/W2.pdf")
#doc = pymupdf.open("D:/E/Dhamange/Chirag/MS/CSU_Chico/tax/2024/chirag_dhamange_w2_2024.pdf")

#print(doc.metadata)

for page in doc: # iterate the document pages
#  #pix = page.get_pixmap(dpi=300)
#  #pix.save("debug_page.png")
#  #text = page.get_textpage_ocr(dpi = 300, tessdata = tessdata_path)
#  #data = text.extractJSON(sort = True, flags = 8)
#  #print(data)
#  #text = page.get_text("json")
#  #print(text)
#
#  #for i, block in enumerate(data["blocks"]):
  pix = page.get_pixmap(dpi=300)
  img = Image.open(io.BytesIO(pix.tobytes("jpg")))
  data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
#  print(data)
#  print(data["block_num"])
  #print(data.keys())
#  print(data["text"][7])
#  print(pix.samples)
  #print(data['text'])
#  scale_x = page.rect.width / pix.width
#  scale_y = page.rect.height / pix.height
#  
#  block_texts = (
#    data[data["text"].notnull() & (data["text"].str.strip() != "")]
#    .groupby(["page_num", "block_num"])["text"]
#    .apply(lambda x: " ".join(x))
#  )
  blocks = {}
  for i, text in enumerate(data["text"]):
    block_num = data["block_num"][i]
    print(block_num)
    if block_num not in blocks:
      blocks[block_num] = ""
    blocks[block_num] += " " + text

  print(blocks)
#    if "ANYWHERE" in text:
#      print(data["par_num"][i])
      #print(data["level"][i])
#      x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
#        
#      # Convert image pixel coordinates to PDF coordinates
#      # PDF origin is bottom-left, image origin is top-left
#      rect = pymupdf.Rect(x * scale_x, y * scale_y, (x + w) * scale_x, (y + h) * scale_y)
#      page.add_redact_annot(rect, fill=(0, 0, 0))
#      page.draw_rect(rect, color = (0, 0, 0), fill=(0, 0, 0))
#
#  ## Step 4: Apply redactions and save
#  page.apply_redactions()
#  img.close()
doc.save("redacted_output.pdf")
doc.close()
