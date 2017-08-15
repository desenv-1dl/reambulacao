#! -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import resources

class CarregaEstilosBotaoPrincipal(QtCore.QObject):
    def __init__(self, iface):
        QtCore.QObject.__init__(self)
        self.inicializarVariaveis()
        self.definirIface(iface)
        self.definirBotaoPrincipal(self.criarBotaoPrincipal())

    def inicializarVariaveis(self):
        self.botaoPrincipal = None
        self.iface = None
        self.controlador = None

    def definirControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def definirIface(self, i):
        self.iface = i

    def obterIface(self):
        return self.iface

    def definirBotaoPrincipal(self, b):
        self.botaoPrincipal = b

    def obterBotaoPrincipal(self):
        return self.botaoPrincipal

    def criarBotaoPrincipal(self):
        botao = QtGui.QAction(QtGui.QIcon(":/plugins/reambulacao/carregaEstilos/visualizacoes/style.jpeg"), 
                u"Carrega Estilos", self.obterIface().mainWindow())
        botao.triggered.connect(self.rodar)
        return botao

    def rodar(self):
        self.obterControlador().rodarComando('abrir carrega estilos interface')

    def abrir(self):
        self.obterIface().digitizeToolBar().addAction(self.obterBotaoPrincipal())

    def fechar(self):
        self.obterIface().digitizeToolBar().removeAction(self.obterBotaoPrincipal())

