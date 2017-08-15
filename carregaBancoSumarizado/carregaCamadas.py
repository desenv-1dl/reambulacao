from views.loadLayersInterface import LoadLayersInterface
from views.loadLayersIconButton import LoadLayersIconButton
from controllers.controller import Controller
from models.loadLayers import LoadLayers

class CarregaCamadas:
    def __init__(self, iface):
        loadLayersIconButton = LoadLayersIconButton(iface)
        loadLayersInterface = LoadLayersInterface()
        loadLayersModel = LoadLayers(iface)
        self.controller = Controller(loadLayersModel, loadLayersIconButton, loadLayersInterface)

    def initGui(self):
        self.controller.runCommand('open loadLayersIconButton', 'True')

    def unload(self):
        self.controller.runCommand('open loadLayersIconButton', 'False')

