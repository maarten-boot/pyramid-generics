# python3
import datetime
import uuid

# from collections import OrderedDict

from typing import (
    # List,
    Dict,
    Any,
    Tuple,
    Optional,
)
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


class WithGenerics:
    _what = None
    _genericMeta = {}
    _genericData = {}
    _genericOrder = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def setWhat(cls, what: str) -> None:
        cls._what = what

    @classmethod
    def addGenericMeta(cls, key: str, val: str) -> None:
        cls._genericMeta[key] = val

    @classmethod
    def addGenericMetaDict(cls, d: Dict[str, str]) -> None:
        cls._genericMeta = d

    @classmethod
    def addGgenericData(cls, name: str, info: Dict[str, Any]) -> None:
        cls._genericData[name] = info

    @classmethod
    def getFields(cls) -> Dict[str, Any]:
        return cls._genericData

    @classmethod
    def setFieldsOrder(cls, fieldsOrder: list) -> None:
        cls._genericOrder = fieldsOrder

    @classmethod
    def getFieldsOrder(cls) -> None:
        return cls._genericOrder

    @classmethod
    def isValid(cls, name: str, value: Any) -> Tuple[bool, Optional[str]]:
        # if we dont know about this name: the data is false allways
        if name not in cls._genericData:
            return False, "Field name unknown in table: Students"

        # if we have no validators define the data is ok allways
        if "validators" not in cls._genericData[name]:
            return True

        for n, func in cls._genericData[name]["validators"].items():
            if func(value) is False:
                return False
        return True


class HavingIntegerIdManual(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGgenericData(
            "id",
            {
                "pk": True,
                "auto": False,
                "readonly": True,
                "pyType": "int",
                "label": "ID",
                "title": "a uniqe id",
            },
        )

    id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )


class HavingIntegerIdAutoIncr(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGgenericData(
            "id",
            {
                "pk": True,
                "auto": True,
                "readonly": True,
                "pyType": "int",
                "label": "ID",
                "title": "a uniqe id, automatically generated",
            },
        )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )


class HavingUuid(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGgenericData(
            "uuid",
            {
                "auto": True,
                "readonly": True,
                "pyType": "uuid",
                "label": "uuid",
                "title": "automatically generated",
            },
        )

    uuid = Column(
        Uuid(36),
        unique=True,
        default=uuid.uuid4,
    )


class HavingUniqNameAndDescription(
    WithGenerics,
    Base,
):
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGgenericData(
            "name",
            {
                "pyType": "str",
                "label": "Name",
                "title": "Enter a unique name.",
                "validators": {
                    "StringLen": lambda a: (len(str(a)) <= 128),
                },
            },
        )

    # _name_lan = 128
    name = Column(
        String(128),
        unique=True,
    )
    description = Column(UnicodeText())


class HavingDatesCreUpdDel(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGgenericData(
            "creAt",
            {
                "pyType": "datetime",
                "format": "%Y-%m-%d %H:%M",
                "label": "created",
                "title": "The create timestamp, automatically generated",
                "readonly": True,
            },
        )
        self.addGgenericData(
            "updAt",
            {
                "pyType": "datetime",
                "format": "%Y-%m-%d %H:%M",
                "label": "updated",
                "title": "The last update timestamp, automatically generated",
                "readonly": True,
            },
        )

        self.addGgenericData(
            "delAt",
            {
                "label": "deleted",
                "format": "%Y-%m-%d %H:%M",
                "title": "The delete timestamp, automatically generated",
                "pyType": "datetime",
                "readonly": True,
            },
        )

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
