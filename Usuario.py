"""
Usuario.py
==========
Classe Usuario — responsável pelo CADASTRO e pela AUTENTICAÇÃO (login).

Conceitos de POO demonstrados neste arquivo:
    * Classe e objeto ............ Usuario é o "molde"; cada pessoa que se
                                    cadastra vira um objeto (instância).
    * Encapsulamento ............. o atributo _senha é protegido (prefixo _),
                                    indicando que não deve ser acessado
                                    diretamente de fora da classe.
    * Property ................... a senha é exposta apenas para leitura
                                    através de @property, sem setter.
    * Abstração .................. quem usa a classe chama cadastrar() e
                                    login() sem precisar conhecer o SQL
                                    executado internamente.

Apresentação: este arquivo faz parte da PARTE 2 (Classe Usuario).
"""

from conexao import obter_conexao


class Usuario:
    """
    Representa uma pessoa que utiliza o sistema (Cliente ou Gerente).

    Atributos:
        id (int | None): chave primária no banco; None até o login/cadastro.
        nome (str): nome completo do usuário.
        email (str): identificador único de login (regra de negócio: UNIQUE).
        _senha (str): atributo PROTEGIDO — encapsulamento.
        perfil_id (int): 1 = Gerente (administrador), 2 = Cliente (padrão).
    """

    def __init__(self):
        """Construtor: inicializa um usuário 'vazio', ainda não autenticado."""
        self.id = None
        self.nome = ''
        self.email = ''
        self._senha = ''          # protegido: convenção do underscore
        self.perfil_id = 2        # todo novo cadastro nasce como Cliente

    @property
    def senha(self):
        """
        Property somente leitura da senha.

        Demonstra ENCAPSULAMENTO: o atributo interno _senha pode ser lido
        via usuario.senha, mas não existe setter — ninguém consegue fazer
        usuario.senha = 'x' de fora da classe.
        """
        return self._senha

    def cadastrar(self):
        """
        Tela de Cadastro: coleta os dados, valida a senha e grava no banco.

        Regras de negócio aplicadas:
            1. A senha e a confirmação devem coincidir (laço até acertar).
            2. A senha não pode ser vazia.
            3. O e-mail é normalizado para minúsculas (login não diferencia
               maiúsculas/minúsculas).
            4. Ao concluir, uma CONTA CORRENTE com saldo 0,00 é criada
               automaticamente e vinculada ao usuário (relação 1 : 1).

        Tratamento de erros:
            O bloco try/except captura falhas do banco (ex.: e-mail já
            cadastrado, pois a coluna é UNIQUE) e exibe uma mensagem
            amigável em vez de derrubar o programa.
        """
        print("\n=== TELA DE CADASTRO ===")
        self.nome = input("Nome: ").strip()
        self.email = input("E-mail: ").strip().lower()

        # Laço de validação: só sai quando senha == confirmação e não vazia
        while True:
            self._senha = input("Senha: ").strip()
            confirma = input("Confirme a senha: ").strip()
            if self._senha != "" and self._senha == confirma:
                break
            print("[ERRO] As senhas não coincidem ou estão vazias. Tente novamente.\n")

        conn = obter_conexao()
        cursor = conn.cursor()
        try:
            # 1º INSERT: grava o usuário na tabela 'usuarios'
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, perfil_id) VALUES (%s, %s, %s, %s)",
                (self.nome, self.email, self._senha, self.perfil_id)
            )
            usuario_id = cursor.lastrowid  # recupera o id gerado (AUTO_INCREMENT)

            # 2º INSERT: cria a conta corrente (tipo_conta_id = 1) vinculada
            # ao usuário recém-criado, com saldo inicial ZERO — regra 1 : 1.
            cursor.execute(
                "INSERT INTO contas (usuario_id, tipo_conta_id, saldo) VALUES (%s, %s, %s)",
                (usuario_id, 1, 0.00)
            )
            conn.commit()  # efetiva as duas gravações juntas
            print(f"\n[OK] Cadastro de {self.nome} ({self.email}) concluído com sucesso.")
        except Exception as e:
            # Ex.: e-mail duplicado (violação de UNIQUE) cai aqui
            print(f"\n[ERRO] Falha ao cadastrar no banco de dados: {e}")
        finally:
            # finally garante que a conexão SEMPRE é fechada,
            # tenha dado certo ou errado.
            cursor.close()
            conn.close()

    def login(self, email, senha):
        """
        Tela de Login: verifica as credenciais no banco de dados.

        Parâmetros:
            email (str): e-mail digitado pelo usuário.
            senha (str): senha digitada pelo usuário.

        Retorno:
            bool: True se autenticou; False caso contrário.

        Funcionamento:
            - Consulta parametrizada (%s) — evita SQL Injection, pois o
              conector trata os valores como dados, nunca como comando.
            - Se encontrou registro, o objeto é "hidratado": os dados do
              banco preenchem os atributos da instância (self.id,
              self.nome, self.perfil_id...), e o main.py usa o perfil_id
            para decidir se abre o menu de Cliente ou o painel do Gerente.
        """
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)  # retorna linhas como dicionário
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s AND senha = %s",
            (email, senha)
        )
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if user_data:
            # Preenche o objeto com os dados vindos do banco
            self.id = user_data['id']
            self.nome = user_data['nome']
            self.email = user_data['email']
            self._senha = user_data['senha']
            self.perfil_id = user_data['perfil_id']
            print("\n[OK] LOGIN REALIZADO COM SUCESSO!")
            print(f"Bem-vindo(a) de volta, {self.nome}!\n")
            return True

        print("\n[ERRO] E-mail ou senha incorretos. Não foi possível realizar o login.\n")
        return False
