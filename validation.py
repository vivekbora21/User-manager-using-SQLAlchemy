from fastapi import HTTPException
import re

def validate_name(name: str) -> bool:
    if not (2 <= len(name) <= 20):
        raise HTTPException(status_code=400, detail="It must be 2-20 characters long")
    if not re.match(r"^[A-Za-z]+$", name):
        raise HTTPException(status_code=400, detail="It can only contain letters")
    return name

def validate_password(password: str) -> bool:
    if not (6 <= len(password) <= 20):
        raise HTTPException(status_code=400, detail="Password must be between 8-15 characters")
    if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,20}$", password):
        raise HTTPException(status_code=400, detail="Password must be 6-20 characters, include letters and numbers.")
    return password

def validate_mobile(mobile: str) -> bool:
    if not re.match(r"^[0-9]{10}$", mobile):
        raise HTTPException(status_code=400, detail="Mobile number must be exactly 10 digits.")
    return mobile

def validate_username(username: str) -> bool:
    if not (5 <= len(username) <= 15):
        raise HTTPException(status_code=400, detail="Username must be between 5-15 characters.")
    if not re.match(r"^[A-Za-z0-9_]+$", username):
        raise HTTPException(status_code=400, detail="Username can only contain letters, numbers, and underscores.")
    return username

def validate_email(email: str) -> bool:
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    return email