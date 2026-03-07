from fastapi import APIRouter,Depends
import schemas,database as d_b
from repository import user as repo_user
from security import oauth2

router=APIRouter(
    prefix="/user",
    tags=["Users"]
)

@router.get('/')
def get_users(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->schemas.ShowUser:
    return repo_user.get_users(db,current_user)

@router.get('/{id}')
def get_user(id:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->schemas.ShowUser:
    return repo_user.get_user(id,db)