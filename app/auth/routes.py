from fastapi import APIRouter, Depends, HTTPException,BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.auth import models, schemas, utils
from app.core.database import Base, engine
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.auth.models import PasswordResetToken, User
from app.auth.schemas import ForgotPasswordRequest, ResetPasswordRequest
from datetime import datetime
from app.core.logging_utils import logger
import uuid
from app.core.config import settings
from app.core.email_utils import send_email

Base.metadata.create_all(bind=engine) #this will create all the tables

router = APIRouter(prefix="/auth", tags=["Authentication"]) # all authentication routes with the prefix of /auth

def get_db():
    db = SessionLocal()
    try:
        yield db #this will yeild the database
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")
# Signup Route
@router.post("/signup", response_model=schemas.ShowUser)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)): #injects db
    domain = user.email.split('@')[-1]
    allowed_endings = (".com", ".in", ".org", ".net", ".co")

    if not domain.endswith(allowed_endings): #validation for email domain
        raise HTTPException(
			status_code=400,
            detail= f"Email with {domain} is not allowed!!!"
		)

    db_user = db.query(models.User).filter(models.User.email == user.email).first() #this checks whether the email is already there
    if db_user:
        logger.warning(f"Signup failed: email {user.email} already registered.")
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = utils.hash_password(user.password)
    new_user = models.User(
        name=user.name, email=user.email, hashed_password=hashed, role=user.role
    )
    db.add(new_user) #add in the database and commit the change
    db.commit()
    db.refresh(new_user)
    logger.info(f"New signup - email: {user.email}")
    return new_user

# Signin Route
@router.post("/signin", response_model=schemas.Token)
def signin(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = utils.create_access_token(data={"sub": user.email})
    logger.info(f"Login Successfully - email: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

#Dependency to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        logger.error("JWT decode error during authentication.")
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

#Rolebased access check for admin
def require_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

#Forget Password Route
@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    bg_task:BackgroundTasks,
    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    token = str(uuid.uuid4())
    reset_token = PasswordResetToken(user_id=user.id, token=token)
    db.add(reset_token)
    db.commit()

    # sending email

    email_body = f"""
    Hi {user.name},

    We recieved a request to reset the password from you.

    This is you reset token : {token}

    If you didn't request, Please ignore this email!!

    Thanks,
    Team
    """

    bg_task.add_task(
		send_email,
        subject="Reset Your Password!!",
        recipient = user.email,
        body=email_body
	)
    logger.info(f"Password reset requested - email: {user.email}")
    return {"message": "Password reset email sent successfully!!!"}

# Reset Password Route
@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_entry = db.query(PasswordResetToken).filter(PasswordResetToken.token == data.token).first()

    if not token_entry or token_entry.used or token_entry.expiration_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == token_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = utils.hash_password(data.new_password)
    token_entry.used = True
    db.commit()

    logger.info(f"Password reset successful - email: {user.email}")
    return {"message": "Password reset successful"}