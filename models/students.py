# python3

from collections import OrderedDict

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    Integer,
    String,
    create_engine,
)

from sqlalchemy.orm import (
    sessionmaker,
)

from .base import Base


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

    _genericMeta = {
        "name": "students",
    }

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