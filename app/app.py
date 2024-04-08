#! /usr/bin/env python3

import hashlib
from typing import (
    List,
    Tuple,
)

from wsgiref.simple_server import make_server

from pyramid.config import Configurator
from pyramid.view import view_config
from pyramid.session import SignedCookieSessionFactory
from pyramid.httpexceptions import HTTPFound


secret = "myverylongsecret of minimal 64 chars and possibly longer with som random data would be fine ;clnaskafdihweflmxnxcaz"
MySession = SignedCookieSessionFactory(secret=secret)


MyList: List[Tuple[str, str]] = []


def setSessionCredentials(request) -> None:
    request.session["credentials"] = MyList


def setSession(request, username: str, password: str):
    request.session["username"] = username
    request.session["password"] = password
    request.session["logged_in"] = True


def clearSession(request) -> None:
    request.session.pop("username", None)
    request.session.pop("password", None)
    request.session["logged_in"] = False


def loginOk(request, username: str, password: str):
    setSession(request, username, password)
    url = request.route_url("index")
    return HTTPFound(location=url)


def findUser(username) -> Tuple[str, str]:
    for i in MyList:
        if i[0] == username:
            return i
    return None


def userPolicy(username, password) -> str:
    if len(username) < 8:
        return "username must me at least 8 characters long"

    if len(password) < 16:
        return "Password must be at least 16 characytters long"

    if username == password:
        return "Username cannot be identical to the password"

    return ""


def err(request, msg: str):
    clearSession(request)
    request.session.flash(msg)
    data = {
        "error": msg,
    }
    return data


@view_config(
    route_name="login",
    renderer="templates/login.html",
    request_method=["POST", "GET"],
)
def login(request):
    if request.method != "POST":
        data = {}
        return data

    # extract post data
    username = request.POST["username"]
    password = request.POST["password"]

    if len(username) == 0 or len(password) == 0:
        msg = "Please fill in all fields properly!"
        return err(request, msg)

    # find the user
    j = findUser(username)
    if j is None:
        msg = "User Not found, try 'Sign Up' first"
        return err(request, msg)

    hash_object = hashlib.sha1(password.encode("utf-8"))
    pwHash = hash_object.hexdigest()

    if j[1] != pwHash:
        msg = "Mismatch pass"
        return err(request, msg)

    return loginOk(request, username, pwHash)


@view_config(
    route_name="signup",
    renderer="templates/signup.html",
    request_method=["POST", "GET"],
)
def signup(request):
    if request.method != "POST":
        data = {}
        return data

    # extract post data
    username = request.POST["username"]
    password = request.POST["password1"]
    password2 = request.POST["password2"]

    if len(username) == 0 or len(password) == 0 or len(password2) == 0:
        msg = "Please fill in all fields properly!"
        return err(request, msg)

    msg = userPolicy(username, password)
    if msg != "":
        return err(request, msg)

    if password != password2:
        msg = "Passwords do not match!"
        return err(request, msg)

    if findUser(username):
        msg = "Username already exists!"
        return err(request, msg)

    hash_object = hashlib.sha1(password.encode("utf-8"))
    pwHash = hash_object.hexdigest()

    MyList.append((username, pwHash))
    setSessionCredentials(request)

    return loginOk(request, username, pwHash)


@view_config(
    route_name="index",
    renderer="templates/index.html",
    request_method="GET",
)
def index(request):  # pylint: disable=unused-argument
    data = {}
    return data


@view_config(
    route_name="logout",
    renderer="templates/logout.html",
    request_method="GET",
)
def logout(request):
    clearSession(request)

    data = {
        "error": "You have been logged out!",
    }
    return data


def makeApp():
    rr = [
        {
            "name": "index",
            "path": "/",
        },
        {
            "name": "login",
            "path": "/login",
        },
        {
            "name": "logout",
            "path": "/logout",
        },
        {
            "name": "signup",
            "path": "/signup",
        },
    ]

    with Configurator() as config:
        config.set_session_factory(MySession)
        config.include("pyramid_jinja2")  # Add Jinja2 Template Renderer
        config.add_jinja2_renderer(".html")

        for r in rr:
            config.add_route(r["name"], r["path"])
        config.scan()  # scan for views in the current code

        return config.make_wsgi_app()  # make a app


if __name__ == "__main__":
    listenAddress: str = "0.0.0.0"
    listenPort: int = 6543

    app = makeApp()

    server = make_server(
        listenAddress,
        listenPort,
        app,
    )
    server.serve_forever()
