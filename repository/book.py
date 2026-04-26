from fastapi import HTTPException,status,Depends
from sqlmodel import select
from sqlmodel import select, or_
import schemas,database as d_b
from typing import List
from security import oauth2

def add(book:schemas.Book,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    new_book=d_b.Book(
        name=book.name,
        author=book.author,
        genre=book.genre,
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

def get_all_books_in_system(
    db: d_b.SessionDep, 
    search_query: str | None = None,
    genre: str | None = None
) -> list[schemas.ShowBook]:
    
    # 1. The Magic JOIN! Select BOTH the Book and the User where their IDs match.
    query = select(d_b.Book, d_b.User).where(d_b.Book.user_id == d_b.User.id)

    # (Keep your search filters exactly the same)
    if search_query:
        query = query.where(
            or_(
                d_b.Book.name.contains(search_query),
                d_b.Book.author.contains(search_query)
            )
        )
    if genre and genre != "All":
        query = query.where(d_b.Book.genre == genre)
    # 2. Execute the query
    results = db.exec(query).all()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No books found matching your search criteria"
        )
    
    # 3. Combine the Book data and User data together to send to the frontend
    formatted_books =[]
    for book, user in results:
        formatted_books.append(
            schemas.ShowBook(
                id=book.id,
                name=book.name,
                author=book.author,
                genre=book.genre,
                user_id=book.user_id,
                owner_name=user.name  # <--- Here is the user's real name!
            )
        )
    
    return formatted_books