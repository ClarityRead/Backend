from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI") 
client = MongoClient(MONGO_URI)
db_handle = client["backend"]
papers = db_handle["papers"]

def InsertFiles(data): 
    for entry in data: 
        papers.update_one({"paper_id": entry["paper_id"]}, {'$set': entry}, upsert=True)

print("Connected to MongoDB database")