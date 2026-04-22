import jwt
from datetime import datetime,timedelta,timezone

SECRET_KEY="bfb591110c7fae5316c69c4898872244bc91468213c279342734c1fba4a26d3e"
ALGORITHM="HS256"
ACCESS_TIMEOUT_EXPIRE_MINUTES=30

def create_access_token(data:dict,expires:timedelta|None=None):
    to_encode=data.copy()
    if expires:
        expire=datetime.now(timezone.utc)+ expires
    else:
        expire=datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TIMEOUT_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

def verify_token(token:str,credentials_exception):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        user_email=payload.get("sub")
        if not user_email:
            raise credentials_exception
        else:
            return user_email
    except jwt.InvalidTokenError:
        raise credentials_exception