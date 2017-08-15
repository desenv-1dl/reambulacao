# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsDataSourceURI, QgsPoint, QGis, QgsGeometry, QgsProject


class LoadCacheLayersModelo(QtCore.QObject):
    finished = QtCore.pyqtSignal(tuple, tuple)
    def __init__(self, data, conn):
        QtCore.QObject.__init__(self)
        self.initVariables()
        self.setData(data)
        self.setConnection(conn)

    def initVariables(self):
        self.data = None
        self.conn = None

    def setData(self, d):
        self.data = d

    def getData(self):
        return self.data

    def setConnection(self, c):
        self.conn = c

    def getConnection(self):
        return self.conn

    def getCachelayers(self):
        return self.cacheLayers

    def run(self):
        cacheLayers = []
        self.getConnection().execute('''SELECT
                                        tablename
                                        FROM
                                        pg_tables
                                        WHERE schemaname ~ 'edgv'
                                        ORDER BY tablename;
                                      ''')
        layers = tuple([x[0]for x in self.getConnection().fetchall()])
        for name in layers:
            layerReady = self.loadLayer(name)
            cacheLayers.append( layerReady ) if layerReady else ''
        self.finished.emit(tuple(cacheLayers) , self.getData())

    def loadLayer(self, view):
        uri = u'dbname=\'%s\' host=%s port=%s user=\'%s\' password=\'%s\' key=\'id\' table="%s"."%s" (geom) sql=' % ( self.getData()[0],
        self.getData()[1], self.getData()[2], self.getData()[3],
        self.getData()[4], self.getData()[5], view )
        layer = QgsVectorLayer(uri, view[len(view.split('_')[0])+1:], "postgres")
        self.createValueMap(layer, view)
        return layer


    def createValueMap(self, layer, view):
        attrName = self.getFieldsNames(layer)
        domains = self.getDomainsFields( view )
        for n in attrName:
            fieldIndex = layer.fieldNameIndex( n )
            if n in domains:
                layer.setEditorWidgetV2( fieldIndex, 'ValueMap' )
                values =  self.getValueMapNewDb(domains[n])
                layer.setEditorWidgetV2Config( fieldIndex, values )

    def getFieldsNames(self, layer):
        conf = layer.fields()
        fieldIndex = conf.allAttributesList()
        nameField = []
        for i in fieldIndex:
            nameField.append(conf.field(i).name())
        return nameField

    def getDomainsFields(self, name):
        self.getConnection().execute('''
                        SELECT pg_get_constraintdef(c.oid) AS cdef 
                        FROM pg_constraint c 
                        JOIN pg_namespace n 
                        ON n.oid = c.connamespace 
                        WHERE contype IN ('f') 
                        AND n.nspname = 'edgv' 
                        AND conrelid::regclass::text IN ('edgv.%s');
                        ''' % (name))
        data = { stg[0].split('(')[1].split(')')[0].replace(' ','') : stg[0].split('(')[1].split('.')[1] for stg in self.getConnection().fetchall()}
        return data

    def getValueMapNewDb(self, n):
        self.getConnection().execute("select * from dominios.%s;" % (n) )
        data = dict(self.getConnection().fetchall())
        inv_data = {v: k for k, v in data.iteritems()}
        return inv_data
