import requests
import json
import re
from dotenv import load_dotenv
import os

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = os.getenv("API_URL")


def normalize_url(url, domain_prefix):
    if not url:
        return ""
    url = url.strip()
    if url.lower() in ["none", "null", "không có", "no"]:
        return ""
    if url.startswith("http"):
        return url
    if not url.startswith("www.") and not url.startswith(domain_prefix):
        url = "www." + url
    return "https://" + url


def build_prompt(resume_text: str, override_name: str = "") -> str:
    name_hint = f"Full Name: {override_name}\n\n" if override_name else ""
    return f"""
You are an HR AI parser. Extract the following information from the resume below and return it strictly as a valid JSON object with double-quoted keys and values. Do not include any explanations or markdown.

Rules:
- JSON must be well-formed and parsable.
- Use English field names exactly as listed below.
- Avoid extracting lines that include address-related terms like “street”, “district”, “city”.
- Ignore any lines that include both a personal name and a location.
- Do NOT include names in HomeAddress.
- Only assign HomeAddress if it contains at least one of: "đường", "phường", "quận", "TP.", "thành phố", etc.
- Do not count Education years (e.g., 2015–2019 at university) as part of YearsOfExperience.
- YearsOfExperience must be a number (integer or float). Do NOT include education years. Only count professional work experience (e.g. internships, full-time, part-time jobs, or significant freelance projects). If unclear, estimate conservatively.
- Skills are programming languages, analytical skills, soft skills (e.g., Python, SQL, communication, leadership).
- Tools are software platforms and technical environments used for work (e.g., Excel, PowerPoint, Azure Databricks, MS Word).
- Do not include tools in Skills. Do not include skills in Tools.

VietNam Name Rules:
- Full name usually appears in the top few lines of the resume.
- It often appears in UPPERCASE or Title Case and contains 2–4 Vietnamese words.
- Ignore uppercase lines that clearly indicate universities, degrees, school names, or organizations.
- Ignore lines that contain keywords like: "ĐẠI HỌC", "UNIVERSITY", "COLLEGE", "KHOA", "TRƯỜNG", "SCHOOL", etc.
- Prioritize lines that contain common Vietnamese surnames such as: Nguyễn, Trần, Lê, Phạm, Hoàng, Huỳnh, Phan, Vũ, Võ, Đặng, Bùi, Đỗ, Hồ, Ngô, Dương, Lý, Trịnh, Trương, Hà, Mai, Lâm, Tạ, Tô, Châu, Cao, Tăng, Lương.
- Return only the most likely full name of the applicant.
- Do NOT include labels like "Name:", "Full Name:".
- Do NOT return multiple lines. Just the name.
- If a string contains a common Vietnamese last name and all-uppercase letters, it is likely a full name.
- If a line contains both a full name and an address-like keyword (e.g., "district", "city"), extract only the name part and ignore address terms.

Fields to extract:
- FullName
- Email
- PhoneNumber
- LinkedInURL
- GitHubURL
- HomeAddress
- Skills (array of strings)
- Tools (array of strings)
- YearsOfExperience
- LastJobTitle
- Education (list with Degree, Institution, GraduationYear, optional GPA)

YearsOfExperience must be a number (integer or float). Do not return null, N/A, or a string. If unclear, estimate conservatively.

{name_hint}Resume:
\"\"\"{resume_text}\"\"\"
"""


def query_llama(resume_text: str) -> dict:
    if not resume_text.strip():
        return {"error": "Resume text is empty."}

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a resume parser."},
            {"role": "user", "content": build_prompt(resume_text)}
        ],
        "temperature": 0.0
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        json_string = match.group(1) if match else content.strip()
        json_string = json_string.replace('\n', '')
        json_string = re.sub(r'[\x00-\x1F\x7F]', '', json_string)
        json_string = json_string.replace("'", '"')
        json_string = re.sub(r'(["}\]])\s*"(\w+)":', r'\1, "\2":', json_string)

        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse failed: {e}", "raw": json_string}

        # Chuẩn hóa URL
        data["LinkedInURL"] = normalize_url(
            data.get("LinkedInURL", ""), "linkedin.com")
        data["GitHubURL"] = normalize_url(
            data.get("GitHubURL", ""), "github.com")

        # Làm sạch địa chỉ
        if "HomeAddress" in data and isinstance(data["HomeAddress"], str):
            data["HomeAddress"] = data["HomeAddress"].strip().replace('\n', ' ')

        # Chuẩn hóa YearsOfExperience
        years = data.get("YearsOfExperience")
        try:
            if isinstance(years, str) and years.strip().lower() in ["none", "null", "n/a", ""]:
                data["YearsOfExperience"] = 0
            else:
                data["YearsOfExperience"] = float(years)
        except (ValueError, TypeError):
            data["YearsOfExperience"] = 0  # fallback nếu lỗi parse

        return data

    except Exception as e:
        print("🔴 API error:", e)
        print("🧾 Raw response:", response.text if 'response' in locals()
              else 'No response')
        return {"error": str(e)}
