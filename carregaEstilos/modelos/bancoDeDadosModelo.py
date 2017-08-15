#! -*- coding: utf-8 -*-                                    
from PyQt4 import QtCore, QtGui
import psycopg2

class BancoDeDadosModelo:
    def __init__(self):
        self.inicializarVariaveis()
        self.definirSettings()

    def inicializarVariaveis(self):
        self.settings = None
        self.conexao  = None
        self.dados = None
        self.estilosId = None

    def definirSettings(self):
        self.settings = QtCore.QSettings()
        self.settings.beginGroup("PostgreSQL/connections")

    def obterSettings(self):
        return self.settings

    def obterListaDeBancos(self):
        dbs = []
        for data in self.obterSettings().allKeys():
            if data[-9:] == "/username":
                dbs.append(data[:-9])
        return tuple(dbs)

    def obterListaDeTiposDeEstilos(self):
        try:
            self.obterConexaoPostgres().execute('''select stylename, id from layer_styles;''')
        except:
            return
        else:
            consultaEstilos = self.obterConexaoPostgres().fetchall()
            estilos = tuple(set([ x[0].split('_')[0] for x in consultaEstilos]))
            estilosId = { x[0] : x[1] for x in consultaEstilos}
            self.definirEstilosId(estilosId)
            return estilos

    def definirEstilosId(self, ei):
        self.estilosId = ei

    def obterEstilosId(self):
        return self.estilosId

    def obterListaDeCartas(self):
        self.obterConexaoPostgres().execute('''
                                            SELECT
                                            nspname
                                            FROM
                                            pg_catalog.pg_namespace
                                            WHERE nspname LIKE '%' || 'view' || '%';
                                            ''')
        cartas = tuple([ x[0] for x in self.obterConexaoPostgres().fetchall()])
        return cartas

    def definirConexaoPostgres(self, param):
        self.obterConexaoPostgres().close() if self.obterConexaoPostgres() else ''
        db = param[0]
        host = self.obterSettings().value(db+"/host")
        port = self.obterSettings().value(db+"/port")
        database = self.obterSettings().value(db+"/database")
        username = self.obterSettings().value(db+'/username')
        password = self.obterSettings().value(db+'/password')
        conn_string = "host="+host+" dbname="+database+" user="+username+" password="+password+" port="+port
        conn = psycopg2.connect(conn_string)
        self.conexao = conn.cursor()
        self.definirDadosDeConexao((database, host, port, username, password))

    def obterConexaoPostgres(self):
        return self.conexao

    def definirDadosDeConexao(self, dados):
        self.dados = dados

    def obterDadosDeConexao(self):
        return self.dados


