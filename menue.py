from collections import OrderedDict


class Menue:
    def __init__(self, verbose: bool = False) -> None:
        self.menue: OrderedDict = OrderedDict()

    def addItem(self, path: str, label: str) -> None:
        self.menue[path] = label

    def getMenuAsDict(self) -> OrderedDict:
        return self.menue
