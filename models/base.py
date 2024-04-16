# python3
import datetime
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    DateTime,
    String,
    UnicodeText,
    Uuid,
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


class HavingIntegerId(Base):  # pylint: disable=too-few-public-methods
    __abstract__ = True
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )


class HavingIntegerIdAutoIncr(Base):  # pylint: disable=too-few-public-methods
    __abstract__ = True
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )


class HavingUuid(Base):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    uuid = Column(
        Uuid(36),
        unique=True,
        default=uuid.uuid4,
    )


class HavingUniqNameAndDescription(Base):
    __abstract__ = True

    name = Column(
        String(128),
        unique=True,
    )
    description = Column(UnicodeText())


class HavingDatesCreUpdDel(Base):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    creAt = Column(
        DateTime,
        default=datetime.datetime.now,
    )
    updAt = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    delAt = Column(
        DateTime,
        nullable=True,
    )
