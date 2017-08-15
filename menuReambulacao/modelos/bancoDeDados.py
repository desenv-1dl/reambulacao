# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings
from qgis.core import QgsMapLayerRegistry, QgsVectorLayer, QgsDataSourceURI, QgsPoint, QGis, QgsGeometry, QgsProject
import psycopg2


class BancoDeDados(QtCore.QObject):
    def __init__(self, iface):
        QtCore.QObject.__init__(self)
        self.iface = iface
        self.inicializarVariaveis()
        self.definirConfiguracoes()

    def inicializarVariaveis(self):
        self.configuracoes = None
        self.postgres = None
        self.controlador = None
        self.dadosDeConexao = None

    def registrarControlador(self, c):
        self.controlador = c

    def obterControlador(self):
        return self.controlador

    def definirConfiguracoes(self):
        self.configuracoes = QSettings()
        self.configuracoes.beginGroup("PostgreSQL/connections")

    def obterConfiguracoes(self):
        return self.configuracoes

    def definirDadosDeConexao(self, d):
        self.dadosDeConexao = d

    def obterDadosDeConexao(self):
        return self.dadosDeConexao

    def obterConexaoPostgres(self):
        return self.postgres

    def definirConexaoPostgres(self, dados):
        nomeBanco = dados[0]
        self.obterConexaoPostgres().close() if self.obterConexaoPostgres() else ''
        host = self.obterConfiguracoes().value(nomeBanco+"/host")
        port = self.obterConfiguracoes().value(nomeBanco+"/port")
        database = self.obterConfiguracoes().value(nomeBanco+"/database")
        username = self.obterConfiguracoes().value(nomeBanco+'/username')
        password = self.obterConfiguracoes().value(nomeBanco+'/password')
        conn_string = "host="+host+" dbname="+database+" user="+username+" password="+password+" port="+port
        conn = psycopg2.connect(conn_string)
        self.postgres = conn.cursor()
        self.definirDadosDeConexao((database, host, port, username,
            password))

    def obterListaDeConexoes(self):
        conexoes=[]
        for x in self.obterConfiguracoes().allKeys():
            if  x[-9:] == "/username":
                conexoes.append(x[:-9])
        return tuple(conexoes)

    def obterListaDeSchemas(self):
        self.obterConexaoPostgres().execute('''
                                            SELECT
                                            nspname
                                            FROM
                                            pg_catalog.pg_namespace
                                            WHERE (nspname LIKE '%' || 'view' || '%') or (nspname = 'edgv');
                                            ''')
        return tuple([x[0]for x in self.obterConexaoPostgres().fetchall()])



