import sys

from typing import (
    Dict,
    List,
    Any,
)

from pyramid.httpexceptions import HTTPFound
from models.base import getDbSession


class GenericView:
    model = None

    def __init__(self, request):
        self.request = request
        self.dbSession = getDbSession()

    def startReturnData(self, action: str) -> Dict[str, Any]:
        actions: List[str] = [
            "new",
            "listAll",
            "showOne",
            "delete",
        ]

        if action not in actions:
            raise Exception(f"unsupported action: {action}; we know about {actions}")

        r = {
            "relativeUrl": self.relativeUrl,
            "currentUrl": self.relativeUrl + action,
            "menue": self.menue,
        }
        return r

    def _getPkName(self, mustExist: bool = True) -> str | None:
        fields = self.model.getFields()
        k = "pk"
        for n, d in fields.items():
            if k in d and d[k] is True:
                return n

        if mustExist is False:
            return None

        assert False, "Expect to see a PK name in the model metadata"

    def _setDataAsDict(self, row):
        fields = self.model.getFields()
        fad = {}
        for name, data in fields.items():
            k = "pyType"
            if k in data and data[k] == "datetime" and "format" in data:
                z = getattr(row, name)
                if z:
                    z = z.strftime(data["format"])
                fad[name] = z
            else:
                fad[name] = getattr(row, name)

        return fad

    def getRowsWithPk(self, idX):
        return self.dbSession.query(self.model).filter(self.model.id == idX)

    def getRowFirstWithPk(self, idX):
        return self.getRowsWithPk(idX).first()

    def newItem(self):  # pylint: disable=unused-argument
        r = self.startReturnData("new")
        r["data"] = self.model._genericData
        return r

    def listAll(self):  # pylint: disable=unused-argument
        listCaption = getattr(self, "listCaption", "")
        fields = self.model.getFields()
        rows = self.dbSession.query(self.model).all()

        items = []
        for row in rows:
            zz = self._setDataAsDict(row)
            items.append(zz)

        r = self.startReturnData("listAll")
        r["items"] = items
        r["data"] = fields
        r["listCaption"] = listCaption
        return r

    def showOne(self):
        # find the name of the pk
        pkName = self._getPkName()
        idX = int(self.request.matchdict.get(pkName))
        # VALIDATE

        row = self.getRowFirstWithPk(idX)
        if row:
            zz = self._setDataAsDict(row)
            r = self.startReturnData("showOne")
            r["item"] = zz
            r["data"] = self.model._genericData
            return r

        if self.settings.get("verbose"):
            print(pkName, idX, "No row fould", file=sys.stderr)

    def addOne(self):
        # TODO: make dymanic

        name = str(self.request.POST.get("name"))
        v = self.request.POST.get("percent")
        if v is None or v == "":
            v = 0
        percent = int(v)
        # TODO: validate

        item = self.model(
            name=name,
            percent=percent,
        )

        self.dbSession.add(item)
        self.dbSession.commit()

        # TODO add option to redirect to showOne

        return HTTPFound(location=f"{self.relativeUrl}")

    def updateOne(self):
        # TODO: make dymanic

        pkName = self._getPkName()
        idX = int(self.request.POST.get(pkName))
        row = self.getRowFirstWithPk(idX)
        if row:
            row.name = str(self.request.POST["name"])
            row.percent = int(self.request.POST["percent"])
            self.dbSession.commit()

        # TODO add option to redirect to self

        return HTTPFound(location=f"{self.relativeUrl}")

    def deleteOne(self):
        pkName = self._getPkName()
        idX = self.request.matchdict.get(pkName)
        # validate

        row = self.getRowFirstWithPk(idX)
        if row:
            self.getRowsWithPk(idX).delete()
            self.dbSession.commit()

        r = self.startReturnData("delete")
        r["message"] = "Record has been deleted"
        r["data"] = self.model._genericData
        return r
