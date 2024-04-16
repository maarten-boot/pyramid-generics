# python3

from typing import (
    Any,
    Tuple,
    Optional,
    Dict,
)
from collections import OrderedDict

from sqlalchemy import (
    Column,
    Integer,
    String,
)


from models.base import (
    Base,
    HavingDatesCreUpdDel,
    HavingUuid,
    HavingIntegerIdAutoIncr,
)


class Students(
    HavingIntegerIdAutoIncr,
    HavingUuid,
    HavingDatesCreUpdDel,
    Base,
):  # pylint: disable=too-few-public-methods
    __tablename__ = "student"

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
        "auto": True,
        "readonly": True,
        "pyType": "int",
        "label": "ID",
        "title": "automatically generated",
    }

    _GenericData["uuid"] = {
        "auto": True,
        "readonly": True,
        "pyType": "uuid",
        "label": "uuid",
        "title": "automatically generated",
    }

    _GenericData["name"] = {
        "pyType": "str",
        "label": "Name",
        "title": "Enter a student name.",
        "validators": {
            "StringLen": lambda a: (len(str(a)) <= 63),
        },
    }

    _GenericData["percent"] = {
        "pyType": "int",
        "label": "%",
        "title": "enter a percentage between [0-100] inclusive",
        "validators": {
            "IntegerPercent": lambda a: (int(a) >= 0 and int(a) <= 100),
        },
    }

    _GenericData["creAt"] = {
        "pyType": "datetime",
        "format": "%Y-%m-%d %H:%M",
        "label": "created",
        "title": "The create timestamp, automatically generated",
        "readonly": True,
    }

    _GenericData["updAt"] = {
        "pyType": "datetime",
        "format": "%Y-%m-%d %H:%M",
        "label": "updated",
        "title": "The last update timestamp, automatically generated",
        "readonly": True,
    }

    _GenericData["delAt"] = {
        "label": "deleted",
        "format": "%Y-%m-%d %H:%M",
        "title": "The delete timestamp, automatically generated",
        "pyType": "datetime",
        "readonly": True,
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
