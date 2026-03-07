from fastapi import APIRouter,Depends,HTTPException,status
import database as d_b,schemas
from security import oauth2
from sqlmodel import select
from typing import List
from sqlmodel import delete
from repository import booklog as repo_booklog

router=APIRouter(
    prefix="/booklog",
    tags=["BookLog"]
)

@router.post('/request')
def request_swap(offered_book:int,wanted_book:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return repo_booklog.request_swap(offered_book,wanted_book,db,current_user)

@router.get('/request')
def pending_request(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return repo_booklog.pending_request(db,current_user)

@router.put('/request')
def upd_pending_request(id:int,upd:str,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return repo_booklog.upd_pending_request(id,upd,db,current_user)

@router.post('/{book_id}')
def make_a_book_log(book_id:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    return repo_booklog.make_a_book_log(book_id,db,current_user)

@router.get('/')
def show_log(db:d_b.SessionDep)->List[schemas.BookLog]:
    return repo_booklog.show_log(db)
