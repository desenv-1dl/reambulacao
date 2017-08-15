from menuReambulacao.main import MenuReambulacaoMain
from carregaBancoSumarizado.carregaCamadas import CarregaCamadas
from carregaEstilos.carregaEstilosMain import CarregaEstilosMain
class Main:
    def __init__(self, iface):
       self.carregaCamadas = CarregaCamadas(iface)
       self.carregaEstilosMain = CarregaEstilosMain(iface)
       self.menu = MenuReambulacaoMain(iface)

    def initGui(self):
       self.carregaCamadas.initGui()
       self.carregaEstilosMain.initGui()
       self.menu.initGui()

    def unload(self):
        self.carregaCamadas.unload()
        self.carregaEstilosMain.unload()
        self.menu.unload()
