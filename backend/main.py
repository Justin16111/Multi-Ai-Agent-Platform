from fastapi import FastAPI, UploadFile, File, WebSocket, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pypdf import PdfReader

from database import chat_collection, user_collection, memory_collection
from auth import hash_password, verify_password, create_access_token

import requests
import os
import uuid
import tempfile
import io
from datetime import datetime
from jose import jwt

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.getenv("SECRET_KEY", "mysecretkey123")
ALGORITHM = "HS256"

class ChatRequest(BaseModel):
    prompt: str
    agent: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

def get_current_user_email(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token properties")
        return email
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@app.get("/")
def home():
    return {"message": "Multi AI Platform Backend Running"}

@app.post("/register")
def register(data: RegisterRequest):
    existing_user = user_collection.find_one({"email": data.email.strip().lower()})
    if existing_user:
        return {"success": False, "message": "User already exists"}

    try:
        plain_password_string = str(data.password)
        hashed_result = hash_password(plain_password_string)

        user_collection.insert_one({
            "username": data.username.strip(),
            "email": data.email.strip().lower(),
            "password": hashed_result
        })
        return {"success": True, "message": "User registered successfully"}
    except Exception as e:
        return {"success": False, "message": f"Encryption Error: {str(e)}"}

@app.post("/login")
def login(data: LoginRequest):
    user = user_collection.find_one({"email": data.email.strip().lower()})
    if not user or not verify_password(str(data.password), user["password"]):
        return {"success": False, "message": "Invalid credentials"}

    token = create_access_token({"email": user["email"]})
    return {"success": True, "token": token}

@app.post("/chat")
def chat(data: ChatRequest, authorization: str = Header(None)):
    try:
        user_email = get_current_user_email(authorization)
    except Exception:
        user_email = "anonymous"

    agent_prompts = {
        "Research Agent": "You are a research expert. Provide deep analytical dives, citations, and structural insights.",
        "Coding Agent": "You are a senior software engineer. Write clean, modular, and performance-optimized code blocks.",
        "Summarizer Agent": "You are a summarization assistant. Extract key points, actions, and bulleted takeaways concisely.",
        "PDF Analysis Agent": "You are a document extraction expert. Analyze, parse, and answer questions based on the document text provided.",
        "Productivity Agent": "You are a productivity layout strategist. Generate task breakdowns, daily schedules, and time management blueprints."
    }

    system_prompt = agent_prompts.get(data.agent, "You are a helpful assistant.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "error": "GEMINI_API_KEY is missing from .env"}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key.strip()}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": data.prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.7}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"success": False, "error": f"Google Gateway returned status {response.status_code}"}

        result = response.json()
        ai_response = result['candidates'][0]['content']['parts'][0]['text']

        chat_collection.insert_one({
            "user_email": user_email,
            "agent": data.agent,
            "prompt": data.prompt,
            "response": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        })

        try:
            memory_collection.insert_one({
                "conversation": f"User: {data.prompt}\nAI: {ai_response}",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception:
            pass

        return {"success": True, "response": ai_response}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/history")
def get_history(authorization: str = Header(None)):
    try:
        user_email = get_current_user_email(authorization)
        query = {"user_email": user_email}
    except Exception:
        query = {}

    chats = []
    try:
        for chat in chat_collection.find(query).sort("timestamp", -1):
            chats.append({
                "id": str(chat.get("_id")),
                "agent": chat.get("agent"),
                "prompt": chat.get("prompt"),
                "response": chat.get("response"),
                "timestamp": chat.get("timestamp")
            })
        return {"success": True, "history": chats}
    except Exception as e:
        return {"success": False, "error": str(e)}

import io  # <-- Make sure this import is added at the very top of main.py

# ==========================
# PDF FILE UPLOAD & ANALYSES (FIXED FOR STREAM ERRORS)
# ==========================

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # BLOCK INVALID FILE EXTENSIONS IMMEDIATELY
    if not file.filename.lower().endswith('.pdf'):
        return {
            "success": False, 
            "error": "Invalid file type. Please upload a genuine PDF file."
        }

    try:
        file_bytes = await file.read()
        
        # CHECK THE INTERNAL FILE HEADERS
        if file_bytes.startswith(b'PK\x03\x04'):
            return {
                "success": False,
                "error": "Validation Error: This file is a Word Document (.docx) or ZIP file disguised as a PDF. Please upload a real PDF."
            }
            
        if not file_bytes.startswith(b'%PDF'):
            return {
                "success": False,
                "error": "Validation Error: Invalid PDF structure header. Please upload a standard PDF."
            }

        if not file_bytes:
            return {"success": False, "error": "Uploaded file is completely empty."}
            
        pdf_stream = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_stream)
        
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            return {
                "success": False, 
                "error": "Could not extract text. The PDF might be scanned or comprised entirely of images."
            }

        return {
            "success": True,
            "text": text.strip(),
            "characters": len(text),
            "preview": text[:1000]
        }

    except Exception as pdf_error:
        print(f"❌ PDF Parsing Crash: {str(pdf_error)}")
        return {
            "success": False,
            "error": f"Failed to parse document structure: {str(pdf_error)}"
        }
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Realtime: {data}")