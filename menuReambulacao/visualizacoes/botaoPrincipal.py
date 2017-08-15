#! -*- coding: utf-8 -*-

import os
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QObject
from qgis.gui import QgsMessageBar
import resources

class BotaoPrincipal(QObject):
    def __init__(self, iface):
        QObject.__init__(self)
        self.inicializarVariaveis()
        self.iface = iface
        self.definirBotao(self.criarBotao())

    def inicializarVariaveis(self):
        self.iface = None
        self.botao = None
        self.controlador = None

    def registrarControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def definirBotao(self, b):
        self.botao = b

    def obterBotao(self):
        return self.botao

    def criarBotao(self):
        botao = QtGui.QAction(QtGui.QIcon(":/plugins/reambulacao/menuReambulacao/visualizacoes/icons/icon.png"), u"Menu de Reambulação", self.iface.mainWindow())
        botao.triggered.connect(self.rodar)
        return botao

    def mostrarBotao(self, bo):
        if bo == 'True':
            self.iface.digitizeToolBar().addAction(self.obterBotao())
        else:
            self.iface.digitizeToolBar().removeAction(self.obterBotao())

    def rodar(self):
        self.obterControlador().rodarComando('inicializar selecao de banco de dados')


