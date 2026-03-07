from typing import Annotated
from sqlmodel import Field,Session,SQLModel,create_engine
from fastapi import Depends
from datetime import datetime,timezone

DATABASE_URL = "postgresql://admin:rootpassword@localhost:5432/booknest_db"

engine=create_engine(DATABASE_URL)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep=Annotated[Session,Depends(get_session)]

class User(SQLModel,table=True):
    id:int=Field(primary_key=True,index=True)
    name:str
    email:str
    password:str

class Book(SQLModel,table=True):
    id:int=Field(primary_key=True,index=True)
    name:str
    author:str
    user_id:int=Field(foreign_key="user.id",index=True)

class BookLog(SQLModel,table=True):
    id:int=Field(primary_key=True,index=True)
    name:str
    author:str
    book_id:int=Field(foreign_key="book.id")
    user_id:int=Field(foreign_key="user.id")
    date:datetime=Field(datetime.now())

class SuccessfulSwapHistory(SQLModel,table=True):
    id:int=Field(primary_key=True,index=True)
    user_1:int=Field(foreign_key="user.id")
    user_2:int=Field(foreign_key="user.id")
    book_1:int=Field(foreign_key="book.id")
    book_2:int=Field(foreign_key="book.id")
    date:datetime=Field(datetime.now())

class Request(SQLModel,table=True):
    id:int=Field(primary_key=True,index=True)
    requestor:int=Field(foreign_key="user.id")
    grantor:int=Field(foreign_key="user.id")
    offered_book:int=Field(foreign_key="book.id")
    wanted_book:int=Field(foreign_key="book.id")
    date:datetime=Field(datetime.now())
    status:str
    

