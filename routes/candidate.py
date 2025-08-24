from flask import Blueprint, render_template, request
import os
from utils.extract_text import extract_text_from_pdf
from utils.llm_parser import query_llama
from utils.predict_category import predict_category
from werkzeug.utils import secure_filename
from db.save import save_resume_to_db

candidate_bp = Blueprint("candidate", __name__)

UPLOAD_FOLDER = "uploaded_resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@candidate_bp.route("/", methods=["GET", "POST"])
def upload():
    result = None
    show_submit = False

    if request.method == "POST":
        file = request.files.get("cv")
        action = request.form.get("action")

        if file and action == "analyze":
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)

            raw_text = extract_text_from_pdf(save_path)
            result = query_llama(raw_text)
            predicted_job = predict_category(raw_text)
            result["PredictedJob"] = predicted_job
            result["RawText"] = raw_text
            result["PDFPath"] = save_path

            show_submit = True
            return render_template("upload.html", info=result, show_submit=show_submit)

        elif action == "submit":
            # Nhận thông tin từ form hidden
            import json
            resume_json = request.form.get("resume_json")
            if resume_json:
                parsed = json.loads(resume_json)
                save_resume_to_db(parsed, parsed["RawText"], parsed["PDFPath"])
                return render_template("upload.html", submitted=True)

    return render_template("upload.html")
