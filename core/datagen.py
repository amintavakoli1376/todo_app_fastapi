from core.database import SessionLocal
from sqlalchemy.orm import Session
from users.models import UserModel, UserType
from tasks.models import TaskModel
from faker import Faker

fake = Faker()


def seed_users(db):
    user = UserModel(username=fake.user_name(), user_type=UserType.USER)
    user.set_password("12345678")
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User created with username: {user.username} and ID: {user.id}")
    return user


def seed_tasks(db, user, count=10):
    tasks_list = []
    for _ in range(10):
        tasks_list.append(
            TaskModel(
                user_id=user.id,
                title=fake.sentence(nb_words=6),
                description=fake.text(),
                is_completed=fake.boolean(),
            )
        )
    db.add_all(tasks_list)
    db.commit()
    print(f"added 10 tasks for user id: {user.id}")


def main():
    db = SessionLocal()

    try:
        user = seed_users(db)
        seed_tasks(db, user)

    finally:
        db.close()


if __name__ == "__main__":
    main()
