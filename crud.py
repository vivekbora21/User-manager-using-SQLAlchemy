from database import User, Session

class CRUD:
    User = User  # Reference to the User model

    def __init__(self):
        self.Session = Session

    # Add new user
    def add(self, first_name, last_name, username, email, mobile, password, security_question, security_answer):
        with self.Session() as session:
            new_user = self.User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                mobile=mobile,
                password=password,
                security_question=security_question,
                security_answer=security_answer
            )
            session.add(new_user)
            session.commit()

    # Update user by id
    def update(self, id, first_name, last_name, username, email, mobile, password=None, security_question=None, security_answer=None):
        with self.Session() as session:
            user = session.get(self.User, id)
            if user:
                user.first_name = first_name
                user.last_name = last_name
                user.username = username
                user.email = email
                user.mobile = mobile

                # Only update password if provided
                if password:
                    user.password = password  

                # Only update security question/answer if provided
                if security_question:
                    user.security_question = security_question
                if security_answer:
                    user.security_answer = security_answer

                session.commit()

    # Delete user by id
    def delete(self, id):
        with self.Session() as session:
            user = session.get(self.User, id)
            if user:
                session.delete(user)
                session.commit()

    # Show all users
    def show_all(self):
        with self.Session() as session:
            return session.query(self.User).all()

    # Find by email
    def get_user_by_email(self, email: str):
        with self.Session() as session:
            return session.query(self.User).filter(self.User.email == email).first()

    # Find by username (for login)
    def get_user_by_username(self, username: str):
        with self.Session() as session:
            return session.query(self.User).filter(self.User.username == username).first()

    # Find by mobile
    def get_user_by_mobile(self, mobile: str):
        with self.Session() as session:
            return session.query(self.User).filter(self.User.mobile == mobile).first()

    # Find by id
    def get_user_by_id(self, id: int):
        with self.Session() as session:
            return session.get(self.User, id)

    def update_password(self, user_id: int, new_password: str):
        with self.Session() as session:
            user = session.get(self.User, user_id)
            if user:
                user.password = new_password
                session.commit()
                return True
            return False
    
    def update_otp(self, user_id: int, otp: str):
        with self.Session() as session:
            user = session.get(self.User, user_id)
            if user:
                user.otp = otp
                session.commit()
                return True
            return False

    def save(self, user):
        with self.Session() as session:
            session.merge(user)
            session.commit()
