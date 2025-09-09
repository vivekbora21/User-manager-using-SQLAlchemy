from fastapi import FastAPI, HTTPException, Request, Form, Depends, status, Cookie
from passlib.context import CryptContext
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from crud import CRUD
from datetime import datetime, timedelta
from jwt_utils import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
import random
from typing import Optional
from smtp_utils import send_email
from validation import validate_name, validate_password, validate_mobile, validate_username


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
db = CRUD()
templates = Jinja2Templates(directory="templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Jinja templates
def render_templates(name: str, request: Request, **context):
    response = templates.TemplateResponse(name, {"request": request, **context})
    return response


#--- Password Hashing ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
        return pwd_context.verify(plain_password, hashed_password)
    else:
        return plain_password == hashed_password
    
#--- Authenticate User ---
def authenticate_user(username: str, password: str):
    user = db.get_user_by_username(username) 
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

#--- JWT Dependency ---
def get_current_user(access_token: str = Cookie(None)):
    if access_token is None:
        return None
    payload = decode_access_token(access_token)
    if payload is None:
        return None
    username = payload.get("sub")
    if username is None:
        return None
    user = db.get_user_by_username(username)
    if user is None:
        return None
    return user



#--- Routes ---
# to render login page
@app.get("/", response_class=HTMLResponse)
def get_login(request: Request):
    return render_templates("login.html", request)

# to render signup page
@app.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    return render_templates("signup.html", request)

#--- Logout user ---
@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/?msg=You have been logged out successfully", status_code=303)
    response.delete_cookie("access_token")
    return response

#--- Login user ---
@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html",{"request": request, "error": "Invalid username or password!"})
    access_token = create_access_token(data={"sub": user.username})
    response =  RedirectResponse("/home?msg= User loggedin successfully",status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True,
                        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return response

#--- Signup user ---
@app.post("/signup")
async def post_signup(request: Request, first_name: str = Form(...), last_name: str = Form(...), username: str = Form(...),
                       email: str = Form(...), mobile: str = Form(...),
                      password: str = Form(...), security_question: str = Form(...), security_answer: str = Form(...)):
    try:
        first_name = validate_name(first_name)
        last_name = validate_name(last_name)
        password = validate_password(password)
        username = validate_username(username)
        mobile = validate_mobile(mobile)
    except HTTPException as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": e.detail})
    try:
        hashed_password = get_password_hash(password)
        db.add(first_name, last_name, username, email, mobile, hashed_password, security_question, security_answer, datetime.now().isoformat(),datetime.now().isoformat(), username, username)
        return RedirectResponse(url="/?msg=Signup successful. Please Login", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("signup.html", {"request": Request, "error": str(e)})

# to render home page with users list
@app.get("/home", response_class=HTMLResponse)
async def get_users(request: Request, current_user= Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/?msg=You need to login first", status_code=303)
    try:
        users = db.show_all()
        return render_templates("home.html", request, users=users, current_user=current_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    
#--- delete User ---
@app.get("/delete/{id}")
async def delete_user(id: int, current_user= Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/?msg=You need to login first", status_code=303)
    try:
        db.delete(id)
        return RedirectResponse(url="/home?msg=User deleted successfully", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# --- Show Update Form (prefilled) ---
@app.get("/update/{id}", response_class=HTMLResponse)
async def get_update_form(request: Request, id: int, current_user= Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/?msg=You need to login first", status_code=303)
    user = db.get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return render_templates("update.html", request, user=user)

# --- Handle Update Submission ---
@app.post("/update/{id}")
async def post_update(request: Request,id: int,first_name: str = Form(...),last_name: str = Form(...),
                        username: str = Form(...), email: str = Form(...), mobile: str = Form(...),
                        password: str = Form(None), security_question: str = Form(None), security_answer: str = Form(None), 
                        current_user= Depends(get_current_user)):
    
    if current_user is None:
        return RedirectResponse(url="/?msg=You need to login first", status_code=303)
    try:
        first_name = validate_name(first_name)
        last_name = validate_name(last_name)
        username = validate_username(username)
        mobile = validate_mobile(mobile)
        if password:
            password = validate_password(password)
    except HTTPException as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": e.detail})
    
    try:
        # Fetch existing user
        existing_user = db.get_user_by_id(id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check uniqueness (ignore current user’s own values)
        if db.get_user_by_username(username) and username != existing_user.username:
            return render_templates("update.html", request, user=existing_user,
                                    error=" Username already exists")
        if db.get_user_by_email(email) and email != existing_user.email:
            return render_templates("update.html", request, user=existing_user,
                                    error=" Email already exists")
        if db.get_user_by_mobile(mobile) and mobile != existing_user.mobile:
            return render_templates("update.html", request, user=existing_user,
                                    error=" Mobile number already exists")

        # Hash password if provided
        hashed_password = get_password_hash(password) if password else None

        # Update user
        db.update(id, first_name, last_name, username, email, mobile,
                  hashed_password, security_question, security_answer, 
                  datetime.now().isoformat(), current_user.username)
        return RedirectResponse(url="/home?msg=User updated succesfully", status_code=303)

    except Exception as e:
        return render_templates("update.html", request, user=existing_user, error=f"Error: {str(e)}")


# --- Add User ---
@app.get("/add", response_class=HTMLResponse)
async def get_add_form(request: Request):
    return render_templates("add.html", request)

@app.post("/add")
async def add_user(request: Request, first_name: str = Form(...), last_name: str = Form(...), username: str = Form(...),
                   email: str = Form(...), mobile: str = Form(...), password: str = Form(...),
                     security_question: str = Form(...), security_answer: str = Form(...),
                     current_user= Depends(get_current_user)):
    if current_user is None:
        return RedirectResponse(url="/?msg=You need to login first", status_code=303)
    try:
        first_name = validate_name(first_name)
        last_name = validate_name(last_name)
        password = validate_password(password)
        username = validate_username(username)
        mobile = validate_mobile(mobile)
    except HTTPException as e:
        return templates.TemplateResponse("signup.html", {"request": request, "error": e.detail})
    
    try:
        # Check uniqueness
        if db.get_user_by_username(username):
            return render_templates("add.html", request, error="Username already exists")
        if db.get_user_by_email(email):
            return render_templates("add.html", request, error="Email already exists")
        if db.get_user_by_mobile(mobile):
            return render_templates("add.html", request, error="Mobile number already exists")

        # Hash password and add user
        hashed_password = get_password_hash(password)
        db.add(first_name, last_name, username, email, mobile,hashed_password, security_question, security_answer, 
               datetime.now().isoformat(),datetime.now().isoformat(), current_user.username, current_user.username)
        return RedirectResponse(url="/home?msg=User added successfully", status_code=303)

    except Exception as e:
        return render_templates("add.html", request, error=f"Error: {str(e)}")
    
#--- forgot password ---
@app.get("/forgot-password", response_class=HTMLResponse)
async def get_forgot_password(request: Request):
    return render_templates("forgot_password.html", request)


@app.post("/forgot-password")
async def forgot_password(request: Request, option: str = Form(...), identifier: str = Form(...),
                          security_question: str = Form(...), security_answer: str = Form(...)):
    identifier = identifier.strip()
    if option == "email":
        identifier = identifier.lower()

    user = None
    if option == "email":
        user = db.get_user_by_email(identifier)
    elif option == "mobile":
        user = db.get_user_by_mobile(identifier)

    if not user:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "User not found"})

    if user.security_question != security_question or user.security_answer != security_answer:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Security check failed"})

    # Generate OTP
    otp = str(random.randint(100000, 999999))
    otp_expiry = datetime.utcnow() + timedelta(minutes=3)  # OTP valid for 3 minutes
    db.update_otp(user.id, otp, otp_expiry)
    subject = "Your OTP for Password Reset"
    body = f"Your OTP is: {otp}"
    if not send_email(user.email, subject, body):
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Failed to send OTP email"})

    return templates.TemplateResponse("verify_otp.html", {"request": request, "option": option, "identifier": identifier})

@app.post("/reset-password")
async def reset_password(request: Request, option: str = Form(...), identifier: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...)):
    if new_password != confirm_password:
        return templates.TemplateResponse("reset_password.html",{
            "request": request, "error": "Passwords do not match", "option": option, "identifier": identifier}
        )
    hashed_password = get_password_hash(new_password)

    # Get user by email or mobile
    user = None
    if option == "email":
        user = db.get_user_by_email(identifier.strip().lower())
    elif option == "mobile":
        user = db.get_user_by_mobile(identifier.strip())

    if not user:
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "User not found", "option": option, "identifier": identifier}
        )

    # Update only password
    db.update_password(user.id, hashed_password)
    return RedirectResponse(url="/?msg=Password reset successful", status_code=303)

@app.get("/verify-otp", response_class=HTMLResponse)
async def get_verify_otp(request: Request):
    # If accessed directly, redirect to forgot-password
    return RedirectResponse(url="/forgot-password", status_code=303)

@app.post("/verify-otp")
async def verify_otp(request: Request, option: Optional[str] = Form(None), identifier: Optional[str] = Form(None), otp: str = Form(...)):
    if not option or not identifier:
        return RedirectResponse(url="/forgot-password", status_code=303)

    identifier = identifier.strip()
    if option == "email":
        identifier = identifier.lower()

    user = None
    if option == "email":
        user = db.get_user_by_email(identifier)
    elif option == "mobile":
        user = db.get_user_by_mobile(identifier)

    if not user or user.otp != otp.strip():
        # OTP invalid, stay on the same page with error
        return templates.TemplateResponse("verify_otp.html", {"request": request, "option": option, "identifier": identifier, "error": "Invalid OTP"})

    if datetime.utcnow() > user.otp_expiry:
        db.update_otp(user.id, None, None)
        return templates.TemplateResponse("forgot_password.html", {"request": request, "option": option, "identifier": identifier, "error": "OTP has expired"})
    
    # OTP matched, clear it
    db.update_otp(user.id, None, None)

    # Redirect to login page with optional message
    return templates.TemplateResponse("reset_password.html",{
        "request": request, "option": option, "identifier": identifier}
    )
