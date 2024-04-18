from collections import OrderedDict
import importlib

from typing import (
    List,
)


class Menue:
    def __init__(self, verbose: bool = False) -> None:
        self.menue: OrderedDict = OrderedDict()

    def addItem(self, path: str, label: str) -> None:
        self.menue[path] = label

    def getMenuAsDict(self) -> OrderedDict:
        return self.menue


def makeMenue(modelList: List[str]) -> OrderedDict:
    menu = Menue()
    menu.addItem(path="/", label="Home")

    for k in modelList:
        _class = getattr(importlib.import_module(f"models.{k.lower()}"), k)
        _instance = _class()
        gM = getattr(_instance, "_genericMeta")

        name = gM.get("name")
        label = gM.get("labelP")

        menu.addItem(path=f"/{name}/", label=label)

    return menu.getMenuAsDict()
