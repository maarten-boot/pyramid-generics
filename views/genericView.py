import sys
import datetime

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

        self.settings = request.registry.settings
        self.menue = self.settings.get("menue")

        self.verbose = self.settings.get("verbose")
        if self.verbose:
            print(
                f"VERBOSE GenericView.__init__: {self.settings}",
                file=sys.stderr,
            )

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
                z = getattr(row, name)
                if z is not None:
                    fad[name] = z

        if self.verbose:
            print(fad)

        return fad

    def getRowsWithPk(self, idX):
        return self.dbSession.query(
            self.model,
        ).filter(
            self.model.id == idX,
        )

    def getRowFirstWithPk(self, idX):
        row = self.getRowsWithPk(idX).first()
        if not row:
            return None
        return row

    def newItem(self):  # pylint: disable=unused-argument
        r = self.startReturnData("new")
        r["data"] = self.model._genericData
        return r

    def listAll(self):  # pylint: disable=unused-argument
        listCaption = (
            self.settings.get(
                "models",
                {},
            )
            .get(
                self.modelName,
                {},
            )
            .get(
                "genericMeta",
                {},
            )
            .get(
                "listCaption",
                "",
            )
        )
        fields = self.model.getFields()
        rows = self.dbSession.query(
            self.model,
        ).filter(
            self.model.delAt.is_(None)  # skip soft_deleted items
        )

        # TODO: add a purge view and real delete actions
        # TODO: introduce paging, filter and search

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
        idX = self.request.matchdict.get(pkName)
        row = self.getRowFirstWithPk(idX)
        if not row:
            # flash message not found pk
            msg = f"showOne: row not found with pkName: {pkName} and pk: {idX}"
            self.request.session.flash(msg)
            return HTTPFound(location=f"/{self._m}/")

        zz = self._setDataAsDict(row)
        r = self.startReturnData("showOne")
        r["item"] = zz
        r["data"] = self.model._genericData
        return r

    def addOne(self):
        fields = self.model.getFields()
        d = {}
        for name, data in fields.items():
            if self.request.POST.get(name):
                if data.get("readonly", None) is True:
                    continue
                d[name] = self.request.POST.get(name)
                # validate
                d[name] = d[name].strip()

        if self.verbose:
            print(f"VERBOSE GenericView.addOne: {d}", file=sys.stderr)

        item = self.model(**d)
        try:
            self.dbSession.add(item)
            self.dbSession.commit()
            return HTTPFound(location=f"{self.relativeUrl}")
        except Exception as e:
            r = self.startReturnData("new")

            r["item"] = d
            r["data"] = self.model._genericData
            r["message"] = f"error on 'add': {e}"

            return r

    def updateOne(self):
        pkName = self._getPkName()
        idX = self.request.POST.get(pkName)
        row = self.getRowFirstWithPk(idX)
        if not row:
            msg = f"updateOne: row not found with pkName: {pkName} and pk: {idX}"
            self.request.session.flash(msg)
            return HTTPFound(location=f"/{self._m}/")

        fields = self.model.getFields()
        d = {}
        for name, data in fields.items():
            if self.request.POST.get(name):
                if data.get("readonly", None) is True:
                    continue

                d[name] = self.request.POST.get(name)
                # TODO: validate
                d[name] = d[name].strip()

                setattr(row, name, d[name])  # update the row
        try:
            self.dbSession.commit()
            return HTTPFound(location=f"{self.relativeUrl}")
        except Exception as e:
            self.dbSession.rollback()
            zz = self._setDataAsDict(row)

            r = self.startReturnData("showOne")
            r["item"] = zz
            r["data"] = self.model._genericData
            r["message"] = f"error on 'update': {e}"

            return r

    def deleteOne(self):
        pkName = self._getPkName()
        idX = self.request.matchdict.get(pkName)
        row = self.getRowFirstWithPk(idX)
        if not row:
            msg = f"deleteOne: row not found with pkName: {pkName} and pk: {idX}"
            self.request.session.flash(msg)
            return HTTPFound(location=f"/{self._m}/")

        # self.getRowsWithPk(idX).delete()
        row.delAt = datetime.datetime.now()
        self.dbSession.commit()

        msg = f"Record has been deleted: pkName: {pkName}, pk: {idX}"
        self.request.session.flash(msg)
        return HTTPFound(location=f"/{self._m}/")

        r = self.startReturnData("delete")
        r["message"] = "Record has been deleted"
        r["data"] = self.model._genericData
        return r
