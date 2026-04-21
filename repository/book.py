from fastapi import HTTPException,status,Depends
from sqlmodel import select
import schemas,database as d_b
from typing import List
from security import oauth2

def add(book:schemas.Book,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    new_book=d_b.Book(
        name=book.name,
        author=book.author,
        user_id=current_user.id
    )
    if not book:
        return False
    db.add(new_book)
    db.commit()
    return "Book added successfully"

def get_book(id:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->schemas.Book:
    book=db.exec(select(d_b.Book).where(d_b.Book.id==id)).first()

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No book found")
    
    if  book.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You do not own this book")
    return book

def get_books(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user))->List[schemas.Book]:
    books=db.exec(select(d_b.Book).where(d_b.Book.user_id==current_user.id)).all()
    if not books:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No book found")
    return books

