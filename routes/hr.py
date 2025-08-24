from flask import Blueprint, render_template, request, redirect, session, url_for, send_from_directory, jsonify
from db.load import get_all_resumes, get_resume_by_id
from flask import flash
from db.update import update_resume_by_id
from bson.objectid import ObjectId
from db.db import collection  # dùng để xóa
import os
import re

hr_bp = Blueprint("hr", __name__, url_prefix="/hr")


# --- Trang đăng nhập HR ---
@hr_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "123456":
            session["logged_in"] = True
            return redirect(url_for("hr.dashboard"))
        else:
            error = "Sai tài khoản hoặc mật khẩu."

    return render_template("login.html", error=error)


# --- Trang dashboard: danh sách ứng viên ---
@hr_bp.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("hr.login"))

    search_query = request.args.get("search", "").strip()
    job_filter = request.args.get("filter", "").strip()
    skill_filter = request.args.get("skill", "").strip()
    min_exp = request.args.get("min_exp", "").strip()

    query = {}

    # Tìm kiếm theo tên, email, kỹ năng
    if search_query:
        query["$or"] = [
            {"full_name": {"$regex": search_query, "$options": "i"}},
            {"email": {"$regex": search_query, "$options": "i"}},
            {"skills": {"$elemMatch": {"$regex": search_query, "$options": "i"}}},
        ]

    # Lọc theo vị trí
    if job_filter:
        query["last_job_title"] = {"$regex": job_filter, "$options": "i"}

    # Lọc theo kỹ năng cụ thể
    if skill_filter:
        query["skills"] = {"$elemMatch": {
            "$regex": skill_filter, "$options": "i"}}

    # Lọc theo số năm kinh nghiệm
    if min_exp:
        try:
            min_exp = float(min_exp)
            query["experience"] = {"$gte": min_exp}
        except ValueError:
            pass  # Bỏ qua nếu nhập sai định dạng

    resumes = get_all_resumes(query=query, limit=100)

    # Tập hợp các vị trí cho dropdown
    all_positions = {cv.get("last_job_title", "")
                     for cv in get_all_resumes(limit=1000)}
    positions = sorted([p for p in all_positions if p])

    # Tập hợp tất cả kỹ năng có trong hệ thống
    all_skills = sorted({skill for cv in get_all_resumes(limit=1000)
                        for skill in cv.get("skills", [])})

    return render_template(
        "dashboard.html",
        resumes=resumes,
        positions=positions,
        all_skills=all_skills
    )


# --- Trang chi tiết ứng viên ---
@hr_bp.route("/detail/<id>", methods=["GET", "POST"])
def detail(id):
    if not session.get("logged_in"):
        return redirect(url_for("hr.login"))

    resume = get_resume_by_id(ObjectId(id))
    raw_text = resume.get("RawText", "")

    # Lấy dữ liệu từ session (nếu có)
    predicted_job = session.get("predicted_job")
    jd_result = session.get("jd_result")

    if request.method == "POST":
        action = request.form.get("action")

        if action == "predict_category":
            from utils.predict_category import predict_category
            predicted_job = predict_category(raw_text)
            session["predicted_job"] = predicted_job  # Ghi vào session

        elif action == "jd_match":
            jd_text = request.form.get("jd_text")
            if jd_text.strip():
                from utils.llm_matching import query_jd_matching_llama
                jd_result = query_jd_matching_llama(jd_text, raw_text)
                session["jd_result"] = jd_result  # Ghi vào session

    return render_template(
        "detail.html",
        cv=resume,
        jd_result=jd_result,
        predicted_job=predicted_job
    )


# --- Xóa ứng viên ---
@hr_bp.route("/delete/<id>", methods=["GET"])
def delete(id):
    if not session.get("logged_in"):
        return redirect(url_for("hr.login"))

    collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("hr.dashboard"))


@hr_bp.route("/edit/<id>", methods=["GET", "POST"])
def edit(id):
    if not session.get("logged_in"):
        return redirect(url_for("hr.login"))

    resume = get_resume_by_id(ObjectId(id))

    if request.method == "POST":
        updated_data = {
            "full_name": request.form.get("full_name"),
            "email": request.form.get("email"),
            "phone": request.form.get("phone"),
            "last_job_title": request.form.get("last_job_title"),
            "experience": int(request.form.get("experience", 0)) if request.form.get("experience", "").isdigit() else 0,
            "home_address": request.form.get("home_address"),
            "skills": [s.strip() for s in request.form.get("skills", "").split(",")],
            "tools": [t.strip() for t in request.form.get("tools", "").split(",")],
            "github": request.form.get("github", "").strip(),
            "linkedin": request.form.get("linkedin", "").strip(),
        }
        update_resume_by_id(ObjectId(id), updated_data)
        flash("✔️ Cập nhật thành công!", "success")
        return redirect(url_for("hr.detail", id=id))

    return render_template("edit.html", cv=resume)

# --- Tải file PDF ---


@hr_bp.route("/download/<filename>")
def download_file(filename):
    uploads = os.path.join("uploaded_resumes")
    return send_from_directory(uploads, filename, as_attachment=True)

@hr_bp.route("/clear_detail_session")
def clear_detail_session():
    session.pop("predicted_job", None)
    session.pop("jd_result", None)
    return redirect(url_for("hr.dashboard"))

@hr_bp.route("/api/predict_category/<id>", methods=["POST"])
def api_predict_category(id):
    resume = get_resume_by_id(ObjectId(id))
    raw_text = resume.get("RawText", "")
    from utils.predict_category import predict_category
    predicted = predict_category(raw_text)
    return jsonify({"predicted_job": predicted})


@hr_bp.route("/api/jd_match/<id>", methods=["POST"])
def api_jd_match(id):
    resume = get_resume_by_id(ObjectId(id))
    jd_text = request.json.get("jd_text", "")
    raw_text = resume.get("RawText", "")
    from utils.llm_matching import query_jd_matching_llama
    result = query_jd_matching_llama(jd_text, raw_text)
    return jsonify(result)

