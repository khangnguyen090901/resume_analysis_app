from datetime import datetime
import os
from db.db import collection

def save_resume_to_db(result: dict, raw_text: str, pdf_path: str = None):
    # ✅ Chuẩn hóa experience thành int (mặc định 0 nếu sai)
    try:
        experience = int(result.get("YearsOfExperience"))
    except (ValueError, TypeError):
        experience = 0

    doc = {
        "full_name": result.get("FullName"),
        "email": result.get("Email"),
        "phone": result.get("PhoneNumber"),
        "github": result.get("GitHubURL"),
        "linkedin": result.get("LinkedInURL"),
        "experience": experience,  # ✅ đã được chuẩn hóa
        "skills": result.get("Skills"),
        "tools": result.get("Tools"),
        "education": result.get("Education"),
        "home_address": result.get("HomeAddress"),
        "last_job_title": result.get("LastJobTitle"),
        "created_at": datetime.utcnow(),
        "RawText": raw_text
    }

    if pdf_path:
        relative_path = os.path.relpath(pdf_path, start="static")
        doc["PDFPath"] = relative_path.replace("\\", "/")

    collection.insert_one(doc)
