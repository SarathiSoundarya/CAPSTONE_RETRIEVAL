#Adding auth and rate limiting to fastapi langchain workflows to ensure only authorized person can access.

# Secure fast api endpoints with JWT authentication and rate limiting using the `fastapi` library.

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt #decoding and encoding JWT tokens
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
load_dotenv()


#JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 #Token expiration time


users_db = {
    "user":{"password":"pass", "role":"user"},
    "admin":{"password":"admin","role":"admin"}
}
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print(to_encode)
    print(f"ENCODING SECRET KEY:{SECRET_KEY}")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token") #"Expect a token in request headers for protected endpoints, and the token can be obtained from the /token endpoint"


def get_current_user(token: str = Depends(oauth_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    print(f"DECODING SECRET KEY:{SECRET_KEY}")
    print(f"TOKEN In Authorization:{token}")
    try:
        print("Decoding payload")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload:{payload}")
        username = payload.get("sub")
        role= payload.get("role")
        if username is None:
            print("Username is none!")
            raise credentials_exception
        return {"username":username, "role":role}
    except JWTError:
        print("JWT Token error")
        raise credentials_exception
    return username

def require_admin(user:dict = Depends(get_current_user)):
    if user["role"]!="admin":
        print("Error, admin access required! ")
    return user