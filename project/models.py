from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from pathlib import Path
import bcrypt

"""
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")"""

MONGO_URI = "mongodb+srv://new_xander:thenewpassword@cluster0.nk0qa3t.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

_client = None
_db_handle = None

def CreateDbHandle():
    global _client, _db_handle

    _client = MongoClient(MONGO_URI)
    _db_handle = _client["backend"]

def get_papers_collection():
    global _client, _db_handle
    
    try:
        if _client is None:
            if not MONGO_URI:
                return None
                
            CreateDbHandle()
        
        return _db_handle["papers"]
    except Exception as e:
        return None

def GetUsers():
    global _client, _db_handle

    try:
        if _client is None:
            if not MONGO_URI:
                return None

            CreateDbHandle()

        return _db_handle["users"]
    except Exception as e:
        return None

def InsertFiles(data): 
    papers = get_papers_collection()

    if papers is None:
        print("Cannot insert files - MongoDB not connected")
        return
        
    for entry in data: 
        papers.update_one({"paper_id": entry["paper_id"]}, {'$set': entry}, upsert=True)

def DoesUserExist(username): 
    users = GetUsers()

    if users is None:
        print("Cannot create a new user - MongoDB is not connected")
        return     

    return users.count_documents({"username": username}) > 0

def AddUser(username, password, email):
    users = GetUsers()

    if users is None:
        print("Cannot create a new user - MongoDB is not connected")
        return     

    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt)

    entry = {"username": username, "password": password, "email": email}
    users.update_one({"username": username}, {'$set': entry}, upsert=True)

def Login(username, password):
    """user_data = users_collection.find_one({"username": username})
    
    if user_data:
        stored_hashed_password = user_data['password']
        stored_salt = user_data['salt']
        
        # Hash the provided password with the stored salt
        entered_hashed_password = bcrypt.hashpw(password.encode('utf-8'), stored_salt)
        
        # Compare the hashes
        if entered_hashed_password == stored_hashed_password:
            print(f"Password for {username} verified successfully.")
            return True
        else:
            print(f"Incorrect password for {username}.")
            return False
    else:
        print(f"User {username} not found.")
        return False"""