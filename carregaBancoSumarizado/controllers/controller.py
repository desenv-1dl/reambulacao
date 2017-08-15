#! -*- coding: UTF-8 -*-
from PyQt4.QtCore import QObject

class Controller(QObject):
    def __init__(self, loadLayersModel, loadLayersIconButton, loadLayersInterface):
        QObject.__init__(self)
        self.loadLayersIconButton = loadLayersIconButton
        self.loadLayersIconButton.setController(self)
        self.loadLayersInterface = loadLayersInterface
        self.loadLayersInterface.setController(self)
        self.loadLayersModel = loadLayersModel
        self.loadLayersModel.setController(self)
        self.initCommands()

    def initCommands(self):
        self.commands = { 'open loadLayersIconButton' : self.loadLayersIconButton.showButton,
                          'open loadLayersInterface'  : self.loadLayersInterface.showFrame,
                          'close loadLayersInterface'  : self.loadLayersInterface.closeFrame,
                          'open gif'                  : self.loadLayersInterface.openGif,
                          'get dataBases list'        : self.loadLayersModel.getDataBasesList,
                          'set connection postgres'   : self.loadLayersModel.setConnectionPostgres,
                          'get MIs list'              : self.loadLayersModel.getMIList,
                          'load layers'               : self.loadLayersModel.loadLayers,
                          'carregar estilos'          : self.loadLayersModel.carregarEstilos,
                        }

    def runCommand(self, cmd, params=None):
        if params:
            r = self.commands[cmd](params)
        else:
            r = self.commands[cmd]()
        return (r if r else '')

