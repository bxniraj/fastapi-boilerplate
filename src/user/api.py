from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.user import models , schemas
from database import get_db
from passlib.context import CryptContext 
from src.user.token import create_token, create_refresh_token
import bcrypt

router = APIRouter()

# Register New User
@router.post("/register")
def create_user(user_request: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_email = db.query(models.User).filter(models.User.email == user_request.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    existing_username = db.query(models.User).filter(models.User.username == user_request.username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    hashed_password = bcrypt.hashpw(user_request.password.encode(), bcrypt.gensalt())
    user = models.User(
        firstname=user_request.firstname,
        lastname=user_request.lastname,
        username=user_request.username,
        email=user_request.email,
        password=hashed_password.decode(),
    )
    db.add(user) 
    db.commit()
    db.refresh(user)

    access_token = create_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return {'email': user.email,
                'access_token' : access_token,
                'refresh_token' : refresh_token,
                'token_type': 'Bearer' }


@router.post("/login/")
def login(request: schemas.UserLogin, db: Session = Depends(get_db)):
    email = request.email
    password = request.password
    user = db.query(models.User).filter(models.User.email == email).first()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if user and pwd_context.verify(password, user.password):

        access_token = create_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})

        return {'name': user.firstname + ' ' + user.lastname,
                'email': user.email,
                'access_token' : access_token,
                'refresh_token' : refresh_token,
                'token_type': 'Bearer'}
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
