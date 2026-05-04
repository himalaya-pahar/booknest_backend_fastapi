from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, or_
from typing import List, Dict, Any

# TODO: Import your actual database models and session generator.
# Adjust these imports based on how your project is structured.
from database import get_session, Request, User, Book, ChatMessage

# Create a router instance for messaging APIs
router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"]
)

@router.get("/active-threads/{user_id}", response_model=List[Dict[str, Any]])
def get_active_threads(user_id: int, db: Session = Depends(get_session)):
    """
    Fetches all active swap requests (threads) for a specific user.
    A thread is considered active if the swap request status is "accepted"
    and the user is either the sender or the receiver of that request.
    """
    try:
        # 1. Find all accepted requests where the current user is involved
        statement = select(Request).where(
            (Request.status == "accepted") & 
            (or_(Request.sender_id == user_id, Request.receiver_id == user_id))
        )
        active_requests = db.exec(statement).all()
        
        threads = []
        
        for req in active_requests:
            # 2. Determine the peer ID (the other person in the swap)
            # If the current user is the sender, the peer is the receiver, and vice versa.
            peer_id = req.receiver_id if req.sender_id == user_id else req.sender_id
            
            # 3. Fetch the peer user's details (to display their name in the sidebar)
            peer_user = db.exec(select(User).where(User.id == peer_id)).first()
            
            # 4. Fetch the book's details (to display the book title being swapped)
            book = db.exec(select(Book).where(Book.id == req.book_id)).first()
            
            # Only add to the threads list if both the user and the book exist
            if peer_user and book:
                threads.append({
                    "id": req.id,                     # The request ID acts as the thread ID
                    "user": peer_user.name,           # Display name of the peer (Check if your DB uses 'name' or 'username')
                    "book": book.title,               # Title of the book being swapped
                    "receiver_id": peer_id            # The peer's ID (needed to send real-time messages)
                })
                
        return threads
        
    except Exception as e:
        print(f"Error fetching threads: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch active threads")


@router.get("/{request_id}")
def get_chat_history(request_id: int, db: Session = Depends(get_session)):
    """
    Fetches the previous chat history for a specific swap request (thread).
    Orders the messages by timestamp so they appear chronologically.
    """
    try:
        # Fetch all messages associated with this request_id, sorted by time
        statement = select(ChatMessage).where(ChatMessage.request_id == request_id).order_by(ChatMessage.timestamp)
        results = db.exec(statement).all()
        return results
        
    except Exception as e:
        print(f"Error fetching chat history: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch chat history")