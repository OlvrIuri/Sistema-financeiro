"""
conexao.py
==========
Módulo de conexão com o banco de dados MySQL.

Responsabilidade única (princípio de coesão): centralizar a configuração
de acesso ao banco. Se o servidor, a porta ou a senha mudarem, alteramos
APENAS este arquivo — nenhuma outra parte do sistema precisa ser tocada.

Apresentação: este módulo faz parte da PARTE 3 (Camada de Dados).
"""

import mysql.connector


def obter_conexao():
    """
    Abre e retorna uma nova conexão com o banco 'sistema_financeiro'.

    Retorno:
        mysql.connector.connection.MySQLConnection: objeto de conexão ativo.

    Observações:
        - host/porta configurados para o ambiente local (USBWebserver usa
          a porta 3307 por padrão).
        - Cada operação do sistema abre a conexão, executa a consulta e a
          fecha em seguida (padrão abre-usa-fecha), evitando conexões
          "penduradas" no servidor.
    """
    return mysql.connector.connect(
        host="localhost",          # servidor local
        user="root",               # usuário do MySQL
        password="usbw",           # senha padrão do USBWebserver
        port=3307,                 # porta do MySQL no USBWebserver
        database="sistema_financeiro"  # banco criado pelo script.sql
    )
