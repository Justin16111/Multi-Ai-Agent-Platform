 Multi-Agent AI Productivity & Document Analysis Platform

An advanced full-stack AI Engineering platform designed to provide modular, context-aware assistance utilizing an isolated multi-agent ecosystem. Built as part of the AIML Engineering Internship curriculum.

🚀 Key Architectural Features
- Multi-Agent Engine: Integrates Google Gemini 2.5 Flash leveraging tailored system instructions across 5 specific domains (Research, Software Engineering, Summarization, Document Analysis, and Productivity Strategy).
- Secure Authentication & Session State:** Custom SHA-256 cryptographic credential hashing coupled with stateless JSON Web Tokens (JWT) to secure user boundaries.
- Robust Storage Architecture:** Multi-collection database mapping (Users, Chat Logs, System Memory) running on MongoDB Atlas with automated SSL verification fallbacks.
- Buffer-Isolated PDF Extraction:** Direct memory-stream text parsing engine using `io.BytesIO` and `pypdf` to inject file data contexts instantly into agent prompts.

🛠️ Tech Stack & Foundations
- Frontend:React, Tailwind CSS, Axios, React Router Dom
- Backend: FastAPI (Python), Uvicorn Web Server, PyJWT, Passlib, hashlib
- Database: MongoDB Atlas (via PyMongo)
- AI Gateway: Google Gemini API REST Clusters

📋 Standard API Directory Layout
- `POST /register` - Processes credential sanitization and unique database indexing.
- `POST /login` - Evaluates match vectors and delivers cryptographic authorization tokens.
- `POST /chat` - Central gateway routing custom payload structures to targeted LLM pipelines.
- `GET /history` - Queries isolated user conversation streams sorted by automated timestamps.
- `POST /upload-pdf` - Ingests raw document binaries to emit parsed plain text context blocks.

🔧 Installation & Local Setup

1. Backend Infrastructure Setup
```bash
cd backend
python -m venv venv
# Activate workspace environment
# On Windows:
.\venv\Scripts\activate

pip install -r requirements.txt
uvicorn main:app --reload