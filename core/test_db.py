from users.models import UserModel, UserType
from core.database import SessionLocal
from tasks.models import TaskModel


db = SessionLocal()

user = db.query(UserModel).filter(UserModel.username == "amintavakoli").first()

if user:
    user.user_type = UserType.ADMIN
    db.commit()
    db.refresh(user)
    print("Updated:", user.username, user.user_type)
else:
    print("User not found")
