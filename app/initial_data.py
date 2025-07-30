from sqlalchemy.orm import Session
from .helpers import user_helper
from .schemas import user_schema
from .configs.database import SessionLocal

def create_initial_users():
    db: Session = SessionLocal()
    try:
        users = user_helper.get_users(db)
        if not users:
            admin_user = user_schema.UserCreate(
                first_name="Admin",
                last_name="User",
                email="admin@example.com",
                password="adminpassword",
            )
            user_helper.create_user(db, user=admin_user, role="admin", is_system_generated=True)

            regular_user = user_schema.UserCreate(
                first_name="Regular",
                last_name="User",
                email="user@example.com",
                password="userpassword",
            )
            user_helper.create_user(db, user=regular_user, role="user", is_system_generated=True)
    finally:
        db.close()
