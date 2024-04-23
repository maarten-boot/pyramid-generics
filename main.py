from wsgiref.simple_server import make_server
from pyramid.session import SignedCookieSessionFactory
from pyramid.config import Configurator

from autoSettings import makeAutoSettings

secret = "mhshshs yverylongsecret of minimal 64 chars and possibly longer with som random data would be fine ;clnaskafdihweflmxnxcaz"
my_session_factory = SignedCookieSessionFactory(secret=secret)


def makeApp(settings):
    paths = settings.get("autoPaths")
    models = settings.get("models")

    with Configurator(settings=settings) as config:
        config.set_session_factory(my_session_factory)
        config.include("pyramid_jinja2")
        config.add_jinja2_renderer(".html")

        config.add_route(name="index", pattern="/")  # name, pattern
        for name, pInfo in paths.items():
            with config.route_prefix_context(name):
                for k, v in pInfo.items():
                    config.add_route(name=f"{name}/{k}", pattern=f"{v}")

        name = "main"
        config.scan(f"views.{name}View")

        for k in modelList:
            name = models[k]["name"]
            config.include(f"views.{name}View")
            config.commit()

        app = config.make_wsgi_app()
        return app


if __name__ == "__main__":
    myAddress = "0.0.0.0"
    myPort = 6543
    verbose = True

    models = [
        "model.students.Students",
        "model.context.Context",
    ]

    modelList = [
        "Students",
        "Context",
    ]

    settings = makeAutoSettings(
        modelList,
        address=myAddress,
        port=myPort,
        verbose=verbose,
    )
    app = makeApp(
        settings=settings,
    )
    server = make_server(
        myAddress,
        myPort,
        app,
    )
    server.serve_forever()
