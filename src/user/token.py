import os
import jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Header
from datetime import datetime, timedelta
from database import get_db
from src.user import models

load_dotenv(os.getenv("ENV_FILE", ".env"))

# Access Token
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=1)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"])
    return token

# Refresh Token
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire_minutes_expr = os.environ["Refresh_Token_Expire_Minutes"]
    expire_minutes = eval(expire_minutes_expr)
    expire = timedelta(minutes=expire_minutes) + datetime.now()
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, os.environ["SECRET_KEY"], algorithm=os.environ["ALGORITHM"])
    return token

# Decode Token
def decode_token(authorization: str = Header(), db: Session = Depends(get_db)):
    try:
        parts = authorization.split(' ')
        verify = parts[1]
        payload = jwt.decode(verify, os.environ["SECRET_KEY"], algorithms=os.environ["ALGORITHM"])
        # Extract the email from the payload
        email_ext = payload.get("sub")
        user_ext = db.query(models.User).filter(models.User.email == email_ext).first()
        if not email_ext:
            raise HTTPException(status_code=400, detail="Email not found in the token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# Refresh Token
def refresh_access_token(refresh_token: str = Header(), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, os.environ["SECRET_KEY"], algorithms=[os.environ["ALGORITHM"]])
        email = payload.get("sub")
        user = db.query(models.User).filter(models.User.email == email).first()
        if user:
            # Generate a new access token
            access_token = create_token(data={"sub": user.email})
            return {"access_token": access_token}
        else:
            raise HTTPException(status_code=401, detail="User not found")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")