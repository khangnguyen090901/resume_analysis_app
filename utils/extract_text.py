import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str):
    doc = fitz.open(file_path)  # ✅ Mở trực tiếp từ đường dẫn file PDF
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text