# UserManagement

A comprehensive user management system built with FastAPI, providing secure authentication, CRUD operations, and password reset functionality via email OTP. The application features a modern web interface for easy user administration.

## Features

- **User Authentication**: Secure login and signup with JWT-based session management
- **CRUD Operations**: Create, read, update, and delete user accounts
- **Password Reset**: Secure password recovery using email OTP verification
- **Input Validation**: Comprehensive validation for all user inputs (name, email, mobile, username, password)
- **Security Features**: Password hashing with bcrypt, JWT tokens, security questions
- **Web Interface**: Responsive HTML templates with modern UI design
- **Database Integration**: MySQL database with SQLAlchemy ORM
- **Email Integration**: SMTP-based email sending for OTP notifications

## Technologies Used

- **Backend**: FastAPI (Python web framework)
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens) with python-jose
- **Password Hashing**: bcrypt with passlib
- **Email**: SMTP with Gmail integration
- **Frontend**: HTML5, CSS3, JavaScript with Jinja2 templating
- **Validation**: Regex-based input validation
- **Styling**: Custom CSS with gradients and animations

## Installation

### Prerequisites

- Python 3.8+
- MySQL Server
- Gmail account (for email functionality)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd UserManagement
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   - Create a MySQL database named `fastapi_users`
   - Update database credentials in `database.py` if needed (default: root/1234)

5. **Configure email settings**:
   - Create a `passkey.py` file with your Gmail credentials:
     ```python
     class PassKey:
         SECRET_KEY = "your-secret-key-here"
         ALGORITHM = "HS256"
         ACCESS_TOKEN_EXPIRE_MINUTES = 30
         SENDER_EMAIL = "your-gmail@gmail.com"
         EMAIL_PASSWORD = "your-app-password"
     ```
   - For Gmail, use an App Password instead of your regular password

6. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

7. **Access the application**:
   - Open your browser and go to `http://127.0.0.1:8000`

## Usage

### Web Interface

1. **Registration**: Visit the signup page to create a new account
2. **Login**: Use your credentials to log in
3. **Dashboard**: View and manage all users
4. **Add User**: Create new user accounts
5. **Update User**: Edit existing user information
6. **Delete User**: Remove user accounts
7. **Password Reset**: Use forgot password feature with email verification

### API Endpoints

The application provides the following endpoints:

- `GET /` - Login page
- `GET /signup` - Signup page
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout
- `GET /home` - User dashboard (requires authentication)
- `GET /delete/{id}` - Delete user by ID
- `GET /update/{id}` - Update user form
- `POST /update/{id}` - Update user data
- `GET /add` - Add user form
- `POST /add` - Create new user
- `GET /forgot-password` - Forgot password page
- `POST /forgot-password` - Initiate password reset
- `GET /reset-password` - Reset password page
- `POST /reset-password` - Reset password
- `GET /verify-otp` - OTP verification page
- `POST /verify-otp` - Verify OTP

## How It Works

### Authentication Flow

1. Users register with personal details, username, email, and password
2. Passwords are hashed using bcrypt before storage
3. Login generates a JWT token stored in HTTP-only cookies
4. Protected routes verify the JWT token for authentication

### Password Reset Flow

1. User requests password reset with email or mobile
2. System verifies security question and answer
3. Generates 6-digit OTP and sends via email
4. User verifies OTP (valid for 3 minutes)
5. Allows password reset with new password

### CRUD Operations

- **Create**: Add new users with validation
- **Read**: Display all users in a table format
- **Update**: Modify user details with uniqueness checks
- **Delete**: Remove users from the system

## Database Schema

The `users` table contains the following fields:

- `id` (Integer, Primary Key, Auto-increment)
- `first_name` (String, 50 chars)
- `last_name` (String, 50 chars)
- `username` (String, 50 chars, Unique)
- `email` (String, 100 chars, Unique)
- `mobile` (String, 15 chars, Unique)
- `password` (String, 100 chars, Hashed)
- `security_question` (String, 100 chars)
- `security_answer` (String, 100 chars)
- `created_at` (String, 50 chars)
- `updated_at` (String, 50 chars)
- `created_by` (String, 50 chars)
- `updated_by` (String, 50 chars)
- `otp` (String, 6 chars, Nullable)
- `otp_expiry` (DateTime, Nullable)

## Security

- **Password Hashing**: Uses bcrypt for secure password storage
- **JWT Authentication**: Stateless authentication with expiration
- **Input Validation**: Prevents malicious input with regex validation
- **OTP Security**: Time-limited one-time passwords for password reset
- **Session Management**: Secure cookie-based sessions
- **Uniqueness Checks**: Prevents duplicate usernames, emails, and mobiles

## Validation Rules

- **Name**: 2-20 characters, letters only
- **Username**: 5-15 characters, letters, numbers, underscores
- **Email**: Valid email format
- **Mobile**: Exactly 10 digits
- **Password**: 6-20 characters, must include letters and numbers

## File Structure

```
UserManagement/
├── main.py                 # Main FastAPI application
├── database.py             # Database models and connection
├── crud.py                 # CRUD operations
├── jwt_utils.py            # JWT token utilities
├── smtp_utils.py           # Email sending utilities
├── validation.py           # Input validation functions
├── requirements.txt        # Python dependencies
├── passkey.py              # Secret keys and credentials
├── static/                 # Static files (CSS, JS)
│   └── js/
│       └── toast.js
└── templates/              # HTML templates
    ├── base.html
    ├── login.html
    ├── signup.html
    ├── home.html
    ├── add.html
    ├── update.html
    ├── forgot_password.html
    ├── reset_password.html
    ├── verify_otp.html
    ├── email_otp.html
    └── messages.html
```
---

Built with ❤️ using FastAPI
