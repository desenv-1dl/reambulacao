#! -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsDataSourceURI, QgsPoint, QGis, QgsGeometry, QgsProject, QgsField
import psycopg2
from loadCacheLayers import LoadCacheLayers

class DataBase(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.initVariables()
        self.setSettings()

    def initVariables(self):
        self.settings = None
        self.connection = None
        self.dataConnection = None
        self.estilosId = None
        self.estilo = None

    def setSettings(self):
        self.settings = QSettings()
        self.settings.beginGroup("PostgreSQL/connections")

    def getSettings(self):
        return self.settings

    def setDataConnection(self, dataConn):
       self.dataConnection = dataConn

    def getDataConnection(self):
        return self.dataConnection

    def setConnectionPostgres(self, param):
        self.getConnectionPostgres().close() if self.getConnectionPostgres() else ''
        db = param[0]
        host = self.getSettings().value(db+"/host")
        port = self.getSettings().value(db+"/port")
        database = self.getSettings().value(db+"/database")
        username = self.getSettings().value(db+'/username')
        password = self.getSettings().value(db+'/password')
        conn_string = "host="+host+" dbname="+database+" user="+username+" password="+password+" port="+port
        conn = psycopg2.connect(conn_string)
        self.connection = conn.cursor()
        self.setDataConnection((database, host, port, username,
                                password))

    def getConnectionPostgres(self):
        return self.connection

    def getMIList(self):
        self.getConnectionPostgres().execute('''
                                            SELECT
                                            nspname
                                            FROM
                                            pg_catalog.pg_namespace
                                            WHERE nspname LIKE '%' || 'view' || '%';
                                             ''')
        return tuple([x[0]for x in self.getConnectionPostgres().fetchall()])

    def getDataBasesList(self):
        dbs = []
        for data in self.getSettings().allKeys():
            if data[-9:] == "/username":
                dbs.append(data[:-9])
        return tuple(dbs)

    def loadLayers(self, params):
        self.definirEstilo(params[-1])
        data = self.getDataConnection() + params[1:-1]
        conn = self.getConnectionPostgres()
        self.startJob(data, conn)

    def definirEstilo(self, e):
        self.estilo = e

    def obterEstilo(self):
        return self.estilo

    def carregarEstilos(self):
        try:
            self.getConnectionPostgres().execute('''
                                                select
                                                stylename, id
                                                from layer_styles ;
                                                ''')
        except:
            return
        else:
            consultaEstilos = self.getConnectionPostgres().fetchall()
            estilos = tuple(set([ x[0].split('_')[0] for x in consultaEstilos]))
            estilosId = { x[0] : x[1] for x in consultaEstilos}
            self.definirEstilosId(estilosId)
            return estilos

    def definirEstilosId(self, ei):
        self.estilosId = ei

    def obterEstilosId(self):
        return self.estilosId

    def finishedJob(self, l, data):
        self.worker.deleteLater()
        self.thread.quit()
        self.thread.wait()
        self.thread.deleteLater()
        self.createGroupsAndAddLayersAndDomains(l, data)
        self.getController().runCommand('open gif', 'False')

    def startJob(self, data, conn):
        thread = QtCore.QThread(self.iface.mainWindow())
        worker =  LoadCacheLayers(data, conn)
        worker.moveToThread(thread)
        worker.finished.connect(self.finishedJob)
        #worker.run()
        thread.started.connect(worker.run)
        self.getController().runCommand('open gif', 'True')
        thread.start()
        self.thread = thread
        self.worker = worker

    def createGroupsAndAddLayersAndDomains(self, l, data):
        root = QgsProject.instance().layerTreeRoot()
        project = data[-2][len(data[-2].split('_')[0])+1:]
        if not project:
            project = data[0]
        parentA = root.addGroup(project)
        for g1, g2 in [('PONTO', 'p'), ('LINHA', 'l'), ('AREA', 'a')]:
            parentB = parentA.addGroup(g1)
            for group in sorted(l[g2]):
                parentC = parentB.addGroup(group)
                for lyr in sorted(l[g2][group]):
                    layer = QgsVectorLayer( lyr.styleURI(), lyr.name(), "postgres")
                    vl = QgsMapLayerRegistry.instance().addMapLayer(layer, False)
                    if vl:
                        vl.loadDefaultStyle()
                        nomeEstilo = self.obterEstilo()+'_'+lyr.name()
                        if (nomeEstilo in self.obterEstilosId()):
                            estiloXml = vl.getStyleFromDatabase(str(self.obterEstilosId()[nomeEstilo]), "Erro")
                            vl.applyNamedStyle(estiloXml)
                        self.createMapValue(lyr, vl)
                        parentC.addLayer(vl)
        self.getController().runCommand('close loadLayersInterface')

    def createMapValue(self, lyrModelo, lyrDestino):
        camposIndex = lyrModelo.attributeList()
        for index in camposIndex:
            if lyrModelo.editorWidgetV2(index) in [u'ValueMap']:
                lyrDestino.setEditorWidgetV2( index, lyrModelo.editorWidgetV2(index) )
                lyrDestino.setEditorWidgetV2Config( index, lyrModelo.valueMap(index) )
        if lyrDestino.geometryType() == 1:
            lyrDestino.addExpressionField('$length', 
                                            QgsField(u'Comprimento', QtCore.QVariant.Double))
        elif lyrDestino.geometryType() == 2:
            lyrDestino.addExpressionField('$area',
                                            QgsField(u'Área', QtCore.QVariant.Double))






