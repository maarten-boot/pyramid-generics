import sys

from pyramid.view import view_config

from models.context import Context
from views.genericView import GenericView

_m = "context"
_where = "templates/generic"


class ContextView(GenericView):
    modelName = "Context"
    _m = _m

    def __init__(self, request):
        super().__init__(request)
        self.model = Context
        self.relativeUrl = f"/{_m}/"

    @view_config(
        route_name=f"{_m}/new",
        renderer=f"{_where}/newform.html",
        request_method="GET",
    )
    def newContext(self):  # pylint: disable=unused-argument
        return super().newItem()

    @view_config(
        route_name=f"{_m}/listAll",
        renderer=f"{_where}/listall.html",
    )
    def listAll(self):  # pylint: disable=unused-argument
        return super().listAll()

    @view_config(
        route_name=f"{_m}/showOne",
        renderer=f"{_where}/showform.html",
        request_method="GET",
    )
    def showOne(self):
        return super().showOne()

    @view_config(
        route_name=f"{_m}/delete",
        renderer=f"{_where}/delete.html",
        request_method="GET",
    )
    def deleteOne(self):
        return super().deleteOne()

    @view_config(
        route_name=f"{_m}/add",
        request_method="POST",
        renderer=f"{_where}/newform.html",
    )
    def addOne(self):
        return super().addOne()

    @view_config(
        route_name=f"{_m}/update",
        request_method="POST",
        renderer=f"{_where}/showform.html",
    )
    def updateOne(self):
        return super().updateOne()


def includeme(config):
    if config.registry.settings.get("verbose", False):
        print(config.registry.settings, file=sys.stderr)
        print("includeme: ContextView(GenericView)", file=sys.stderr)
    config.scan()
