from pyramid.httpexceptions import HTTPFound
from models.base import  getDbSession


class GenericView:
    model = None

    def __init__(self, request):
        self.request = request
        self.dbSession = getDbSession()

    def newItem(self):  # pylint: disable=unused-argument
        return {
            "data": self.model._GenericData,
        }

    def listAll(self):  # pylint: disable=unused-argument
        rows = self.dbSession.query(self.model).all()
        items = []
        for row in rows:
            items.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "percent": row.percent,
                },
            )
        return {
            "items": items,
            "data": self.model._GenericData,
        }

    def showOne(self):
        idX = int(self.request.matchdict.get("id"))
        # VALIDATE

        row = (
            self.dbSession.query(
                self.model,
            )
            .filter(self.model.id == idX)
            .first()
        )

        item = {}
        if row:
            item = {
                "id": row.id,
                "name": row.name,
                "percent": row.percent,
            }
            return {
                "item": item,
                "data": self.model._GenericData,
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
        return HTTPFound(location="/")

    def updateOne(self):
        idX = int(self.request.POST.get("id"))
        # TODO: VALIDATE

        item = (
            self.dbSession.query(
                self.model,
            )
            .filter(self.model.id == idX)
            .first()
        )
        item.name = str(self.request.POST["name"])
        item.percent = int(self.request.POST["percent"])

        self.dbSession.commit()
        return HTTPFound(location="/")

    def deleteOne(self):
        idX = self.request.matchdict.get("id")

        self.dbSession.query(self.model).filter(self.model.id == idX).delete()
        self.dbSession.commit()

        return {"message": "Record has been deleted"}
