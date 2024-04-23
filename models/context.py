# python3

# from collections import OrderedDict

from sqlalchemy import (
    Column,
    String,
    UniqueConstraint,
)


from models.base import (
    Base,
    HavingIntegerIdPkAutoIncr,
    HavingName,
    HavingDatesCreUpd,
    HavingDescriptionUtf8,
)


class Context(
    HavingIntegerIdPkAutoIncr,
    HavingName,
    HavingDescriptionUtf8,
    HavingDatesCreUpd,
    Base,
):
    PARENT_STRLEN_MAX = 128

    parent = Column(String(PARENT_STRLEN_MAX), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "parent",
            "name",
            name="uix_name_unique_in_parent",
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        what = "Context"
        self.setWhat(what)

        self.addGenericData(
            "parent",
            {
                "pyType": "str",
                "label": "Parent",
                "title": "my parent context",
                "validators": {},
            },
        )

        self.addGenericMetaDict(
            {
                "name": "context",
                "labelP": f"{what}s",  # plural
                "labelS": f"{what}",  # singular
                "listCaption": "Defined context's",
            },
        )

        self.setFieldsOrder(
            [
                "id",
                "parent",
                "name",
                "description",
                "creAt",
                "updAt",
            ],
        )
