from visualizacoes.botaoPrincipal import BotaoPrincipal
from visualizacoes.definirBancoDeDadosInterface import DefinirBancoDeDadosInterface
from visualizacoes.menuInterface import MenuInterface
from controladores.controlador import Controlador
from modelos.bancoDeDados import BancoDeDados
from modelos.menuModelo import MenuModelo
from PyQt4 import QtGui, QtCore

class MenuReambulacaoMain(QtCore.QObject):
    def __init__(self, iface):
        QtCore.QObject.__init__(self)
        botaoPrincipal = BotaoPrincipal(iface)
        definirBancoDeDadosInterface = DefinirBancoDeDadosInterface()
        bancoDeDados = BancoDeDados(iface)
        menuModelo = MenuModelo(iface, MenuInterface)
        controlador = Controlador(bancoDeDados, botaoPrincipal, definirBancoDeDadosInterface, menuModelo)
        self.registrarControlador(controlador)

    def registrarControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def initGui(self):
        self.obterControlador().rodarComando('inicializar botao principal', 'True')

    def unload(self):
        self.obterControlador().rodarComando('inicializar botao principal', 'False')

