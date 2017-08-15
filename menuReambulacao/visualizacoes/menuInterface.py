# -*- coding: utf-8 -*-
from qgis.gui import QgsAttributeDialog
from PyQt4 import QtCore, QtGui
from multiLayerSelection import MultiLayerSelection
from PyQt4.QtCore import QSettings
import psycopg2, sys, os, csv, resources
import os
import time
from shortcuts import ShortCut


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
  def _fromUtf8(s):
      return s

try:
  _encoding = QtGui.QApplication.UnicodeUTF8
  def _translate(context, text, disambig):
      return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
      return QtGui.QApplication.translate(context, text, disambig)
     
class MenuInterface(QtGui.QDockWidget):
    def __init__(self, iface, DB, d):
        QtGui.QDockWidget.__init__(self)
        self.dockWidgetContents = QtGui.QWidget()
        self.dataBase = d
        self.DB=DB
        self.iface=iface
        self.tool = MultiLayerSelection(self.iface.mapCanvas(), self.iface)
        self.caminho=""
        self.tabs={}
        self.setStyleSheet(u"background-color: rgb(205,205,205);")
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.botaoSelecionarCsv = QtGui.QPushButton(self.dockWidgetContents)
        self.botaoSelecionarCsv.setStyleSheet(u"color: rgb(0, 0, 0);background-color: rgb(205,205,205);")
        self.botaoSelecionarCsv.setObjectName(u"botaoSelecionarCsv")
        self.botaoSelecionarCsv.setText(u"Selecionar CSV")
        self.verticalLayout.addWidget(self.botaoSelecionarCsv)


        self.splitter_20 = QtGui.QSplitter(self.dockWidgetContents)
        self.splitter_20.setOrientation(QtCore.Qt.Horizontal)
        self.l = QtGui.QLabel(self.splitter_20)
        self.l.setStyleSheet(u"color: rgb(0, 0, 0);background-color: rgb(205,205,205);")
        self.l.setText( u"Estilo :")
        self.c = QtGui.QComboBox(self.splitter_20)
        self.c.setStyleSheet(u"color: rgb(0, 0, 0);background-color: rgb(205,205,205);")
        self.verticalLayout.addWidget(self.splitter_20)

        self.splitter_6 = QtGui.QSplitter(self.dockWidgetContents)
        self.splitter_6.setOrientation(QtCore.Qt.Horizontal)
        self.botaoSelecionarFeicao = QtGui.QPushButton(self.splitter_6)
        self.botaoSelecionarFeicao.setStyleSheet(u"color: rgb(0, 0, 0);background-color: rgb(205,205,205);")
        self.botaoSelecionarFeicao.setText( u"Selecionar Feição [F3] ")
        self.botaoSelecionarFeicao.clicked.connect(self.run)    
        self.abrirFormulario = QtGui.QPushButton(self.splitter_6)
        self.abrirFormulario.setStyleSheet(u"color: rgb(0, 0, 0);background-color: rgb(205,205,205);")
        self.abrirFormulario.setText(u"Abrir Formulário [F4]")
        self.abrirFormulario.clicked.connect(self.openFormAttribute)
        self.verticalLayout.addWidget(self.splitter_6)
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.verticalLayout.addWidget(self.line)
        self.splitter_3 = QtGui.QSplitter(self.dockWidgetContents)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.label = QtGui.QLabel(self.splitter_3)
        self.label.setStyleSheet(u"background-color: rgb(85, 255, 0);")
        self.label_2 = QtGui.QLabel(self.splitter_3)
        self.label_2.setStyleSheet(u"background-color: rgb(255, 255, 0);")
        self.label_5 = QtGui.QLabel(self.splitter_3)
        self.label_5.setStyleSheet(u"background-color: rgb(255, 0, 0);")
        self.label_3 = QtGui.QLabel(self.splitter_3)
        self.label_3.setStyleSheet(u"color: rgb(255, 255, 255);\n"
        u"background-color: rgb(0, 0, 0);")
        self.label_4 = QtGui.QLabel(self.splitter_3)
        self.label_4.setStyleSheet(u"background-color: rgb(0, 0, 255);\n"
        u"color: rgb(255, 255, 255);")
        self.verticalLayout.addWidget(self.splitter_3)
        self.modeReclass = QtGui.QCheckBox(self.dockWidgetContents)
        self.modeReclass.setText(u'Ativar Reclassificação')
        self.verticalLayout.addWidget(self.modeReclass)
        self.tabWidget = QtGui.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.West)
        self.tabWidget.setMovable(True)
        self.verticalLayout.addWidget(self.tabWidget)
        self.label.setText(u" Centroide ")
        self.label_2.setText(u"Delimitador")
        self.label_5.setText(u"    Área   ")
        self.label_3.setText(u"    Linha   ")
        self.label_4.setText(u"   Ponto  ")
        self.setWidget(self.dockWidgetContents)
        buttons = { 
                   u'select' : self.botaoSelecionarFeicao, 
                   u'form' : self.abrirFormulario
                   }
        self.teste = ShortCut(self.dockWidgetContents, self.tabWidget, buttons)
        self.mapShortcuts = {}
        self.mapMenu = {}

    def getStatusMode(self):
        return self.modeReclass.checkState() 
        
    def obterTabs(self):
        return self.tabs    

    def criarTab(self, listaCategorias):
        for categoria in listaCategorias:
            self.mapShortcuts[categoria]={}
            self.mapMenu[categoria]=[]
            tab_3 = QtGui.QWidget()
            tab_3.setObjectName(_fromUtf8(categoria))
            verticalLayout_4 = QtGui.QVBoxLayout(tab_3)
            verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
            scrollArea = QtGui.QScrollArea(tab_3)
            scrollArea.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
            scrollArea.setWidgetResizable(True)
            scrollArea.setObjectName(_fromUtf8("scrollArea"))
            scrollAreaWidgetContents = QtGui.QWidget()
            scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 325, 647))
            scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
            verticalLayout_3 = QtGui.QVBoxLayout(scrollAreaWidgetContents)
            verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
            scrollArea.setWidget(scrollAreaWidgetContents)
            verticalLayout_4.addWidget(scrollArea)
            self.tabWidget.addTab(tab_3, _fromUtf8(""))
            self.tabWidget.setTabText(self.tabWidget.indexOf(tab_3), _translate("Dialog", categoria, None))
            self.tabs[categoria]=[scrollAreaWidgetContents, verticalLayout_3]            
        self.tabWidget.setCurrentIndex(0)    

    def criarBotao(self, nomeB, nomeF, atalho=None):
        pushButton = QtGui.QPushButton(self.tabs.get(self.DB.get(nomeF))[0])            
        if nomeF[-1:] in ["p", "P"]:            
            pushButton.setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);background-color: rgb(0, 0, 255);"))
        elif nomeF[-1:] in ["l", "L"]:            
            pushButton.setStyleSheet(_fromUtf8("background-color: rgb(21, 7, 7);color: rgb(255, 255, 255);"))
        elif nomeF[-1:] in ["d", "D"]:            
            pushButton.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 0);"))
        elif nomeF[-1:] in ["c", "C"]:        
            pushButton.setStyleSheet(_fromUtf8("background-color: rgb(85, 255, 0);"))
        elif nomeF[-1:] in ["a", "A"]:
            pushButton.setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);background-color: rgb(246, 13, 13);"))        
        self.tabs.get(self.DB.get(nomeF))[1].addWidget(pushButton)
        pushButton.setText(_translate("Dialog",_fromUtf8(nomeB), None))
        pushButton.clicked.connect(lambda:self.setNomeBotao(pushButton))
        self.mapMenu[self.DB.get(nomeF)].append([nomeF, pushButton])
        if atalho:
            self.mapShortcuts[self.DB.get(nomeF)][int(atalho)]=pushButton
            pushButton.setText(unicode(nomeB+" ["+str(atalho)+"]"))
        pushButton.setObjectName(_fromUtf8(_fromUtf8(nomeB)))
        return pushButton

    def reStyle(self):
        for aba in self.mapMenu:
            for data in self.mapMenu[aba]:
                if data[0][-1:] in ["p", "P"]:
                    data[1].setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);background-color: rgb(0, 0, 255);"))
                elif data[0][-1:] in ["l", "L"]:
                    data[1].setStyleSheet(_fromUtf8("background-color: rgb(21, 7, 7);color: rgb(255, 255, 255);"))
                elif data[0][-1:] in ["d", "D"]:
                    data[1].setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 0);"))
                elif data[0][-1:] in ["c", "C"]:
                    data[1].setStyleSheet(_fromUtf8("background-color: rgb(85, 255, 0);"))
                elif data[0][-1:] in ["a", "A"]:
                    data[1].setStyleSheet(_fromUtf8("color: rgb(255, 255, 255);background-color: rgb(246, 13, 13);"))        
    
    def registerShortcuts(self):
        self.teste.setMapShortcuts(self.mapShortcuts)
    
    def registerMapMenu(self):
        pass

    def setNomeBotao(self, b):
        self.reStyle()
        b.setStyleSheet(u"background-color: rgb(253, 97, 0);")
        self.NomeBotao = b.objectName()

    def obterNomeBotao(self):
        return self.NomeBotao
    
    def run(self): 
        self.iface.mapCanvas().setMapTool(self.tool)
        
    def cleanCursor(self):
        self.iface.mapCanvas().unsetMapTool(self.tool)
                
    def getValueSelection(self):
        return self.tool.getSelectionsLayers()

    def runBackup(self):
        self.Dialog = QtGui.QDialog(self.iface.mainWindow())
        self.menu2 = Ui_Backup(self.Dialog, self.iface)   
        self.Dialog.show()    

    def openFormAttribute(self):
        lyr = self.iface.mapCanvas().currentLayer()
        if lyr:
            f = lyr.selectedFeatures()[0]
            attrDialog = QgsAttributeDialog(lyr, f, False)
            result = attrDialog.exec_()

    def removeSelecoes(self):
        for i in range(len(self.iface.mapCanvas().layers())):
            try:
                self.iface.mapCanvas().layers()[i].removeSelection()
            except:
                pass    
        
    def showDialog(self):
        self.iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self)











