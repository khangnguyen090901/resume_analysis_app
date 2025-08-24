from db.db import collection

def update_resume_by_id(resume_id, updated_data):
    collection.update_one({"_id": resume_id}, {"$set": updated_data})
