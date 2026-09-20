from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from models.user import User


def get_user_by_email(db: Session, email: str):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)

    if user is None:
        return None

    if user.is_locked:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    return user