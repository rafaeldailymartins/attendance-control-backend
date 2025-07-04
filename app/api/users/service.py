from sqlmodel import Session, select

from app.core import service as core_service
from app.core.models import User


def authenticate(session: Session, email: str, password: str):
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not core_service.verify_password(password, db_user.password):
        return None
    return db_user


def get_user_by_email(session: Session, email: str):
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user
