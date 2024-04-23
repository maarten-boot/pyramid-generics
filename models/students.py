# python3

# from collections import OrderedDict

from sqlalchemy import (
    Column,
    Integer,
    # String,
    UniqueConstraint,
)


from models.base import (
    Base,
    HavingIntegerIdPkAutoIncr,
    HavingUuid,
    HavingName,
    HavingDatesCreUpd,
    HavingSoftDelete,
)


class Students(
    HavingIntegerIdPkAutoIncr,
    HavingUuid,
    HavingName,
    HavingDatesCreUpd,
    HavingSoftDelete,
    Base,
):  # pylint: disable=too-few-public-methods
    __tablename__ = "student"

    percent = Column(
        Integer,
    )

    __table_args__ = (
        UniqueConstraint("name"),
        # UniqueConstraint("col2", "col3", name="uix_1"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        what = "Student"
        self.setWhat(what)

        self.addGenericData(
            "percent",
            {
                "pyType": "int",
                "label": "%",
                "title": "enter a percentage between [0-100] inclusive",
                "validators": {
                    "IntegerPercent": {
                        "valid": lambda a: (int(a) >= 0 and int(a) <= 100),
                        "message": "the data is invalid, please verify that the value is a integer between 0 and 100, inclusive",
                    },
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
