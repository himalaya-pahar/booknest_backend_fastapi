from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    name:str
    email:str
    password:str

class ShowUser(BaseModel):
    id:int
    name:str
    email:str

class Book(BaseModel):
    name:str
    author:str
    genre:str

class BookLog(Book):
    id:int
    user_id:int
    date:datetime

class ShowBook(BaseModel):
    id: int
    name: str
    author: str
    genre:str
    user_id: int
    owner_name: str


class WishlistCreate(BaseModel):
    title: str
    author: str
    condition: str
    user_id: int

class ShowWishlist(BaseModel):
    id: int
    title: str
    author: str
    condition: str
    user_id: int