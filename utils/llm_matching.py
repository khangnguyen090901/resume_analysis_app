import requests
import re
import json
from dotenv import load_dotenv
import os

API_KEY = os.getenv("GROQ_API_KEY")
API_URL = os.getenv("API_URL")

def query_jd_matching_llama(jd_text, resume_text):
    prompt = f"""
Bạn là chuyên gia tuyển dụng. Dưới đây là một bản mô tả công việc (JD) và một CV ứng viên. Hãy đánh giá độ phù hợp theo thang điểm từ 0 đến 10 và giải thích ngắn gọn lý do.

Job Description:
\"\"\"{jd_text}\"\"\"

Resume:
\"\"\"{resume_text}\"\"\"

Trả về kết quả JSON:
{{
  "MatchingScore": number,
  "Reason": string
}}
"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are an expert HR analyst."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(API_URL, headers=headers, json=body)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]

        # Trích JSON nếu có markdown
        match = re.search(r"\{.*\}", content, re.DOTALL)
        result_json = match.group(0) if match else content
        return json.loads(result_json)

    except Exception as e:
        return {"error": str(e)}
