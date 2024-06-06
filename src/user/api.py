from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from src.user.schemas import UserCreate, UserLogin, UserUpdate, UpdatePassword
from src.user.models import User
from database import get_db
from passlib.context import CryptContext 
from src.user.token import create_token, create_refresh_token, decode_token
import bcrypt

router = APIRouter()

# Register New User
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(request: UserCreate, db: get_db):
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    hashed_password = bcrypt.hashpw(request.password.encode(), bcrypt.gensalt())
    user = User(
        firstname=request.firstname,
        lastname=request.lastname,
        username=request.username,
        email=request.email,
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
                'token_type': 'Bearer' 
            }

# Login User
@router.post("/login/", status_code=status.HTTP_200_OK)
def login(request: UserLogin, db: get_db):
    email = request.email
    password = request.password
    user = db.query(User).filter(User.email == email).first()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if user and pwd_context.verify(password, user.password):

        access_token = create_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})

        return {'name': user.firstname + ' ' + user.lastname,
                'email': user.email,
                'access_token' : access_token,
                'refresh_token' : refresh_token,
                'token_type': 'Bearer'
                }
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
# Update Password
@router.patch("/update_password", status_code=status.HTTP_200_OK)
def update_password(request: UpdatePassword, db: get_db , token: str = Depends(decode_token)):
    email = request.email
    password = request.old_password
    user = db.query(User).filter(User.email == email).first()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    if user and pwd_context.verify(password, user.password):
        hashed_password = bcrypt.hashpw(request.new_password.encode(), bcrypt.gensalt())
        user.password = hashed_password.decode()
        db.commit()
        return {'Password Updated Successfully'}
    else:
        raise HTTPException(status_code=401, detail="Incorrect email or password")


@router.get("/get_user/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: str, db: get_db, token: str = Depends(decode_token)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.patch("/update_user/{user_id}", status_code=status.HTTP_200_OK)
def update_user_details(user_id: str,request: UserUpdate , db: get_db, token: str = Depends(decode_token)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    for key, value in request.model_dump().items():
        setattr(user, key, value)
    db.commit()
    return {'Updated Successfuslly'}


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: str, db: get_db, token: str = Depends(decode_token)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    user.deleted_at = datetime.now()
    db.commit()
    return {'Deleted Successfully'}
