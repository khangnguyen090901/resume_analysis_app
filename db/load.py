from db.db import collection
from bson.objectid import ObjectId

def get_all_resumes(query=None, limit: int = 20):
    if query is None:
        query = {}
    resumes = collection.find(query).sort("created_at", -1).limit(limit)
    return list(resumes)

def get_resume_by_id(id: ObjectId):
    return collection.find_one({"_id": id})