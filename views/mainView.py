from pyramid.view import view_config


@view_config(
    route_name="index",
    renderer="templates/base.html",
)
def index(request):
    action = ""
    relativeUrl = "/"
    currentUrl = relativeUrl + action

    settings = request.registry.settings
    menue = settings.get("menue")

    data = {
        "currentUrl": currentUrl,
        "relativeUrl": relativeUrl,
        "menue": menue,
    }
    return data
