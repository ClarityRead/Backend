from pymongo import MongoClient
import os 
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
import jwt
from datetime import datetime, timedelta
from backend import settings 

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

def GetUserObjectByUsername(username):
    users = GetUsers()
    user_data = users.find_one({"username": username})

    return user_data

def AddUser(username, password, email):
    users = GetUsers()

    if users is None:
        print("Cannot create a new user - MongoDB is not connected")
        return     

    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    entry = {"username": username, "password": hashed_pw, "email": email}
    users.update_one({"username": username}, {'$set': entry}, upsert=True)

def Login(username, entered_password):
    user_data = GetUserObjectByUsername(username)

    if not user_data: 
        print(f"User {username} not found.")

        return False
    
    entered_pw = entered_password.encode('utf-8')
    stored_pw = user_data['password'].encode('utf-8')    
    correct = bcrypt.checkpw(entered_pw, stored_pw)
    
    if correct:
        print(f"Password for {username} verified successfully.")
        return True
    else:
        print(f"Incorrect password for {username}.")
        return False

def CreateJWTToken(username):
    user_data = GetUserObjectByUsername(username)

    if not user_data:
        return

    payload = {
        "user_id": str(user_data['_id']),
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return token