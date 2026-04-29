from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import database as d_b,schemas
from security import hashing
from routers import user,authenticate,book,booklog,wishlist
from sqlmodel import select,func

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("server starting...")
    d_b.create_db_and_tables()
    yield
    print("server shutting down...")

app=FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_credentials=True,
    allow_methods=["*"],        
    allow_headers=["*"],        
)

app.include_router(user.router)
app.include_router(authenticate.router)
app.include_router(book.router)
app.include_router(booklog.router)
app.include_router(wishlist.router)

@app.get("/api/booknest-stats")
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
