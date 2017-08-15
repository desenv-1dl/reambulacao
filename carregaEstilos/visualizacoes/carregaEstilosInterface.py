#! -*- coding: UTF-8 -*-
from PyQt4 import QtCore, QtGui, uic
import sys, os

sys.path.append(os.path.dirname(__file__))
GUI, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'carregaEstilosInterface.ui' ), resource_suffix='')

class CarregaEstilosInterface(QtGui.QFrame, GUI):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        GUI.__init__(self)
        self.setupUi(self)
        self.inicializarVariaveis()
        self.configurarGif()

    def configurarGif(self):
        self.gifLabel.setVisible(False)
        gif = os.path.join(os.path.dirname(__file__), 'loading.gif')
        self.movie = QtGui.QMovie(gif)
        self.gifLabel.setMovie(self.movie)
        self.movie.start()

    def abrirGif(self):
        self.mainFrame.hide()
        self.gifLabel.setVisible(True)

    def fecharGif(self):
        self.mainFrame.show()
        self.gifLabel.setVisible(False)

    def inicializarVariaveis(self):
        self.controlador = None

    def definirControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def abrir(self):
        self.iniciallizarInterface()
        self.show()

    def fechar(self):
        self.close()

    def iniciallizarInterface(self):
        self.carregarBancoCombo()

    def carregarCombo(self, cb, data=False):
        cb.clear()
        cb.addItem(u"<Opções>")
        if data:
            cb.addItems(data)

    def carregarBancoCombo(self):
        dbs  = self.obterControlador().rodarComando('obter lista de bancos')
        self.carregarCombo(self.bancoCombo, dbs)

    def carregarEstilosCombo(self):
        estilos  = self.obterControlador().rodarComando('obter lista de tipos de estilos')
        self.carregarCombo(self.estiloCombo, estilos)

    def carregarCartaCombo(self, banco):
        if banco:
            self.obterControlador().rodarComando('definir conexao postgres', (banco,))
            cartas = self.obterControlador().rodarComando('obter lista de cartas')
            self.carregarCombo(self.cartaCombo, cartas+(u'edgv',)) if cartas else self.carregarCombo(self.cartaCombo, (u'edgv',))
            self.carregarEstilosCombo()

    def definirCarta(self, c):
        self.carta = c

    def obterCarta(self):
        return self.carta

    def definirBanco(self, b):
        self.bancoDeDados = b

    def obterBanco(self):
        return self.bancoDeDados

    def definirEstilo(self, e):
        self.estilo = e

    def obterEstilo(self):
        return self.estilo

    def obterEscolhaDeUsuario(self):
        if not(u"<Opções>" in self.obterEstilo()+self.obterBanco()+self.obterCarta()):
            return (self.obterEstilo(),self.obterBanco(),self.obterCarta(),)

    @QtCore.pyqtSlot(str)
    def on_bancoCombo_currentIndexChanged(self, banco):
        idx = self.bancoCombo.currentIndex()
        self.definirBanco(banco)
        if idx == 0:
            self.carregarCombo(self.cartaCombo)
            self.carregarCombo(self.estiloCombo)
        else:
            self.carregarCartaCombo(banco)

    @QtCore.pyqtSlot(str)
    def on_cartaCombo_currentIndexChanged(self, carta):
        self.definirCarta(carta)

    @QtCore.pyqtSlot(str)
    def on_estiloCombo_currentIndexChanged(self, estilo):
        self.definirEstilo(estilo)

    @QtCore.pyqtSlot(bool)
    def on_carregarBotao_clicked(self):
        if self.obterEscolhaDeUsuario():
            self.abrirGif()
            self.obterControlador().rodarComando('estilizar camadas', self.obterEscolhaDeUsuario())


