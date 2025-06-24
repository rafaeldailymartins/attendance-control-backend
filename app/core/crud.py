from sqlmodel import Session, select, SQLModel
from app.core.models import AppConfig, Role, User
from app.core.config import settings
from app.core.security import get_password_hash


def db_insert(instance: SQLModel, session: Session):
    session.add(instance)
    session.commit()
    session.refresh(instance)


def get_admin_role(session: Session):
    return session.exec(
        select(Role).where(Role.name == settings.ADMIN_ROLE_NAME)
    ).first()


def create_admin_role(session: Session):
    admin_role = get_admin_role(session)
    if not admin_role:
        admin_role = Role(name=settings.ADMIN_ROLE_NAME)
        db_insert(admin_role, session)

    return admin_role


def create_first_admin(session: Session):
    admin_role = get_admin_role(session)
    if not admin_role:
        admin_role = create_admin_role(session)

    admin = session.exec(select(User).where(User.role_id == admin_role.id)).first()
    if not admin:
        admin = User(
            email=settings.FIRST_ADMIN_EMAIL,
            password=get_password_hash(settings.FIRST_ADMIN_PASSWORD),
            name=settings.ADMIN_ROLE_NAME,
            role_id=admin_role.id,
        )
        db_insert(admin, session)

    return admin


def reset_app_config(session: Session):
    app_config = session.exec(select(AppConfig)).first()
    if not app_config:
        app_config = AppConfig(
            minutes_early=settings.DEFAULT_MINUTES_EARLY,
            minutes_late=settings.DEFAULT_MINUTES_LATE,
        )
        db_insert(app_config, session)

    return app_config
