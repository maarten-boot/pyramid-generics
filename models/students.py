# python3

# from collections import OrderedDict

from sqlalchemy import (
    Column,
    Integer,
    String,
)


from models.base import (
    Base,
    # WithGenerics,
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        what = "Student"
        self.setWhat(what)

        self.addGgenericData(
            "name",
            {
                "pyType": "str",
                "label": "Name",
                "title": "Enter a student name.",
                "validators": {
                    "StringLen": lambda a: (len(str(a)) <= 63),
                },
            },
        )

        self.addGgenericData(
            "percent",
            {
                "pyType": "int",
                "label": "%",
                "title": "enter a percentage between [0-100] inclusive",
                "validators": {
                    "IntegerPercent": lambda a: (int(a) >= 0 and int(a) <= 100),
                },
            },
        )
        self.addGenericMetaDict(
            {
                "name": "students",
                "labelP": f"{what}s",  # plural
                "labelS": f"{what}",  # singular
                "listCaption": f"{what}s Percentage List",
            },
        )

        self.setFieldsOrder(
            [
                "id",
                "uuid",
                "name",
                "percent",
                "creAt",
                "updAt",
            ],
        )

    name = Column(
        String(63),
        unique=True,
    )

    percent = Column(
        Integer,
    )
