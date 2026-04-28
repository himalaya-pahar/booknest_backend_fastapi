from fastapi import Depends,APIRouter,Query
from typing import Annotated
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

@router.get('/all', response_model=List[schemas.ShowBook])
def explore_all_books(db: d_b.SessionDep,
                    q: Annotated[str | None, Query(description="Search by title or author")] = None,
                    genre: Annotated[str | None, Query(description="Filter by genre")] = None
                    ,current_user=Depends(oauth2.get_current_user)):
    return repo_book.get_all_books_in_system(db, search_query=q, genre=genre)

@router.get('/{id}')
def get_one_book(id:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->schemas.Book:
    return repo_book.get_book(id,db,current_user)

@router.get('/')
def get_book(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return repo_book.get_books(db,current_user)

@router.delete('/{id}')
def delete_book(id: int, db: d_b.SessionDep, current_user=Depends(oauth2.get_current_user)):
    return repo_book.delete_book(id, db, current_user)
