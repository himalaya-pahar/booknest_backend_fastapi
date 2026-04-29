import database as d_b
import schemas
from sqlmodel import select, Session

def add_to_wishlist(wish_item: schemas.WishlistCreate, session: Session, user_id: int):
    # Assigning data to the database model; user_id comes from the decoded token
    db_item = d_b.Wishlist(
        title=wish_item.title,
        author=wish_item.author,
        condition=wish_item.condition,
        user_id=user_id 
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

def get_wishlist(session: Session, user_id: int):
    # Fetching only the books that belong to this specific user from the database
    wishlist_items = session.exec(select(d_b.Wishlist).where(d_b.Wishlist.user_id == user_id)).all()
    return wishlist_items