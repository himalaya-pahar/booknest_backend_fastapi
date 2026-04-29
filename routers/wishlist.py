from fastapi import APIRouter, Depends, HTTPException, status
import database as d_b
import schemas
from security import oauth2
from repository import wishlist as repo_wishlist

router = APIRouter(
    prefix="/wishlist", # The base URL will be http://127.0.0.1:8000/wishlist/
    tags=["Wishlist"]
)

@router.post("/", response_model=schemas.ShowWishlist)
def add_to_wishlist(wish_item: schemas.WishlistCreate, session: d_b.SessionDep, current_user = Depends(oauth2.get_current_user)):
    # Passing the user ID extracted from the token to the repository function
    return repo_wishlist.add_to_wishlist(wish_item, session, current_user.id)

@router.get("/", response_model=list[schemas.ShowWishlist])
def get_wishlist(session: d_b.SessionDep, current_user = Depends(oauth2.get_current_user)):
    # Passing the user ID extracted from the token to fetch only their specific wishlist
    return repo_wishlist.get_wishlist(session, current_user.id)