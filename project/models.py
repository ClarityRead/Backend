from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")

# Global variables for MongoDB connection
_client = None
_db_handle = None

def get_papers_collection():
    """Get the papers collection, establishing connection if needed"""
    global _client, _db_handle
    
    try:
        if _client is None:
            _client = MongoClient(MONGO_URI)
            _db_handle = _client["backend"]
            print("Connected to MongoDB database")
        
        return _db_handle["papers"]
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

def InsertFiles(data): 
    papers = get_papers_collection()
    if papers is None:
        print("Cannot insert files - MongoDB not connected")
        return
        
    print("Inserting files")
    print(data)
    for entry in data: 
        print(entry)
        papers.update_one({"paper_id": entry["paper_id"]}, {'$set': entry}, upsert=True)