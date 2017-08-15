# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from qgis import core, gui
from bancoDeDadosModelo import BancoDeDadosModelo
from loadCacheLayersModelo import LoadCacheLayersModelo

class CarregaEstilosModelo:
    def __init__(self, iface):
        self.inicializarVariaveis()
        self.definirIface(iface)
        self.definirBanco( BancoDeDadosModelo())

    def inicializarVariaveis(self):
        self.controlador = None
        self.bancoDeDados = None
        self.iface = None
        self.dados = None

    def definirIface(self, i):
        self.iface = i

    def obterIface(self):
        return self.iface

    def definirControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def definirBanco(self, b):
        self.bancoDeDados = b

    def obterBanco(self):
        return self.bancoDeDados

    def obterListaDeBancos(self):
        return self.obterBanco().obterListaDeBancos()

    def definirPostgres(self, param):
       self.obterBanco().definirConexaoPostgres(param)

    def obterTiposDeEstilos(self):
        return self.obterBanco().obterListaDeTiposDeEstilos()

    def obterCartas(self):
        return self.obterBanco().obterListaDeCartas()

    def definirDadosSelecaoUsuario(self, d):
        self.dados = d

    def obterDadosSelecaoUsuario(self):
        return self.dados

    def estilizarCamadas(self, dados):
        self.definirDadosSelecaoUsuario(dados)
        informacoes = self.obterBanco().obterDadosDeConexao()+(dados[-1],)
        thread = QtCore.QThread(self.iface.mainWindow())
        worker =  LoadCacheLayersModelo(informacoes, self.obterBanco().obterConexaoPostgres())
        worker.moveToThread(thread)
        worker.finished.connect(self.inserirEstiloNaCamada)
        #worker.run()
        thread.started.connect(worker.run)
        thread.start()
        self.thread = thread
        self.worker = worker

    def inserirEstiloNaCamada(self, camadas, dados):
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        bancoAtual = self.obterBanco().obterDadosDeConexao()[0]
        estilosBanco =  self.obterBanco().obterEstilosId()
        camadasCarregadas = core.QgsMapLayerRegistry.instance().mapLayers().values()
        if camadasCarregadas :
            for camadaCrua in camadasCarregadas:
                for camadaModelo in camadas:
                    bancoDaCamada = camadaCrua.dataProvider().dataSourceUri().split(' ')[0][8:-1]
                    if (bancoAtual == bancoDaCamada) and (camadaModelo.name() in camadaCrua.name()):
                        camadaCrua.loadDefaultStyle()
                        nomeEstilo = self.obterDadosSelecaoUsuario()[0]+'_'+camadaModelo.name()
                        if nomeEstilo in estilosBanco:
                            estiloXml = camadaCrua.getStyleFromDatabase(str(estilosBanco[nomeEstilo]), "Erro")
                            camadaCrua.applyNamedStyle(estiloXml)
                        self.gerarMapaDeValores(camadaModelo, camadaCrua)
            self.obterIface().mapCanvas().refreshAllLayers()
        self.obterControlador().rodarComando('fechar gif')
        self.obterControlador().rodarComando('fechar carrega estilos interface')

    def gerarMapaDeValores(self, lyrModelo, lyrDestino):
        camposIndex = lyrModelo.attributeList()
        for index in camposIndex:
            if lyrModelo.editorWidgetV2(index) in [u'ValueMap']: 
                lyrDestino.setEditorWidgetV2( index, lyrModelo.editorWidgetV2(index) )
                lyrDestino.setEditorWidgetV2Config( index, lyrModelo.valueMap(index) )
        if lyrDestino.geometryType() == 1:
            lyrDestino.addExpressionField('$length',
                core.QgsField(u'Comprimento', QtCore.QVariant.Double))
        elif lyrDestino.geometryType() == 2:
            lyrDestino.addExpressionField('$area',
                core.QgsField(u'Área', QtCore.QVariant.Double))

