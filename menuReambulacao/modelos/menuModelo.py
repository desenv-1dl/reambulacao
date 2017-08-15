# -*- coding: utf-8 -*-
from PyQt4.QtGui import QAction, QDialog, QFileDialog, QMessageBox, QIcon, QFrame
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsDataSourceURI, QgsPoint, QGis, QgsGeometry, QgsProject
from PyQt4 import uic
import psycopg2, sys, os, csv, resources, qgis.utils, time
from PyQt4.QtCore import QSettings
from PyQt4.QtCore import QT_TR_NOOP as tr
from PyQt4 import QtCore, QtGui
from qgis.gui import QgsAttributeDialog
import os
from carregarCacheMenu import CarregarCacheMenu

class MenuModelo(QtCore.QObject):
    def __init__(self, iface, menuInterface):
        QtCore.QObject.__init__(self)
        self.inicializarVariaveis()
        self.menuInterface = menuInterface
        self.iface = iface
        self.iface.actionAddFeature().toggled.connect(self.desconnectLayer)
        self.iface.layerTreeView().clicked.connect(self.desconnectLayer)
        self.iface.legendInterface().itemAdded.connect(self.desconnectLayer)
        self.iface.actionToggleEditing().triggered.connect(self.desconnectLayer)

    def inicializarVariaveis(self):
        self.iface = None
        self.controlador = None
        self.menuInterface = None
        self.data = None
        self.estilosId =  None

    def desconnectLayer(self):
        try:
            self.iface.activeLayer().setFeatureFormSuppress(False)
        except:
            pass
        try:
            self.iface.activeLayer().featureAdded.disconnect(self.createFeature)
        except:
            pass
        try:
            self.iface.activeLayer().featureAdded.disconnect(self.cutPasteFeature)
        except:
            pass

    def registrarControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def ativarMenu(self, dadosSelecaoUsuario):
        cursorPostgres = self.obterControlador().rodarComando('obter cursor postgres')
        dadosDeConexao = self.obterControlador().rodarComando('obter dados de conexao')
        dados  = dadosDeConexao + dadosSelecaoUsuario
        self.bancoEmUso = dados[0]
        self.obterControlador().rodarComando('iniciar gif')
        self.carregarCacheMenu(dados, cursorPostgres)

    def carregarCacheMenu(self, dados, cursorPostgres):
        thread = QtCore.QThread(self)
        cache = CarregarCacheMenu(dados, cursorPostgres)
        cache.moveToThread(thread)
        cache.finished.connect(self.abrirMenu)
        thread.started.connect(cache.run)
        self.thread = thread
        self.worker = cache
        thread.start()
        #cache.run()

    def setData(self,d):
        self.data = d

    def getData(self):
        return self.data

    def abrirMenu(self, feicoes, dadosBotoes, dados):
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.obterControlador().rodarComando('terminar gif')
        self.obterControlador().rodarComando('fechar definir banco de dados interface')
        self.leituradb = dadosBotoes
        self.feicoesCache = feicoes
        self.setData(dados)
        self.menu = self.menuInterface(self.iface, dadosBotoes, dados)
        self.menu.botaoSelecionarCsv.clicked.connect(self.selecioneCsv)
        self.menu.closeEvent = self.outMenu
        self.menu.c.addItem(u'<Opções>')
        self.menu.c.addItems(self.carregarEstilos())
        self.menu.showDialog()

    def carregarEstilos(self):
        try:
            cursor = self.obterControlador().rodarComando('obter cursor postgres')
            cursor.execute('''
                                                select
                                                stylename, id
                                                from layer_styles;
                                                ''')
        except:
            return
        else:
            consultaEstilos = cursor.fetchall()
            estilos = tuple(set([ x[0].split('_')[0] for x in consultaEstilos]))
            estilosId = { x[0] : x[1] for x in consultaEstilos}
            self.definirEstilosId(estilosId)
            return estilos


    def definirEstilosId(self, ei):
        self.estilosId = ei

    def obterEstilosId(self):
        return self.estilosId

    def definirAcao(self):
        botao = self.menu.obterNomeBotao()
        camada= self.atributagem.get(botao).keys()[0]
        grupo = self.leituradb[camada]
        valores = self.checkSelections()
        l = self.procurarFeicao(camada, grupo)
        if not(l):
            l = self.loadLayer(camada, grupo)
        if valores[0] and (valores[1] == l.geometryType()) and (self.menu.getStatusMode() != 0):
            self.cortaCola(camada, botao, valores[0], valores[2], l)
        else:
           self.addCamada(camada, botao)

    def checkSelections(self):
        if self.iface.mapCanvas().currentLayer():
            lyr = self.iface.mapCanvas().currentLayer()
            if (lyr.selectedFeatureCount() > 0):
                tipoDeGeometria = lyr.geometryType()
                selecoes = lyr.selectedFeaturesIds()
                self.removeSelecoes()
                return (selecoes, tipoDeGeometria, lyr,)
        return (False,)

    def procurarFeicao(self, camada, grupo):
        resultado1 = QgsMapLayerRegistry.instance().mapLayersByName(camada)
        resultado2 = QgsMapLayerRegistry.instance().mapLayersByName(grupo+'_'+camada)
        for layer in resultado1+resultado2:
            if self.bancoEmUso == layer.source().split(' ')[0][8:-1]:
                self.iface.setActiveLayer(layer)
                return layer

    def loadLayer(self, camada, grupo):
        uri = u'dbname=\'%s\' host=%s port=%s user=\'%s\' password=\'%s\' key=\'id\' table="%s"."%s" (geom) sql=' % ( self.getData()[0],
            self.getData()[1], self.getData()[2], self.getData()[3], self.getData()[4], self.getData()[6], grupo+'_'+camada )
        layer = QgsVectorLayer(uri, camada, "postgres")
        l = QgsMapLayerRegistry.instance().addMapLayer(layer)
        self.carregarEstilo(camada, l)
        self.gerarMapaDeValores(camada, grupo, l)
        return l

    def carregarEstilo(self, camada, layer):
        layer.loadDefaultStyle()
        nomeEstilo = self.menu.c.currentText()+'_'+camada
        if nomeEstilo in self.obterEstilosId():
            estiloXml = layer.getStyleFromDatabase(str(self.obterEstilosId()[nomeEstilo]), "Erro")
            layer.applyNamedStyle(estiloXml)

    def gerarMapaDeValores(self, camada, grupo, layer):
        for c in self.feicoesCache[camada.split('_')[-1]][grupo]:
            if c.keys()[0] == camada:
                for fieldIndex in sorted(c[camada]):
                   if c[camada][fieldIndex][0] in [u'ValueMap']: 
                       layer.setEditorWidgetV2( fieldIndex, c[camada][fieldIndex][0] )
                       layer.setEditorWidgetV2Config( fieldIndex, c[camada][fieldIndex][1] )

    def disconnectLayerForm(self, b):
        try:
            self.iface.activeLayer().setFeatureFormSuppress(b)
        except:
            pass

    def disconnectLayerAdd(self, b):
        try:
            if b:
                self.iface.activeLayer().featureAdded.connect(self.createFeature)
            else:
                self.iface.activeLayer().featureAdded.disconnect(self.createFeature)
        except:
            pass

    def cortaCola(self, camada, botao, selectionsId, camadaOrigem, camadaDestino):
        self.disconnectLayerForm(False)
        self.disconnectLayerAdd(False)
        self.iface.activeLayer().startEditing()
        self.iface.actionAddFeature().trigger()
        self.setButton(botao)
        self.disconnectLayerForm(True)
        self.iface.activeLayer().featureAdded.connect(self.cutPasteFeature)
        self.iface.setActiveLayer(camadaOrigem)
        for i in selectionsId:
            self.iface.activeLayer().select(i)
        self.iface.actionCutFeatures().trigger()
        self.iface.setActiveLayer(camadaDestino)
        self.iface.actionPasteFeatures().trigger()
        self.iface.activeLayer().featureAdded.disconnect(self.cutPasteFeature)
        self.iface.activeLayer().removeSelection()
        self.addCamada(camada, botao)

    def cutPasteFeature(self, Id):
        lyr = self.iface.mapCanvas().currentLayer()
        formValue = self.botaoConfig[self.getButton()][1]
        if (lyr) and (Id < 0):
            lyr.select(Id)
            f = lyr.selectedFeatures()[0]
            lyr.deselect(Id)
            self.autoAttribute(lyr, f)


    def setButton(self, b):
        self.botao1 = b

    def getButton(self):
        return self.botao1

    def addCamada(self, camada, botao):
        self.disconnectLayerForm(False)
        self.disconnectLayerAdd(False)
        self.iface.activeLayer().startEditing()
        self.iface.actionAddFeature().trigger()
        self.setButton(botao)
        self.disconnectLayerForm(True)
        self.disconnectLayerAdd(True)

    def createFeature(self, Id):
        lyr = self.iface.mapCanvas().currentLayer()
        formValue = self.botaoConfig[self.getButton()][1]
        if (lyr) and (Id < 0) and (formValue != u"sim"):
            lyr.select(Id)
            f = lyr.selectedFeatures()[0]
            lyr.deselect(Id)
            provider = lyr.dataProvider()
            fields = lyr.pendingFields()
            try:
                attr = f.initAttributes(len(fields))
                for i in range(len(fields)):
                    f.setAttribute(i,  provider.defaultValue(i))
            except AttributeError:
                for i in fields:
                    f.addAttribute(i,  provider.defaultValue(i))
            attrDialog = QgsAttributeDialog(lyr, f, False)
            self.attributeForm(attrDialog, lyr)
            result = attrDialog.exec_()
            if not result:
                lyr.deleteFeature(Id)
                self.iface.mapCanvas().refresh()
        elif (lyr) and (Id < 0) and (formValue == u"sim"):
            lyr.select(Id)
            f = lyr.selectedFeatures()[0]
            lyr.deselect(Id)
            self.autoAttribute(lyr, f)


    def autoAttribute(self, lyr, f):
        flds = lyr.attributeList()
        for i in flds:
            valueMap = lyr.valueMap(i)
            if (lyr.editorWidgetV2(i) == u'ValueMap') and (u'A SER PREENCHIDO' in valueMap):
                lyr.changeAttributeValue(f.id(), i , valueMap[u'A SER PREENCHIDO'])
            elif (lyr.editorWidgetV2(i) == u'formawarevaluerelationwidget'):
                lyr.changeAttributeValue(f.id(), i , 999)
        data = self.atributagem[self.getButton()][lyr.name()]
        for i in data:
            indx = lyr.fieldNameIndex(unicode(i))
            valueMap = lyr.valueMap(indx)
            if lyr.editorWidgetV2(indx) == u'TextEdit':
                lyr.changeAttributeValue(f.id(), indx , data[i][0] )
            elif (lyr.editorWidgetV2(indx) == u'ValueMap') and ( data[i][0] in valueMap):
                lyr.changeAttributeValue(f.id(), indx , valueMap[data[i][0]])

    def attributeForm(self, attrDialog, lyr):
        flds = lyr.attributeList()
        for i in flds:
            valueMap = lyr.valueMap(i)
            if (lyr.editorWidgetV2(i) == u'ValueMap') and (u'A SER PREENCHIDO' in valueMap):
                attrDialog.attributeForm().changeAttribute( lyr.fields().field(i).name() , valueMap[u'A SER PREENCHIDO'])
            elif (lyr.editorWidgetV2(i) == u'formawarevaluerelationwidget'):
                attrDialog.attributeForm().changeAttribute( lyr.fields().field(i).name() , 999)
        data = self.atributagem[self.getButton()][lyr.name()]
        for i in data:
            indx = lyr.fieldNameIndex(unicode(i))
            valueMap = lyr.valueMap(indx)
            if lyr.editorWidgetV2(indx) == u'TextEdit':
                attrDialog.attributeForm().changeAttribute( i , data[i][0] )
            elif (lyr.editorWidgetV2(indx) == u'ValueMap') and ( data[i][0] in valueMap):
                attrDialog.attributeForm().changeAttribute( i , valueMap[data[i][0]])

    def removeSelecoes(self):
        for i in range(len(self.iface.mapCanvas().layers())):
            try:
                self.iface.mapCanvas().layers()[i].removeSelection()
            except:
                pass

    def outMenu(self, c):
        if self.iface.activeLayer():
            self.iface.activeLayer().startEditing()
        try:
            self.iface.activeLayer().setFeatureFormSuppress(False)
        except:
            pass
        try:
            self.iface.activeLayer().featureAdded.disconnect(self.createFeature)
        except:
            pass
        try:
            self.iface.activeLayer().featureAdded.disconnect(self.cutPasteFeature)
        except:
            pass
        self.menu.cleanCursor()

    def selecioneCsv(self):
        fileN = QFileDialog(self.iface.mainWindow()).getOpenFileName()
        if fileN[-4:] == ".csv":
            self.lerCsv(fileN)
            self.menu.botaoSelecionarCsv.close()
        elif (fileN[-4:] != ".csv") and (fileN[-4:] != "") :
            QMessageBox.warning(self.iface.mainWindow(), u"ERRO:", u"<font color=red>Arquivo não compatível:<br></font><font color=blue>Selecione um Arquivo com extensão '.csv'!</font>", QMessageBox.Close)

    def lerCsv(self, file1):
        self.relatorioDeErros=[]
        self.conjBot=[]
        self.atributagem={}
        self.botaoConfig = {}
        linhaCsv=2
        conjuntoBotaoFeicao=[]
        conjuntoCategorias=[]
        fileC=open(file1, 'rb')
        for linha in fileC:
            if not linha.startswith("CATEGORIA"):
                linha=linha.replace("\n","").split(",")
                nomeBot=unicode(linha[1], "utf-8")
                nomeCamada=unicode(linha[2].replace(" ",""), "utf-8")
                atalho=unicode(linha[3], "utf-8")
                form=unicode(linha[4], "utf-8")
                self.botaoConfig[nomeBot] = [atalho, form]
                self.atributagem[nomeBot]={}
                self.atributagem[nomeBot][nomeCamada]={}
                index=5            
                for i in range(len(linha)-5):
                    if len(linha[index].split(":")) > 1:
                        campo=unicode(linha[index].split(":")[0], "utf-8")
                        valor1=unicode(linha[index].split(":")[1].replace("\r","").replace("\n",""), "utf-8")                        
                        if len(linha[index].split(":")) == 3:
                            valor2=unicode(linha[index].split(":")[2], "utf-8")                    
                            self.atributagem[nomeBot][nomeCamada][campo]=[valor1, valor2]
                            index+=1
                        elif len(linha[index].split(":")) == 2:
                            self.atributagem[nomeBot][nomeCamada][campo]=[valor1]
                            index+=1
                if (self.leituradb.get(nomeCamada)) and (not self.leituradb.get(nomeCamada) in conjuntoCategorias):      
                    conjuntoCategorias.append(self.leituradb.get(nomeCamada))
                if (self.leituradb.get(nomeCamada)):
                    conjuntoBotaoFeicao.append([nomeBot, nomeCamada, campo, valor1])            
                linhaCsv+=1
        self.menu.criarTab(conjuntoCategorias)        
        for botaofeicao in conjuntoBotaoFeicao:    
            bot = self.menu.criarBotao(botaofeicao[0], botaofeicao[1], self.botaoConfig[botaofeicao[0]][0])
            bot.clicked.connect(self.definirAcao)
        self.menu.registerShortcuts()    

