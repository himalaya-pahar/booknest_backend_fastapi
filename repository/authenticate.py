from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
import schemas,database as d_b
from repository import user as repo_user
from security import hashing,token
from typing import Annotated
from sqlmodel import select

def signup(user:schemas.User,db:d_b.SessionDep)->schemas.ShowUser:
    new_user=d_b.User(name=user.name,email=user.email,password=hashing.get_hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def signin(user:Annotated[OAuth2PasswordRequestForm,Depends()],db:d_b.SessionDep):
    find_user=db.exec(select(d_b.User).where(d_b.User.email==user.username)).first()
    if not find_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect email or password")
    if not hashing.verify_password(user.password,find_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect email or password")
    
    access_token=token.create_access_token(data={"sub":user.username})
    return {"access_token":access_token,"token_type":"bearer"}
