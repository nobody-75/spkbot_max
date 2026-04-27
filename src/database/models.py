from sqlalchemy import Column, Integer, String, event, ForeignKey
from sqlalchemy.orm import relationship

from . import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # "user", "admin", etc.

    def __str__(self):
        return self.name


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), index=True, nullable=False)
    second_name = Column(String(100), index=True, nullable=False)
    login = Column(String(100), index=True, nullable=False)
    max_id = Column(String(100), unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    password = Column(String(100), nullable=False)

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined"
    )

    role_rel = relationship("Role", lazy="joined")

    def __str__(self):
        return f"{self.first_name} {self.second_name}"


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="profile", lazy="joined")

    @property
    def user_display(self) -> str:
        """Возвращает ФИО пользователя"""
        if self.user:
            return f"{self.user.first_name} {self.user.second_name}".strip()
        return "Не указан"

    def __str__(self):
        return self.user_display








# Для User -> Profile
@event.listens_for(User, 'after_insert')
def create_profile(mapper, connection, target):
    """Автоматически создает профиль при создании пользователя"""
    connection.execute(
        Profile.__table__.insert().values(user_id=target.id)
    )


