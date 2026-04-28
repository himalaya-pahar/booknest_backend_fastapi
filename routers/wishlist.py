from fastapi import APIRouter,Depends,HTTPException,status
import database as d_b,schemas
from security import oauth2
from sqlmodel import select
from typing import List
from sqlmodel import delete
from repository import booklog as repo_booklog,wishlist

router=APIRouter(
    prefix="/wishlist",
    tags=["BookLog"]
)


@router.post("/", response_model=schemas.ShowWishlist)
def add_to_wishlist(wish_item: schemas.WishlistCreate, session: d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return wishlist.add_to_wishlist(wish_item,session)

@router.get("/", response_model=list[schemas.ShowWishlist])
def get_wishlist(session: d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return wishlist.get_wishlist(session)