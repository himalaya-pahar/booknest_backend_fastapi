from sqlmodel import func,select
import database as d_b
from fastapi import APIRouter

router= APIRouter

@router.get("/api/booknest-stats")
def get_booknest_stats(session: d_b.SessionDep):
    # 1. Get the total number of books listed
    total_books = session.exec(select(func.count(d_b.Book.id))).one_or_none() or 0
    
    # 2. Get the total number of registered readers
    total_users = session.exec(select(func.count(d_b.User.id))).one_or_none() or 0
    
    # 3. Get the total number of unique genres
    unique_genres = session.exec(select(func.count(func.distinct(d_b.Book.genre)))).one_or_none() or 0
    
    return {
        "books": total_books,
        "readers": total_users,
        "genres": unique_genres
    }