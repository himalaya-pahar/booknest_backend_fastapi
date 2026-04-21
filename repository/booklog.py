from fastapi import APIRouter,Depends,HTTPException,status
import database as d_b,schemas
from security import oauth2
from sqlmodel import select
from typing import List
from sqlmodel import delete

def request_swap(offered_book:int,wanted_book:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    w_book=db.exec(select(d_b.BookLog).where(d_b.BookLog.book_id==wanted_book)).first()
    o_book=db.exec(select(d_b.Book).where(d_b.Book.id==offered_book)).first()

    if not w_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book is not in swaplist")
    if not o_book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    if o_book.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You do not own the offered book")
    if current_user.id==w_book.user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You cannot request your own book")
    
    db.exec(delete(d_b.Request).where(d_b.Request.offered_book==o_book.id,d_b.Request.wanted_book==w_book.book_id))
    
    new_request=d_b.Request(
        requestor=current_user.id,
        grantor=w_book.user_id,
        offered_book=offered_book,
        wanted_book=wanted_book,
        status="pending"
    )

    db.add(new_request)
    db.commit()
    return "request for book swap successful"

def pending_request(db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    requests=db.exec(select(d_b.Request).where(d_b.Request.status=="pending",d_b.Request.grantor==current_user.id)).all()

    if not requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No request found")
    
    return requests

def upd_pending_request(id:int,upd:str,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    request=db.exec(select(d_b.Request).where(d_b.Request.id==id)).first()

    if not request or request.grantor!=current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No request found")
    if request.status=="accepted":
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED,detail="Already accepted")
    

    request.status=upd
    db.add(request)

    if upd=="accepted":
        db.exec(delete(d_b.BookLog).where(d_b.BookLog.book_id==request.wanted_book))
        db.exec(delete(d_b.BookLog).where(d_b.BookLog.book_id==request.offered_book))

        new_successful_swap_book=d_b.SuccessfulSwapHistory(
            user_1=request.grantor,
            user_2=request.requestor,
            book_1=request.wanted_book,
            book_2=request.offered_book)
        

        db.add(new_successful_swap_book)
        book_1=db.exec(select(d_b.Book).where(d_b.Book.id==request.wanted_book)).first()
        book_2=db.exec(select(d_b.Book).where(d_b.Book.id==request.offered_book)).first()

        if book_1 and book_2:
            book_1.user_id = request.requestor
            book_2.user_id = request.grantor
            db.add(book_1)
            db.add(book_2)

    db.commit()
    return "updated"

def make_a_book_log(book_id:int,db:d_b.SessionDep,current_user=Depends(oauth2.get_current_user)):
    book=db.exec(select(d_b.Book).where(d_b.Book.id==book_id)).first()

    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Book not found")
    if book.user_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You do not own this book")

    
    new_book_log=d_b.BookLog(
        name=book.name,
        author=book.author,
        book_id=book.id,
        user_id=current_user.id
    )

    db.exec(delete(d_b.BookLog).where(d_b.BookLog.book_id==book_id))
    db.add(new_book_log)
    db.commit()
    return "Log added successfully"

def show_log(db:d_b.SessionDep)->List[schemas.BookLog]:
    book_logs=db.exec(select(d_b.BookLog)).all()

    if not book_logs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No log found")
    
    return book_logs 
