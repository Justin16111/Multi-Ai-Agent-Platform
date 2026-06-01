import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv

# Load variables from the hidden .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

# CRITICAL FIX: Removed the hardcoded fallback password string to keep it completely hidden
if not MONGO_URI:
    raise ValueError("❌ CRITICAL ERROR: MONGO_URI is missing from your environment variables!")

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