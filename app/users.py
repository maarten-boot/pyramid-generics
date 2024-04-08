from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
)

from sqlalchemy.orm import DeclarativeBase
import sqlalchemy.orm

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    pass


class Users(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(14), unique=True, nullable=False)
    email = Column(String(255))
    password = Column(String(64))


class Xsers:
    def __init__(self) -> None:
        self.users = {}

    def add(self, username: str, password: str) -> None:
        self.users[username] = password

    def exists(self, username: str) -> bool:
        return bool(self.users.get(username))

    def delete(self, username: str) -> None:
        if self.exists(username):
            del self.users[username]


def getsession():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
    )
    Base.metadata.create_all(bind=engine)
    s = sqlalchemy.orm.sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    return s()
