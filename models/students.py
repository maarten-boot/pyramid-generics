# python3

from typing import (
    Any,
    Tuple,
    Optional,
    Dict,
)
from collections import OrderedDict

# from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Column,
    Integer,
    String,
    # create_engine,
)

# from sqlalchemy.orm import sessionmaker


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
        "labelP": "Students",  # plural
        "labelS": "Student",  # singular
    }

    _GenericData = OrderedDict()

    _GenericData["id"] = {
        "pk": True,
        "label": "ID",
        "title": "Enter a student identifier.",
        "pyType": "int",
        "validators": {
            "GreaterZero": lambda a: (int(a) > 0),
        },
    }

    _GenericData["name"] = {
        "label": "Name",
        "title": "Enter a student name.",
        "pyType": "str",
        "validators": {
            "StringLen": lambda a: (len(str(a)) <= 63),
        },
    }

    _GenericData["percent"] = {
        "label": "Percentage%",
        "title": "enter a percentage between [0-100] inclusive",
        "pyType": "int",
        "validators": {
            "IntegerPercent": lambda a: (int(a) >= 0 and int(a) <= 100),
        },
    }

    @classmethod
    def getFields(cls) -> Dict[str, Any]:
        return cls._GenericData

    @classmethod
    def isValid(cls, name: str, value: Any) -> Tuple[bool, Optional[str]]:
        # if we dont know about this name the data is false allways
        if name not in cls._GenericData:
            return False, "Field name unknown in table: Students"

        # if we have no validators define the data is ok allways
        if "validators" not in cls._GenericData[name]:
            return True

        for n, func in cls._GenericData[name]["validators"].items():
            if func(value) is False:
                return False
        return True
