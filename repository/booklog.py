from fastapi import APIRouter,Depends,HTTPException,status
import database as d_b,schemas
from sqlmodel import or_
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

def upd_pending_request(id: int, upd: str, db: d_b.SessionDep, current_user):
    request = db.exec(select(d_b.Request).where(d_b.Request.id == id)).first()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # 1. HANDLE ACCEPT / REJECT (Only the Owner/Grantor can do this)
    if upd in ["accepted", "rejected"]:
        if request.grantor != current_user.id:
            raise HTTPException(status_code=403, detail="Only the owner can accept/reject")
        request.status = upd

    # 2. HANDLE MUTUAL CONFIRMATION (Both can do this once status is 'accepted')
    if upd == "completed":
        if request.status != "accepted":
            raise HTTPException(status_code=400, detail="Request must be accepted before confirming swap")
        
        if current_user.id == request.requestor:
            request.requestor_confirmed = True
        elif current_user.id == request.grantor:
            request.grantor_confirmed = True

        # Check if BOTH have now confirmed
        if request.requestor_confirmed and request.grantor_confirmed:
            request.status = "completed"
            
            # --- THE ACTUAL DATABASE SWAP LOGIC ---
            db.exec(delete(d_b.BookLog).where(d_b.BookLog.book_id == request.wanted_book))
            db.exec(delete(d_b.BookLog).where(d_b.BookLog.book_id == request.offered_book))

            book_1 = db.get(d_b.Book, request.wanted_book)
            book_2 = db.get(d_b.Book, request.offered_book)
            if book_1 and book_2:
                book_1.user_id = request.requestor
                book_2.user_id = request.grantor
                db.add(book_1)
                db.add(book_2)
            
            # Add to Successful History
            history = d_b.SuccessfulSwapHistory(
                user_1=request.grantor, user_2=request.requestor,
                book_1=request.wanted_book, book_2=request.offered_book
            )
            db.add(history)

    db.add(request)
    db.commit()
    return {"status": request.status, "requestor_confirmed": request.requestor_confirmed, "grantor_confirmed": request.grantor_confirmed}

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

def get_detailed_history(db: d_b.SessionDep, current_user):
    # Fetch all requests where the user is either the Requestor or the Grantor
    statement = select(d_b.Request).where(
        or_(d_b.Request.grantor == current_user.id, d_b.Request.requestor == current_user.id)
    )
    requests = db.exec(statement).all()

    results = []
    for req in requests:
        # Fetch Book Titles
        wanted_book = db.get(d_b.Book, req.wanted_book)
        offered_book = db.get(d_b.Book, req.offered_book)
        
        # Fetch User Details
        requestor = db.get(d_b.User, req.requestor)
        grantor = db.get(d_b.User, req.grantor)

        # Decide who the "Other Person" is for this specific user
        other_user = grantor if current_user.id == req.requestor else requestor
        
        # We only share phone/address if the status is NOT "pending"
        contact_info = {
            "phone": other_user.phone_no if req.status != "pending" else "Hidden",
            "address": other_user.address if req.status != "pending" else "Hidden"
        }

        results.append({
            "id": req.id,
            "status": req.status,
            "date": req.date,
            "wanted_book_title": wanted_book.name if wanted_book else "Deleted",
            "offered_book_title": offered_book.name if offered_book else "Deleted",
            "other_person_name": other_user.name,
            "other_person_contact": contact_info,
            "role": "owner" if current_user.id == req.grantor else "requestor"
        })
    return results

def get_marketplace_logic(db: d_b.SessionDep, q: str | None = None, genre: str | None = None):
    # 1. Join BookLog with User (to get owner name)
    # We also join with the original Book table to get the Genre 
    # (since BookLog doesn't store Genre, but Book does)
    query = select(d_b.BookLog, d_b.User, d_b.Book).where(
        d_b.BookLog.user_id == d_b.User.id,
        d_b.BookLog.book_id == d_b.Book.id
    )

    # 2. Add Search Filter (Title or Author)
    if q:
        query = query.where(
            or_(
                d_b.BookLog.name.contains(q),
                d_b.BookLog.author.contains(q)
            )
        )

    # 3. Add Genre Filter
    if genre and genre != "All":
        query = query.where(d_b.Book.genre == genre)

    results = db.exec(query).all()
    
    if not results:
        raise HTTPException(status_code=404, detail="No books in marketplace")

    # 4. Format for the frontend
    formatted_books = []
    for log, user, book in results:
        formatted_books.append({
            "id": log.book_id, # This is the ID we need for swap requests
            "name": log.name,
            "author": log.author,
            "genre": book.genre,
            "user_id": log.user_id,
            "owner_name": user.name
        })
    return formatted_books