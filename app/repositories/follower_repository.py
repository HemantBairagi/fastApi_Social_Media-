from app.models.models import Follow
from sqlalchemy.orm import Session

def get_follower(db: Session, user_id: int) -> Follow:
    return db.query(Follow).filter(Follow.follower_id == user_id).count()


def get_following(db: Session, user_id: int) -> Follow:
    return db.query(Follow).filter(Follow.following_id == user_id).count()
