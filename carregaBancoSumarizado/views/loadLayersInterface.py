# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui, uic, QtGui
from qgis.gui import QgsMessageBar
import sys, os
import resources

sys.path.append(os.path.dirname(__file__))
GUI, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'loadLayersInterface.ui'), resource_suffix='')

class LoadLayersInterface(QtGui.QFrame, GUI):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        GUI.__init__(self)
        self.setupUi(self)
        self.initVariables()
        self.gifLabel.setVisible(False)
        self.configGif()

    def initVariables(self):
        self.controller = None
        self.db = None
        self.mi = None
        self.tp = None
        self.movie = None
        self.estilo = None

    def configGif(self):
        gif = os.path.join(os.path.dirname(__file__), 'loading.gif')
        self.movie = QtGui.QMovie(gif)
        self.gifLabel.setMovie(self.movie)
        self.movie.start()

    def openGif(self, b):
        if b == 'True':
            self.mainFrame.hide()
            self.gifLabel.setVisible(True)
        else:
            self.mainFrame.show()
            self.gifLabel.setVisible(False)

    def setController(self, c):
        self.controller = c

    def getController(self):
        return self.controller

    def showFrame(self):
        self.loadDataBases()
        self.carregarTiposDeEstilo()
        self.loadTypes()
        self.show()
    
    def closeFrame(self):
        self.close()
    
    def carregarTiposDeEstilo(self):
        estilos  = self.getController().runCommand('carregar estilos')
        self.loadCombo(self.estiloCombo, estilos)

    def loadDataBases(self):
        dbs  = self.getController().runCommand('get dataBases list')
        self.loadCombo(self.dataBaseCombo, dbs)

    def loadMIs(self, db):
        if db:
            self.getController().runCommand('set connection postgres', (db,)) 
            mis = self.getController().runCommand('get MIs list')
            self.loadCombo(self.miCombo, mis+('edgv',)) if mis else self.loadCombo(self.miCombo, ('edgv',))
            self.carregarTiposDeEstilo()

    def loadTypes(self):
        self.loadCombo(self.typeCombo, [u"Carregar Todas as Camadas",
        u"Carregar Apenas Camadas com Feiçoes"])

    def loadCombo(self, cb, data=False):
        cb.clear()
        cb.addItem(u"<Opções>")
        if data:
            cb.addItems(data)

    def setMI(self, i):
        self.mi = i

    def getMI(self):
        return self.mi

    def setDataBase(self, i):
        self.db = i

    def getDataBase(self):
        return self.db

    def setTypeLoad(self, i):
        self.tp = i

    def getTypeLoad(self):
        return self.tp

    def getDataToLoad(self):
        db = self.getDataBase()
        mi = self.getMI()
        typeLoad = self.getTypeLoad()
        if not(0 in [db, mi, typeLoad, self.estiloCombo.currentIndex()]):
            return (self.dataBaseCombo.currentText(),
                    self.miCombo.currentText(),
                    typeLoad,
                    self.estiloCombo.currentText(),)
        elif (self.estiloCombo.currentIndex()==0) and (not (0 in [db, mi, typeLoad,])):
            return (self.dataBaseCombo.currentText(),
                    self.miCombo.currentText(),
                    typeLoad,
                    self.estiloCombo.currentText(),)

    @QtCore.pyqtSlot(str)
    def on_dataBaseCombo_currentIndexChanged(self, text):
        idx = self.dataBaseCombo.currentIndex()
        self.setDataBase(idx)
        if idx == 0:
           self.loadCombo(self.miCombo)
        else:
            self.loadMIs(text)

    @QtCore.pyqtSlot(str)
    def on_miCombo_currentIndexChanged(self, text):
        idx = self.miCombo.currentIndex()
        self.setMI(idx)

    @QtCore.pyqtSlot(str)
    def on_typeCombo_currentIndexChanged(self, text):
        idx = self.typeCombo.currentIndex()
        self.setTypeLoad(idx)

    @QtCore.pyqtSlot(bool)
    def on_loadButton_clicked(self):
        if self.getDataToLoad():
            self.getController().runCommand('load layers', self.getDataToLoad())


