import hashlib
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    """Hashes a plain text password string cleanly with zero length limits."""
    # Convert whatever comes in strictly to a clean string format
    clean_password = str(password).strip()
    
    # Use standard SHA256 to hash the text safely without passlib's 72-byte firewall barrier
    return hashlib.sha256(clean_password.encode('utf-8')).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Compares the incoming plain text login password against the database string."""
    clean_password = str(password).strip()
    return hashlib.sha256(clean_password.encode('utf-8')).hexdigest() == hashed

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )