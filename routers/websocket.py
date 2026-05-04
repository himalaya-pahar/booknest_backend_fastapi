from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from database import engine, ChatMessage
from connectionManager import ConnectionManager
manager = ConnectionManager()

router = APIRouter(
    prefix="/ws",
    tags=["WebSocket"]
)

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # Step 1: Register the user connection
    await manager.connect(user_id, websocket)
    
    # Using a manual database session to ensure it stays open during the loop
    with Session(engine) as db:
        try:
            while True:
                # Step 2: Receive JSON data from the client (Next.js)
                # Expected payload: {"request_id": 1, "receiver_id": 2, "content": "Hello!"}
                data = await websocket.receive_json()
                
                # Step 3: Save the message to the database for persistence
                new_msg = ChatMessage(
                    request_id=data["request_id"],
                    sender_id=user_id,
                    receiver_id=data["receiver_id"],
                    content=data["content"]
                )
                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)

                # Step 4: Prepare the message for real-time delivery
                payload = {
                    "id": new_msg.id,
                    "request_id": new_msg.request_id,
                    "sender_id": new_msg.sender_id,
                    "content": new_msg.content,
                    "timestamp": str(new_msg.timestamp)
                }
                
                # Step 5: Push the message to the receiver instantly if they are online
                await manager.send_personal_message(payload, data["receiver_id"])
                
        except WebSocketDisconnect:
            # Clean up when the user closes the tab or loses connection
            manager.disconnect(user_id)
        except Exception as e:
            # Handle unexpected errors and ensure the user is disconnected
            print(f"Error in WebSocket: {e}")
            manager.disconnect(user_id)
