#! -*- coding: UTF-8 -*-
from PyQt4.QtCore import QObject

class Controlador(QObject):
    def __init__(self, carregaEstilosModelo, carregaEstilosBotaoPrincipal, carregaEstilosInterface):
        QObject.__init__(self)
        self.carregaEstilosBotaoPrincipal = carregaEstilosBotaoPrincipal
        self.carregaEstilosBotaoPrincipal.definirControlador(self)
        self.carregaEstilosInterface = carregaEstilosInterface
        self.carregaEstilosInterface.definirControlador(self)
        self.carregaEstilosModelo = carregaEstilosModelo
        self.carregaEstilosModelo.definirControlador(self)
        self.inicializarComandos()

    def inicializarComandos(self):
        self.comandos = {
        'abrir botao principal' : self.carregaEstilosBotaoPrincipal.abrir,
        'fechar botao principal' : self.carregaEstilosBotaoPrincipal.fechar,
        'abrir carrega estilos interface' : self.carregaEstilosInterface.abrir,
        'fechar carrega estilos interface' : self.carregaEstilosInterface.fechar,
        'obter lista de bancos' :  self.carregaEstilosModelo.obterListaDeBancos ,
        'definir conexao postgres' :  self.carregaEstilosModelo.definirPostgres ,
        'obter lista de tipos de estilos' :  self.carregaEstilosModelo.obterTiposDeEstilos ,
        'obter lista de cartas' :  self.carregaEstilosModelo.obterCartas ,
        'estilizar camadas' :  self.carregaEstilosModelo.estilizarCamadas ,
        'fechar gif' :  self.carregaEstilosInterface.fecharGif ,
                        }

    def rodarComando(self, cmd, params=None):
        if params:
            r = self.comandos[cmd](params)
        else:
            r = self.comandos[cmd]()
        return (r if r else '')

