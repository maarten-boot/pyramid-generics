from pyramid.httpexceptions import HTTPFound
from models.base import getDbSession


class GenericView:
    model = None

    def __init__(self, request):
        self.request = request
        self.dbSession = getDbSession()

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
        zz = {}
        for n, d in fields.items():
            zz[n] = getattr(row, n)
        return zz

    def getRowsWithPk(self, idX):
        return self.dbSession.query(self.model).filter(self.model.id == idX)

    def getRowFirstWithPk(self, idX):
        return self.getRowsWithPk(idX).first()

    def newItem(self):  # pylint: disable=unused-argument
        return {
            "data": self.model._GenericData,
            "relativeUrl": self.relativeUrl,
        }

    def listAll(self):  # pylint: disable=unused-argument
        listCaption = getattr(self, "listCaption", "")
        fields = self.model.getFields()
        rows = self.dbSession.query(self.model).all()

        items = []
        for row in rows:
            zz = self._setDataAsDict(row)
            items.append(zz)

        return {
            "items": items,
            "data": fields,
            "relativeUrl": self.relativeUrl,
            "listCaption": listCaption,
        }

    def showOne(self):
        # find the name of the pk
        pkName = self._getPkName()
        idX = int(self.request.matchdict.get(pkName))
        # VALIDATE

        row = self.getRowFirstWithPk(idX)
        if row:
            zz = self._setDataAsDict(row)
            return {
                "item": zz,
                "data": self.model._GenericData,
                "relativeUrl": self.relativeUrl,
            }
        else:
            pass
            # not found

    def addOne(self):
        idX = int(self.request.POST.get("id"))
        name = str(self.request.POST.get("name"))
        v = self.request.POST.get("percent")
        if v is None or v == "":
            v = 0
        percent = int(v)

        # TODO: validate

        item = self.model(
            id=idX,
            name=name,
            percent=percent,
        )

        self.dbSession.add(item)
        self.dbSession.commit()

        return HTTPFound(location=f"{self.relativeUrl}/")

    def updateOne(self):
        pkName = self._getPkName()
        idX = int(self.request.POST.get(pkName))
        # validate

        row = self.getRowFirstWithPk(idX)
        if row:
            row.name = str(self.request.POST["name"])
            row.percent = int(self.request.POST["percent"])

            self.dbSession.commit()

        return HTTPFound(location=f"{self.relativeUrl}/")

    def deleteOne(self):
        pkName = self._getPkName()
        idX = self.request.matchdict.get(pkName)
        # validate

        row = self.getRowFirstWithPk(idX)
        if row:
            self.getRowsWithPk(idX).delete()
            self.dbSession.commit()

        return {
            "message": "Record has been deleted",
            "data": self.model._GenericData,
            "relativeUrl": self.relativeUrl,
        }
