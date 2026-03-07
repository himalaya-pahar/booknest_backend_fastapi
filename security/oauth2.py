from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,status
from typing import Annotated
import database as d_b,schemas
from sqlmodel import select
from security import token

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(db:d_b.SessionDep,data:Annotated[str,Depends(oauth2_scheme)])->schemas.ShowUser:
    credentials_exception= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    user_email=token.verify_token(data,credentials_exception)
    user=db.exec(select(d_b.User).where(d_b.User.email==user_email)).first()
    
    if not user:
        raise credentials_exception
    return user