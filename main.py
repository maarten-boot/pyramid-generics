from collections import OrderedDict

from typing import (
    Dict,
)

from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from pyramid.view import view_config

from models.students import Students
from menue import Menue

secret = "mhshshs yverylongsecret of minimal 64 chars and possibly longer with som random data would be fine ;clnaskafdihweflmxnxcaz"
MySession = SignedCookieSessionFactory(secret=secret)


def makeMenue() -> OrderedDict:
    menu = Menue()

    menu.addItem(
        path="/",
        label="Home",
    )
    menu.addItem(
        path=f"/{Students._genericMeta['name']}/",
        label=Students._genericMeta["labelP"],
    )

    return menu.getMenuAsDict()


def addDefaultPaths(paths: Dict[str, OrderedDict], name: str) -> None:
    paths[name]["listAll"] = "/"
    paths[name]["new"] = "/new"
    paths[name]["add"] = "/add"
    paths[name]["showOne"] = "/show/{id}"
    paths[name]["update"] = "/update"
    paths[name]["delete"] = "/delete/{id}"


@view_config(
    route_name="index",
    renderer="views/templates/base.html",
)
def index(request):
    data = {
        "currentUrl": "/",
        "relativeUrl": "/",
        "menue": makeMenue(),
    }
    return data


if __name__ == "__main__":
    name = Students._genericMeta["name"]
    paths = {
        name: OrderedDict(),
    }
    addDefaultPaths(paths, name)

    with Configurator() as config:
        config.set_session_factory(MySession)
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")

        config.add_route("index", "/")
        for m, pInfo in paths.items():
            for k, v in pInfo.items():
                config.add_route(f"{m}/{k}", f"{m}{v}")

        config.scan(f"views.{name}View")
        config.scan()
        app = config.make_wsgi_app()

    server = make_server("0.0.0.0", 6543, app)
    server.serve_forever()
