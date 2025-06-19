from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from datetime import datetime, timedelta
from app.core.database import Base
from enum import Enum as PyEnum
import uuid

class UserRole(PyEnum):
    admin = "admin"
    user = "user"

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)

class PasswordResetToken(Base):
    __tablename__ = "passwordResets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, default=lambda: str(uuid.uuid4())) # uuid token is generated for 15 minutes
    expiration_time = Column(DateTime, default=lambda: datetime.now() + timedelta(minutes=15))
    used = Column(Boolean, default=False)