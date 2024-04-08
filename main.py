from collections import OrderedDict
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

from models.base import getDbSession
from models.students import Students

secret = "mhshshs yverylongsecret of minimal 64 chars and possibly longer with som random data would be fine ;clnaskafdihweflmxnxcaz"
MySession = SignedCookieSessionFactory(secret=secret)


dbSession = getDbSession()

if __name__ == "__main__":

    name = Students._genericMeta["name"]
    paths = {
        name: OrderedDict(),
    }
    paths[name]["listAll"] = "/"
    paths[name]["new"] = "/new"
    paths[name]["add"] = "/add"
    paths[name]["showOne"] = "/show/{id}"
    paths[name]["update"] = "/update"
    paths[name]["delete"] = "/delete/{id}"

    with Configurator() as config:
        config.set_session_factory(MySession)
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")

        for m, pInfo in paths.items():
            for k, v in pInfo.items():
                print(m, k, v)
                config.add_route(f"{m}/{k}", f"{m}{v}")
                print(f"{m}/{k}", f"{m}{v}")

        config.scan("views.studentView")
        app = config.make_wsgi_app()

    server = make_server("0.0.0.0", 6543, app)
    server.serve_forever()
