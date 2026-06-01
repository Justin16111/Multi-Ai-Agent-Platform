import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    MONGO_URI = "mongodb+srv://jus4802_db_user:3NXU4QgYnNnCFNOG@cluster0.fhfdi9z.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"⚠️ Primary SSL connection failed: {e}. Trying fallback validation...")
    client = MongoClient(MONGO_URI, tlsAllowInvalidCertificates=True)

db = client["ai_productivity_platform"]

user_collection = db["users"]
chat_collection = db["chats"]
memory_collection = db["ai_memory"]