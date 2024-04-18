from pyramid.view import view_config

from models.students import Students
from views.genericView import GenericView

_m = "students"


class StudentView(GenericView):
    modelName = "Students"
    _m = _m

    def __init__(self, request):
        super().__init__(request)
        self.model = Students
        self.relativeUrl = f"/{_m}/"

    @view_config(
        route_name=f"{_m}/new",
        renderer="templates/generic/newform.html",
        request_method="GET",
    )
    def newStudent(self):  # pylint: disable=unused-argument
        return super().newItem()

    @view_config(
        route_name=f"{_m}/listAll",
        renderer="templates/generic/listall.html",
        request_method="GET",
    )
    def listAll(self):  # pylint: disable=unused-argument
        return super().listAll()

    @view_config(
        route_name=f"{_m}/showOne",
        renderer="templates/generic/showform.html",
        request_method="GET",
    )
    def showOne(self):
        return super().showOne()

    @view_config(
        route_name=f"{_m}/delete",
        renderer="templates/generic/delete.html",
        request_method="GET",
    )
    def deleteOne(self):
        return super().deleteOne()

    @view_config(
        route_name=f"{_m}/add",
        request_method="POST",
        renderer="templates/generic/newform.html",
    )
    def addOne(self):
        return super().addOne()

    @view_config(
        route_name=f"{_m}/update",
        request_method="POST",
        renderer="templates/generic/showform.html",
    )
    def updateOne(self):
        return super().updateOne()
