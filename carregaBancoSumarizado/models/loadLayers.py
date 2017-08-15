# -*- coding: utf-8 -*-
from dataBase import DataBase

class LoadLayers(DataBase):
    def __init__(self, iface):
        DataBase.__init__(self)
        self.iface = iface

    def setController(self, c):
        self.controller = c

    def getController(self):
        return self.controller


