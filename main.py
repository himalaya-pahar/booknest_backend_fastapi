from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import database as d_b,schemas
from security import hashing
from routers import user,authenticate,book,booklog,wishlist

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
