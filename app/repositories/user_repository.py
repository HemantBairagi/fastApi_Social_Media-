from app.models.models import Users as User
from sqlalchemy.orm import Session
def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()



def update_profile_picture(db: Session, user_id: int, filename: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.profile_picture = filename
        db.commit()
        db.refresh(user)
    return user
