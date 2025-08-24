import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()  

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    db = client["resume_app"]
    collection = db["parsed_resumes"]
    print("✅ Kết nối MongoDB Atlas thành công!")
except Exception as e:
    print("❌ Lỗi kết nối:", e)
