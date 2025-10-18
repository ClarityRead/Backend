from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from pathlib import Path

"""
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")"""

MONGO_URI = "mongodb+srv://new_xander:thenewpassword@cluster0.nk0qa3t.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

_client = None
_db_handle = None

def get_papers_collection():
    """Get the papers collection, establishing connection if needed"""
    global _client, _db_handle
    
    try:
        if _client is None:
            if not MONGO_URI:
                return None
                
            _client = MongoClient(MONGO_URI)
            # Test the connection
            _client.admin.command('ping')
            _db_handle = _client["backend"]
        
        return _db_handle["papers"]
    except Exception as e:
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