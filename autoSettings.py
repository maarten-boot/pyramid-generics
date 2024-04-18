import sys
from collections import OrderedDict
import importlib

from typing import (
    Dict,
    List,
    Any,
)

from menue import makeMenue


def addAutoPaths(
    paths: Dict[str, OrderedDict],
    name: str,
) -> None:
    paths[name]["listAll"] = "/"
    paths[name]["new"] = "/new"
    paths[name]["add"] = "/add"
    paths[name]["showOne"] = "/show/{id}"
    paths[name]["update"] = "/update"
    paths[name]["delete"] = "/delete/{id}"


def makeAutoSettings(
    modelList: List[str],
    address: str = "0.0.0.0",
    port: int = 6543,
    verbose: bool = False,
) -> Dict[str, Any]:

    paths = {}
    models: Dict[str, Any] = {}

    for k in modelList:
        _class = getattr(importlib.import_module(f"models.{k.lower()}"), k)
        _instance = _class()
        gM = getattr(_instance, "_genericMeta")
        gD = getattr(_instance, "_genericData")
        _name: str = gM.get("name")

        models[k] = {
            "genericMeta": gM,
            "genericData": gD,
            "name": _name,
        }
        paths[_name] = OrderedDict()
        addAutoPaths(paths, _name)

        if verbose:
            print(_name, file=sys.stderr)

    settings: Dict[str, Any] = {
        "verbose": verbose,
        "autoPaths": paths,
        "modelList": modelList,
        "models": models,  # a dict holding info on all models used and their meta info
        "menue": makeMenue(modelList),
    }

    if verbose:
        print(f"settings: {settings}", file=sys.stderr)

    return settings
