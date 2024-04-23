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

# from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
)

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
    _genericData = {}
    _genericOrder = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._what = None
        self._genericMeta = {}
        self._genericData = {}
        self._genericOrder = []

    def setWhat(self, what: str) -> None:
        self._what = what

    def addGenericMeta(self, key: str, val: str) -> None:
        self._genericMeta[key] = val

    def addGenericMetaDict(self, d: Dict[str, str]) -> None:
        self._genericMeta = d

    def addGenericData(self, name: str, info: Dict[str, Any]) -> None:
        self._genericData[name] = info

    def getGenericData(self) -> dict:
        return self._genericData

    def getFields(self) -> Dict[str, Any]:
        return self._genericData

    def setFieldsOrder(self, fieldsOrder: list) -> None:
        self._genericOrder = fieldsOrder

    def getFieldsOrder(self) -> None:
        return self._genericOrder

    def isValid(self, name: str, value: Any) -> Tuple[bool, Optional[str]]:
        # if we dont know about this name: the data is false allways
        if name not in self._genericData:
            return False, "Field name unknown in table: Students"

        # if we have no validators define the data is ok allways
        if "validators" not in self._genericData[name]:
            return True

        for n, func in self._genericData[name]["validators"].items():
            if func(value) is False:
                return False
        return True


class Base(DeclarativeBase):
    # make the default table name the lower case class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class HavingIntegerIdPkManual(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
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


class HavingIntegerIdPkAutoIncr(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
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
        self.addGenericData(
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


class HavingName(
    WithGenerics,
    Base,
):
    __abstract__ = True

    NAME_STRLEN_MAX = 128

    def getNameStrlenMax(self):
        return self.NAME_STRLEN_MAX

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
            "name",
            {
                "pyType": "str",
                "label": "Name",
                "title": "Enter a name.",
                "validators": {
                    "StringLen": lambda a: (len(str(a)) <= self.NAME_STRLEN_MAX),
                },
            },
        )

    name = Column(
        String(NAME_STRLEN_MAX),
    )


class HavingUniqName(
    WithGenerics,
    Base,
):
    __abstract__ = True

    NAME_STRLEN_MAX = 128

    def getNameStrlenMax(self):
        return self.NAME_STRLEN_MAX

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
            "name",
            {
                "pyType": "str",
                "label": "Name",
                "title": "Enter a unique name.",
                "validators": {
                    "StringLen": lambda a: (len(str(a)) <= self.NAME_STRLEN_MAX),
                },
            },
        )

    name = Column(
        String(NAME_STRLEN_MAX),
        unique=True,
        nullable=False,
    )


class HavingDescriptionUtf8(
    WithGenerics,
    Base,
):
    __abstract__ = True

    description = Column(
        UnicodeText(),
        nullable=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
            "description",
            {
                "pyType": "str",
                "label": "Description",
                "title": "Describe this item.",
                "validators": {},
            },
        )


class HavingDatesCreUpd(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
            "creAt",
            {
                "pyType": "datetime",
                "format": "%Y-%m-%d %H:%M",
                "label": "created",
                "title": "The create timestamp, automatically generated",
                "readonly": True,
            },
        )
        self.addGenericData(
            "updAt",
            {
                "pyType": "datetime",
                "format": "%Y-%m-%d %H:%M",
                "label": "updated",
                "title": "The last update timestamp, automatically generated",
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


class HavingSoftDelete(
    WithGenerics,
    Base,
):  # pylint: disable=too-few-public-methods
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addGenericData(
            "delAt",
            {
                "label": "deleted",
                "format": "%Y-%m-%d %H:%M",
                "title": "The delete timestamp, automatically generated",
                "pyType": "datetime",
                "readonly": True,
            },
        )

    delAt = Column(
        DateTime,
        nullable=True,
    )
