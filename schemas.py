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

class BookLog(Book):
    id:int
    user_id:int
    date:datetime
