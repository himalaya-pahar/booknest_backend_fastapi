from fastapi import APIRouter,Depends,HTTPException,status
import database as d_b,schemas
from security import oauth2
from sqlmodel import select
from typing import List
from sqlmodel import delete
from repository import booklog as repo_booklog


def add_to_wishlist(wish_item: schemas.WishlistCreate, session: d_b.SessionDep):

    db_item = d_b.Wishlist(
        title=wish_item.title,
        author=wish_item.author,
        condition=wish_item.condition,
        user_id=wish_item.user_id
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_wishlist(session: d_b.SessionDep):
    wishlist_items = session.exec(select(d_b.Wishlist)).all()
    return wishlist_items