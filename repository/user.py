from fastapi import HTTPException,status,Depends
import schemas,database as d_b
from sqlmodel import select
from security import oauth2

def get_users(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->schemas.ShowUser:
    user=db.exec(select(d_b.User).where(d_b.User.id==current_user.id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no user found"
        )
    return user

def get_user(id:int,db:d_b.SessionDep)->schemas.ShowUser:
    user=db.exec(select(d_b.User).where(d_b.User.id==id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no user found"
        )
    return user

def update_user(request: schemas.UserUpdate, db: d_b.SessionDep, current_user):
    
    user = db.exec(select(d_b.User).where(d_b.User.id == current_user.id)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    if request.name:
        user.name = request.name
    if request.phone_no is not None:  
        user.phone_no = request.phone_no
    if request.address is not None:
        user.address = request.address
        
    db.add(user)
    db.commit()
    return "Profile updated successfully"