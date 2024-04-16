from collections import OrderedDict
import datetime
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    create_engine,
)

from sqlalchemy.orm import (
    sessionmaker,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test2.db"

Base = declarative_base()


class HavingIntegerId(Base):  # pylint: disable=too-few-public-methods
    __abstract__ = True
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )


class HavingUuid(Base):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    uuid = Column(String(36), unique=True, default=str(uuid.uuid4()))


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


class Students(Base):  # pylint: disable=too-few-public-methods
    __tablename__ = "student"
    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )
    name = Column(
        String(63),
        unique=True,
    )
    percent = Column(
        Integer,
    )

    _GenericData = OrderedDict()

    _GenericData["id"] = {
        "label": "ID",
        "title": "Enter a student identifier.",
    }

    _GenericData["name"] = {
        "label": "Name",
        "title": "Enter a student name.",
    }

    _GenericData["percent"] = {
        "label": "Percentage%",
        "title": "enter a percentage between [0-100] inclusive",
    }


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
