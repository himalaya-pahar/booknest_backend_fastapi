from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, or_
from typing import List, Dict, Any

# Tomar database.py theke asol model gulo import kora holo
from database import get_session, Request, User, Book, ChatMessage

router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"]
)

@router.get("/active-threads/{user_id}")
def get_active_threads(user_id: int, db: Session = Depends(get_session)):
    try:
        # 1. sender_id/receiver_id er bodole requestor ar grantor use kora holo
        statement = select(Request).where(
            (Request.status == "accepted") & 
            (or_(Request.requestor == user_id, Request.grantor == user_id))
        )
        active_requests = db.exec(statement).all()
        
        threads = []
        
        for req in active_requests:
            # 2. Peer ber korar jonno requestor ar grantor check kora holo
            peer_id = req.grantor if req.requestor == user_id else req.requestor
            
            peer_user = db.exec(select(User).where(User.id == peer_id)).first()
            
            # 3. book_id er bodole wanted_book use kora holo (je boi ta swap hocche)
            book = db.exec(select(Book).where(Book.id == req.wanted_book)).first()
            
            if peer_user and book:
                threads.append({
                    "id": req.id,                     
                    "user": peer_user.name,           
                    "book": book.name,     # 4. book.title er bodole book.name deya holo          
                    "receiver_id": peer_id            
                })
                
        return threads
        
    except Exception as e:
        print(f"Error fetching threads: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch active threads")


@router.get("/{request_id}")
def get_chat_history(request_id: int, db: Session = Depends(get_session)):
    try:
        statement = select(ChatMessage).where(ChatMessage.request_id == request_id).order_by(ChatMessage.timestamp)
        results = db.exec(statement).all()
        return results
        
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")