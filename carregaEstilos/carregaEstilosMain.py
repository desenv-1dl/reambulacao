#! -*- coding : utf-8 -*- 
from visualizacoes.carregaEstilosBotaoPrincipal import CarregaEstilosBotaoPrincipal
from visualizacoes.carregaEstilosInterface import CarregaEstilosInterface
from modelos.carregaEstilosModelo import CarregaEstilosModelo
from controles.controlador import Controlador

class CarregaEstilosMain:
    def __init__(self, iface):
        carregaEstilosBotaoPrincipal =  CarregaEstilosBotaoPrincipal(iface)
        carregaEstilosInterface = CarregaEstilosInterface()
        carregaEstilosModelo = CarregaEstilosModelo(iface)
        controlador = Controlador(carregaEstilosModelo, carregaEstilosBotaoPrincipal, carregaEstilosInterface)
        self.definirControlador(controlador)

    def definirControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def initGui(self):
        self.obterControlador().rodarComando('abrir botao principal')

    def unload(self):
        self.obterControlador().rodarComando('fechar botao principal')

