# -*- coding: utf-8 -*-                                                           
from PyQt4 import QtCore, QtGui, uic, QtGui
from qgis.gui import QgsMessageBar
import sys, os
import resources

sys.path.append(os.path.dirname(__file__))
GUI, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'ui/definirBancoDeDados.ui'), resource_suffix='')

class DefinirBancoDeDadosInterface(QtGui.QFrame, GUI):
    def __init__(self):
        QtGui.QFrame.__init__(self)
        GUI.__init__(self)
        self.setupUi(self)
        self.inicializarVariaveis()
	self.gifLabel.setVisible(False)
	self.configGif()
	
    def inicializarVariaveis(self):
        self.bancoDeDados = None
        self.controlador = None
        self.view = None
	self.movie = None

    def configGif(self):
        gif = os.path.join(os.path.dirname(__file__), 'loading.gif')
        self.movie = QtGui.QMovie(gif)
        self.gifLabel.setMovie(self.movie)
        self.movie.start()

    def iniciarGif(self):
        self.mainFrame.hide()
        self.gifLabel.setVisible(True)
        
    def terminarGif(self):
        self.mainFrame.show()
        self.gifLabel.setVisible(False)

    def registrarControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def listarConexoes(self):
        self.opcionalFrame.hide()
        conexoes = self.obterControlador().rodarComando('obter lista de conexoes')
        self.carregarCombo(self.conexoesCombo, conexoes)

    def listarSchemas(self, nomeBaseDeDados):
         self.opcionalFrame.hide()
         if self.validarSelecao(nomeBaseDeDados):
            self.obterControlador().rodarComando('conectar em postgresql', (self.obterBancoDeDados(),)) 
            schemas = self.obterControlador().rodarComando('obter lista de schemas')
            if schemas:
                self.carregarCombo(self.sumarizadoCombo, schemas)
                self.opcionalFrame.show()

    def validarSelecao(self, selecao):
        if (selecao !=  u'<Opções>') and selecao:
            return True
        return False

    def carregarCombo(self, combo, lista=None):
        combo.clear()
        dados = (u'<Opções>',)
        if lista:
            dados = dados+lista
        combo.addItems(dados)

    def definirBancoDeDados(self, b):
        self.bancoDeDados = b

    def obterBancoDeDados(self):
        return self.bancoDeDados

    def definirView(self, v):
        self.view = v

    def obterView(self):
        return self.view

    @QtCore.pyqtSlot(str)
    def on_conexoesCombo_currentIndexChanged(self, nome):
        self.carregarCombo(self.sumarizadoCombo)
        if self.validarSelecao(nome):
            self.definirBancoDeDados(nome)
            self.listarSchemas(nome)
        else:
            self.carregarCombo(self.sumarizadoCombo)
            self.definirBancoDeDados(u'<Opções>')
            self.listarSchemas(nome)

    @QtCore.pyqtSlot(str)
    def on_sumarizadoCombo_currentIndexChanged(self, nome):
        self.definirView(nome)

    @QtCore.pyqtSlot(bool)
    def on_definirButton_clicked(self):
            banco = None
            schema = None
            if self.validarSelecao(self.obterBancoDeDados()):
                banco = self.obterBancoDeDados()
            if self.validarSelecao(self.obterView()):
                schema = self.obterView()
            dados = tuple(x for x in [banco, schema] if x is not None)
            self.obterControlador().rodarComando('ativar menu', dados)

    def mostrarFrame(self):
        self.listarConexoes()
        self.show()



