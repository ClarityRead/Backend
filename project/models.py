from django.db import models
from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

host = os.getenv('HOST')
port = os.getenv('PORT')
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')

client = MongoClient(host=host,
                        port=int(port),
                        username=username,
                        password=password
                    )
db_handle = client['backend']

print("Connected to MongoDB database")