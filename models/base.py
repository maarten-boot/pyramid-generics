# python3

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    create_engine,
)

from sqlalchemy.orm import (
    sessionmaker,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test2.db"

Base = declarative_base()


def getDbSession():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()
