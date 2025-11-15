from sqlalchemy import (
    Column,
    String,
    Boolean,
    Text,
    func,
    Integer,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
)
from core.database import Base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from enum import Enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserType(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), nullable=False)
    user_type = Column(SQLEnum(UserType, name="user_type"), nullable=False)

    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    tasks = relationship("TaskModel", back_populates="user")

    def hash_password(self, password: str) -> str:
        """Hash a plain-text password."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain-text password against a hashed password."""
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)


class TokenModel(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, nullable=False, unique=True)
    created_date = Column(DateTime, server_default=func.now())

    user = relationship("UserModel", uselist=False)
