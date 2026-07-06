"""
ContaBancaria.py
================
Classe ContaBancaria — responsável por TODAS as operações financeiras:
saldo, depósito, saque e extrato.

Conceitos de POO demonstrados neste arquivo:
    * Encapsulamento ......... _id_conta é protegido; o saldo NÃO fica em
                                memória — é sempre lido do banco através de
                                uma @property somente leitura. Ninguém
                                consegue fazer conta.saldo = 1000000.
    * Property ............... 'saldo' parece um atributo, mas por baixo
                                executa um SELECT (getter calculado).
    * Composição/associação .. cada ContaBancaria nasce ligada a um
                                usuario_id (relação Usuario 1 : 1 Conta).
    * Abstração .............. o main.py só chama mostrar_saldo(),
                                realizar_transacao() e mostrar_extrato();
                                todo o SQL fica escondido aqui dentro.

Apresentação: este arquivo faz parte da PARTE 4 (Classe ContaBancaria).
"""

from conexao import obter_conexao


class ContaBancaria:
    """
    Representa a conta bancária digital de um usuário.

    Atributos:
        usuario_id (int): id do dono da conta (chave estrangeira lógica).
        _id_conta (int | None): id da conta no banco — atributo PROTEGIDO.
    """

    def __init__(self, usuario_id):
        """
        Construtor: recebe o id do usuário logado e localiza a conta dele.

        Parâmetros:
            usuario_id (int): id do usuário autenticado (vem do objeto
            Usuario após o login, no main.py).
        """
        self.usuario_id = usuario_id
        self._id_conta = None
        self.carregar_dados_conta()  # busca no banco o id da conta do usuário

    def carregar_dados_conta(self):
        """
        Localiza no banco a conta vinculada ao usuário (relação 1 : 1)
        e guarda o id dela em self._id_conta para uso nas demais operações.
        """
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM contas WHERE usuario_id = %s", (self.usuario_id,))
        conta = cursor.fetchone()
        cursor.close()
        conn.close()
        if conta:
            self._id_conta = conta['id']

    @property
    def saldo(self):
        """
        Property somente leitura do saldo (ENCAPSULAMENTO).

        Em vez de manter o saldo em uma variável na memória (que poderia
        ficar desatualizada ou ser alterada indevidamente), cada leitura
        consulta o valor REAL gravado no banco de dados.

        Retorno:
            float: saldo atual da conta (0.0 se a conta não existir).
        """
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("SELECT saldo FROM contas WHERE id = %s", (self._id_conta,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return float(resultado[0]) if resultado else 0.0

    def mostrar_saldo(self):
        """Tela de Saldo (opção 3): exibe o saldo atual formatado em reais."""
        print("\n=== TELA DE SALDO ===")
        print(f"Seu saldo atual é de: R$ {self.saldo:.2f}")

    def registrar_historico(self, tipo_transacao_id, valor):
        """
        Grava uma movimentação na tabela 'transacoes' (histórico/extrato).

        Parâmetros:
            tipo_transacao_id (int): 1 = Depósito, 2 = Saque
                                     (tabela de domínio 'tipos_transacao').
            valor (float): valor movimentado (sempre positivo).

        Observação:
            A coluna data_hora tem DEFAULT CURRENT_TIMESTAMP no banco,
            por isso não precisamos enviá-la: o MySQL registra o momento
            exato da transação automaticamente.
        """
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transacoes (conta_id, tipo_transacao_id, valor) VALUES (%s, %s, %s)",
            (self._id_conta, tipo_transacao_id, valor)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def realizar_transacao(self):
        """
        Tela de Transferência (opção 5): depósito (+) ou saque (-).

        Regras de negócio aplicadas (na ordem):
            1. O sinal deve ser '+' (depósito) ou '-' (saque).
            2. O valor deve ser numérico (try/except ValueError).
            3. O valor deve ser MAIOR que zero.
            4. No saque, o saldo deve ser suficiente.
            5. Toda operação válida atualiza o saldo E registra a
               transação no histórico (extrato).
        """
        print("\n=== TELA DE TRANSFERÊNCIA (DEPÓSITO / SAQUE) ===")
        sinal = input("Digite '+' para DEPÓSITO ou '-' para SAQUE: ").strip()

        if sinal in ['+', '-']:
            try:
                valor = float(input("Digite o valor da transação: "))

                # Regra: só valores positivos
                if valor <= 0:
                    print("[ERRO] O valor deve ser maior que zero.")
                    return

                if sinal == '+':
                    # DEPÓSITO: soma ao saldo atual
                    novo_saldo = self.saldo + valor
                    tipo_id = 1  # 1 = Depósito na tabela tipos_transacao
                else:
                    # SAQUE: verifica se há saldo suficiente antes de debitar
                    if self.saldo < valor:
                        print("[ERRO] Saldo insuficiente para realizar o saque.")
                        return
                    novo_saldo = self.saldo - valor
                    tipo_id = 2  # 2 = Saque

                # Persiste o novo saldo no banco (UPDATE)
                conn = obter_conexao()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contas SET saldo = %s WHERE id = %s",
                    (novo_saldo, self._id_conta)
                )
                conn.commit()
                cursor.close()
                conn.close()

                # Regra: toda transação vai para o histórico
                self.registrar_historico(tipo_id, valor)
                print(f"[OK] Operação realizada com sucesso! Novo saldo: R$ {novo_saldo:.2f}")

            except ValueError:
                # Usuário digitou texto em vez de número
                print("[ERRO] Digite um valor numérico válido.")
        else:
            print("[ERRO] Opção inválida.")

    def mostrar_extrato(self):
        """
        Tela de Extrato (opção 4): lista todas as movimentações da conta.

        Destaque técnico:
            Usa INNER JOIN entre 'transacoes' e 'tipos_transacao' para
            trazer o NOME do tipo ('Depósito'/'Saque') em vez do número,
            demonstrando o relacionamento entre tabelas do MER.
            ORDER BY data_hora DESC = movimentações mais recentes primeiro.
        """
        print("\n=== TELA DE EXTRATO ===")
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.valor, t.data_hora, tt.nome as tipo
            FROM transacoes t
            INNER JOIN tipos_transacao tt ON t.tipo_transacao_id = tt.id
            WHERE t.conta_id = %s ORDER BY t.data_hora DESC
        """, (self._id_conta,))
        linhas = cursor.fetchall()
        cursor.close()
        conn.close()

        if not linhas:
            # Regra: se não houver movimentações, informa o usuário
            print("Nenhuma transferência ou movimentação realizada nesta conta.")
        else:
            for linha in linhas:
                # Sinal visual: '+' para depósitos, '-' para saques
                sinal = "+" if linha['tipo'] == 'Depósito' else "-"
                print(f"[{linha['data_hora']}] {linha['tipo']}: {sinal}R$ {linha['valor']:.2f}")
        print("-" * 30)
        print(f"SALDO ATUAL: R$ {self.saldo:.2f}")
