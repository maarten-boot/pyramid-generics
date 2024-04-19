import sys
import datetime
import math

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

    def getMySessionData(self):
        session = self.request.session
        if self.model._what not in session:
            session[self.model._what] = {}
        return session

    def getListCaption(self):
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
        return listCaption

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

    def getNavAndLimit(self):
        nav = None
        limit = None

        for k in ["first", "prev", "next", "last"]:
            z = f"btn-{k}"
            if z in self.request.POST:
                nav = k

        if "limit" in self.request.POST:
            limit = int(self.request.POST.get("limit", 0))

        if not limit:
            limit = 5

        if self.verbose:
            print(f"nav: {nav}, {limit}", file=sys.stderr)

        if limit <= 0:
            limit = 1
        if limit > 1000:
            limit = 1000

        return nav, limit

    def getSortUpDownForFields(self):
        def toggleSort(what):
            if what == "" or what is None:
                what = "down"
            elif what == "down":
                what = "up"
            elif what == "up":
                what = ""
            else:
                what = ""
            return what

        session = self.getMySessionData()

        sortList = session.get(
            self.model._what,
            {},
        ).get(
            "sort",
            {},
        )

        fields = self.model.getFields()
        for name, data in fields.items():
            z = f"btn-{name}"
            if z in self.request.POST:
                sortList[name] = toggleSort(self.request.POST.get(z))

        if self.verbose:
            print("Sort:", sortList, file=sys.stderr)

        session[self.model._what]["sort"] = sortList
        return sortList

    def getRowsWithPaginate(self, sortList, nav, limit):
        session = self.getMySessionData()

        k = "currentPage"
        if k not in session[self.model._what]:
            session[self.model._what][k] = 0
        currentPage = session[self.model._what][k]

        k = "offset"
        if k not in session[self.model._what]:
            session[self.model._what][k] = 0
        offset = session[self.model._what]["offset"]

        # formulate the basic query
        q = self.dbSession.query(
            self.model,
        ).filter(
            self.model.delAt.is_(None),  # skip soft_deleted items
        )
        count = q.count()  # how many rows do we have
        session[self.model._what]["count"] = count

        pages = int(math.ceil(count / limit))  # how many pages is that with the current perPage limit

        if self.verbose:
            print("currentPage/count/limit/offset/pages", currentPage, count, limit, offset, pages, file=sys.stderr)

        if nav:
            if nav == "first":
                currentPage = 0
            if nav == "prev":
                currentPage -= 1
            if nav == "next":
                currentPage += 1
            if nav == "last":
                currentPage = pages - 1

        if currentPage < 0:
            currentPage = 0
        if currentPage >= pages:
            currentPage = pages

        if currentPage == pages and pages > 0:
            currentPage -= 1

        offset = limit * currentPage
        if offset < 0:
            offset = 0
        if offset > count:
            offset = count

        if self.verbose:
            print("currentPage/count/limit/offset/pages", currentPage, count, limit, offset, pages, file=sys.stderr)

        session[self.model._what]["offset"] = offset
        session[self.model._what]["currentPage"] = currentPage
        session[self.model._what]["pages"] = pages

        q = q.limit(
            limit,
        ).offset(
            offset,
        )

        data = q.all()

        return data, limit, count, pages, currentPage

    def newItem(self):  # pylint: disable=unused-argument
        r = self.startReturnData("new")
        r["data"] = self.model._genericData
        return r

    def listAll(self):  # pylint: disable=unused-argument
        if self.verbose:
            print("POST", self.request.POST, file=sys.stderr)

        sortList = self.getSortUpDownForFields()
        nav, limit = self.getNavAndLimit()

        rows, limit, count, pages, currentPage = self.getRowsWithPaginate(
            sortList,
            nav,
            limit,
        )

        items = []
        for row in rows:
            zz = self._setDataAsDict(row)
            items.append(zz)

        r = self.startReturnData("listAll")
        r["items"] = items  # a list of all rows
        r["data"] = self.model.getFields()
        r["listCaption"] = self.getListCaption()

        r["limit"] = limit
        r["count"] = count
        if pages == 0:
            pages = 1
        r["pages"] = pages
        if currentPage == 0:
            currentPage = 1
        r["currentPage"] = currentPage

        r["sort"] = sortList
        # search

        # TODO: add a purge view and real delete actions
        # TODO: introduce paging, filter and search
        # TODO: clear all filters
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
