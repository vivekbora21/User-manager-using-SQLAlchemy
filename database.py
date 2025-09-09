from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

#Database connection
engine = create_engine("mysql+pymysql://root:1234@localhost/fastapi_users")
Base = declarative_base()
Session = sessionmaker(bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    mobile = Column(String(15), unique=True)
    password = Column(String(100))
    security_question = Column(String(100))
    security_answer = Column(String(100))
    created_at = Column(String(50))
    updated_at = Column(String(50))
    created_by = Column(String(50))
    updated_by = Column(String(50))
    otp = Column(String(6), nullable=True)
    otp_created_at = Column(String(50), nullable=True)

#Create table if not present
Base.metadata.create_all(engine) 

