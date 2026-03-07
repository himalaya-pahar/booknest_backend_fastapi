from fastapi import Depends,APIRouter
import schemas,database as d_b
from typing import List
from security import oauth2
from repository import book as repo_book


router=APIRouter(
    prefix="/book",
    tags=["Books"]
)

@router.post('/')
def add_book(book:schemas.Book,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return repo_book.add(book,db,current_user)

@router.get('/{id}')
def get_one_book(id:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->schemas.Book:
    return repo_book.get_book(id,db,current_user)

@router.get('/')
def get_book(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->List[schemas.Book]:
    return repo_book.get_books(db,current_user)
