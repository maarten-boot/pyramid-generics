import sys
import datetime
import math
import inspect

from typing import (
    Dict,
    List,
    Any,
)

from pyramid.httpexceptions import HTTPFound

import sqlalchemy
from sqlalchemy.sql.expression import cast

from models.base import getDbSession


class WithVerbose:
    verbose: bool = False

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _verb(self, s: str) -> None:
        if self.verbose is False:
            return

        frame = inspect.stack()[1]
        the_class = frame[0].f_locals["self"].__class__.__name__
        the_method = frame[0].f_code.co_name

        print(
            "VERBOSE",
            frame.filename,
            frame.lineno,
            the_class,
            the_method,
            str(s),
            file=sys.stderr,
        )


class GenericView(WithVerbose):
    model = None

    def __init__(self, request):
        self.verbose = request.registry.settings.get("verbose", False)
        # super().__init__(verbose=verbose)

        self.request = request
        self.session = request.session
        self.settings = request.registry.settings

        self.menue = self.settings.get("menue")

        self.dbSession = getDbSession()
        if self.verbose:
            self._verb(str(self.settings))

    def getMySessionData(self):
        session = self.session
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
        fad = {}

        fields = self.model.getFields()

        for name in self.model.getFieldsOrder():
            data = fields[name]
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
            self._verb(str(fad))

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
            self._verb(f"nav: {nav}, {limit}")

        if limit <= 0:
            limit = 1
        if limit > 1000:
            limit = 1000

        return nav, limit

    def getSessionItemByNameWithDefault(self, k, default):
        session = self.getMySessionData()
        if k not in session[self.model._what]:
            session[self.model._what][k] = default
        return session[self.model._what][k]

    def getFilterFields(self):
        k = "filters"
        filtersList = self.getSessionItemByNameWithDefault(k, {})

        for name in self.model.getFieldsOrder():
            z = f"{k}-{name}"
            if z in self.request.POST and self.request.POST[z].strip() != "":
                filtersList[name] = self.request.POST.get(z).strip()
            else:
                if name in filtersList:
                    del filtersList[name]

        if self.verbose:
            self._verb(f"{k}: {filtersList}")

        session = self.getMySessionData()
        session[self.model._what][k] = filtersList

        return filtersList

    def getSortUpDownForFields(self):
        def toggleSort(what):
            what = what.strip().lower()
            if what == "" or what is None:
                what = "down"
            elif what == "down":
                what = "up"
            elif what == "up":
                what = ""
            else:
                what = ""
            return what

        k = "sort"
        sortList = self.getSessionItemByNameWithDefault(k, {})

        for name in self.model.getFieldsOrder():
            z = f"btn-{name}"
            if z in self.request.POST:
                sortList[name] = toggleSort(self.request.POST.get(z))

        if self.verbose:
            self._verb(f"{k} {sortList}")

        session = self.getMySessionData()
        session[self.model._what][k] = sortList

        return sortList

    def updateCurrentPage(
        self,
        nav,
        currentPage,
        pages,
    ):
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

        session = self.getMySessionData()
        session[self.model._what]["currentPage"] = currentPage

        return currentPage

    def newOffset(self, offset, limit, currentPage, count):
        offset = limit * currentPage
        if offset < 0:
            offset = 0
        if offset > count:
            offset = count

        session = self.getMySessionData()
        session[self.model._what]["currentPage"] = currentPage

        return offset

    def newPageCalculations(
        self,
        nav,
        currentPage,
        count,
        limit,
        offset,
    ):
        session = self.getMySessionData()

        pages = int(math.ceil(count / limit))  # how many pages is that with the current perPage limit
        session[self.model._what]["pages"] = pages

        if self.verbose:
            self._verb(
                ",".join(
                    [f"currentPage {currentPage}", f"count {count}", f"limit {limit}", f"offset {offset}", f"pages {pages}"],
                ),
            )

        currentPage = self.updateCurrentPage(nav, currentPage, pages)
        offset = self.newOffset(offset, limit, currentPage, count)

        if self.verbose:
            self._verb(
                ",".join(
                    [f"currentPage {currentPage}", f"count {count}", f"limit {limit}", f"offset {offset}", f"pages {pages}"],
                ),
            )

        return currentPage, offset, pages

    def basicSelectWithCount(self):
        self.getFilterFields()
        session = self.getMySessionData()

        # formulate the basic query|select
        q = sqlalchemy.select(
            self.model,
        ).filter(
            self.model.delAt.is_(None),  # skip soft_deleted items
        )

        filtersList = session[self.model._what]["filters"]

        for key, val in filtersList.items():
            q = q.filter(
                cast(  # non string fields cannot use ilike so we cast everything for now
                    getattr(self.model, key),
                    sqlalchemy.String,
                ).ilike(
                    f"%{val}%",
                ),
            )

        if self.verbose:
            self._verb(str(q))

        q2 = sqlalchemy.select(
            sqlalchemy.func.count(),
        ).select_from(
            q,
        )

        if self.verbose:
            self._verb(str(q2))

        count = self.dbSession.execute(
            q2,
        ).scalar_one()  # how many rows do we have

        session[self.model._what]["count"] = count

        return q, count

    def fetchDataWithLimitAndOffset(self, q, limit, offset):
        session = self.getMySessionData()
        sortList = session[self.model._what]["sort"]
        for key, val in sortList.items():
            if val == "down":
                q = q.order_by(getattr(self.model, key).asc())
            elif val == "up":
                q = q.order_by(getattr(self.model, key).desc())
            else:
                q = q

        # limit and offset must be after order by
        q = q.limit(
            limit,
        ).offset(
            offset,
        )

        # use scalars instead of execute:
        # see:: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html#selecting-orm-entities
        return self.dbSession.scalars(q).all()

    def getRowsWithPaginate(self):
        self.getSortUpDownForFields()
        nav, limit = self.getNavAndLimit()

        currentPage = self.getSessionItemByNameWithDefault("currentPage", 0)
        offset = self.getSessionItemByNameWithDefault("offset", 0)

        q, count = self.basicSelectWithCount()  # will later need search filter data and ordering

        currentPage, offset, pages = self.newPageCalculations(
            nav,
            currentPage,
            count,
            limit,
            offset,
        )

        data = self.fetchDataWithLimitAndOffset(
            q,
            limit,
            offset,
        )

        return data, limit, count, pages, currentPage

    def newItem(self):  # pylint: disable=unused-argument
        r = self.startReturnData("new")
        r["data"] = self.model._genericData
        return r

    def listAll(self):  # pylint: disable=unused-argument
        if self.verbose:
            self._verb(str("POST: {self.request.POST}"))

        rows, limit, count, pages, currentPage = self.getRowsWithPaginate()

        d = {}
        fields = self.model.getFields()
        for name in self.model.getFieldsOrder():
            self._verb(f"name: {name}")
            d[name] = fields[name]

        r = self.startReturnData("listAll")
        r["data"] = d

        r["items"] = rows
        r["listCaption"] = self.getListCaption()

        r["limit"] = limit
        r["count"] = count
        if pages == 0:
            pages = 1
        r["pages"] = pages
        if currentPage == 0:
            currentPage = 1
        r["currentPage"] = currentPage

        session = self.getMySessionData()
        r["sort"] = session[self.model._what]["sort"]
        r["filters"] = session[self.model._what]["filters"]

        # TODO: add a purge view and real delete actions
        # TODO: clear all filters

        if self.verbose:
            self._verb(f"{r}")

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
        d = {}
        fields = self.model.getFields()

        for name in self.model.getFieldsOrder():
            data = fields[name]
            if self.request.POST.get(name):
                if data.get("readonly", None) is True:
                    continue

                d[name] = self.request.POST.get(name).strip()
                # TODO: validate

        if self.verbose:
            self._verb(f"VERBOSE GenericView.addOne: {d}")

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

        d = {}
        fields = self.model.getFields()

        for name in self.model.getFieldsOrder():
            data = fields[name]

            if self.request.POST.get(name):
                if data.get("readonly", None) is True:
                    continue

                d[name] = self.request.POST.get(name).strip()
                # TODO: validate

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
