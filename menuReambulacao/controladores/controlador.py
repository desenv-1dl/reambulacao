#! -*- coding: UTF-8 -*-
from PyQt4.QtCore import QObject

class Controlador(QObject):
    def __init__(self, bancoDeDados, botaoPrincipal, definirBancoDeDadosInterface, menuModelo):
        QObject.__init__(self)
        self.botaoPrincipal = botaoPrincipal
        self.botaoPrincipal.registrarControlador(self)
        self.definirBancoDeDadosInterface = definirBancoDeDadosInterface
        self.definirBancoDeDadosInterface.registrarControlador(self)
        self.bancoDeDados = bancoDeDados
        self.bancoDeDados.registrarControlador(self)
        self.menuModelo = menuModelo
        self.menuModelo.registrarControlador(self)
        self.inicializarComandos()

    def inicializarComandos(self):
        self.comandos = {
        'inicializar botao principal' : self.botaoPrincipal.mostrarBotao,
        'inicializar selecao de banco de dados' : self.definirBancoDeDadosInterface.mostrarFrame,
        'iniciar gif' : self.definirBancoDeDadosInterface.iniciarGif,
        'terminar gif' : self.definirBancoDeDadosInterface.terminarGif,
        'fechar definir banco de dados interface' : self.definirBancoDeDadosInterface.close,
        'conectar em postgresql'      : self.bancoDeDados.definirConexaoPostgres,
        'obter lista de conexoes'     : self.bancoDeDados.obterListaDeConexoes,
        'obter lista de schemas'      : self.bancoDeDados.obterListaDeSchemas,
        'obter dados de conexao'      : self.bancoDeDados.obterDadosDeConexao,
        'obter cursor postgres'       : self.bancoDeDados.obterConexaoPostgres,
        'ativar menu'                 : self.menuModelo.ativarMenu,
                        }

    def rodarComando(self, cmd, params=None):
        if params:
            r = self.comandos[cmd](params)
        else:
            r = self.comandos[cmd]()
        return (r if r else '')

