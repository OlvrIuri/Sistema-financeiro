"""
main.py
=======
Ponto de entrada do Sistema Financeiro (Conta Bancária Digital).

Papel deste arquivo:
    * Exibir os MENUS em modo texto e controlar a navegação entre telas.
    * Controlar a SESSÃO: a variável user_logado guarda o objeto Usuario
      autenticado (None = ninguém logado).
    * Direcionar o fluxo conforme o PERFIL:
        - perfil_id = 1 (Gerente)  -> painel administrativo (CRUD)
        - perfil_id = 2 (Cliente)  -> menu financeiro (saldo/extrato/transf.)

Observação de arquitetura:
    O main NÃO contém regra financeira nem SQL de negócio: ele apenas
    orquestra as classes Usuario e ContaBancaria (separação de
    responsabilidades). A exceção é o painel do Gerente, que concentra o
    CRUD administrativo exigido no trabalho.

Apresentação: este arquivo faz parte das PARTES 5 (menus/fluxo) e 6 (demo).
"""

from Usuario import Usuario
from ContaBancaria import ContaBancaria
from conexao import obter_conexao


def menu_gerente():
    """
    Painel administrativo exclusivo do perfil GERENTE (perfil_id = 1).

    Implementa o CRUD sobre a tabela 'usuarios':
        (1) Read   - listar todos os usuários cadastrados;
        (2) Update - alterar o nome de um usuário pelo id;
        (3) Delete - excluir usuário (e, por CASCADE, a conta e as
                     transações dele) — Gerentes não podem ser excluídos;
        (0) Logout administrativo.

    O Create do CRUD é o próprio Cadastro do menu principal.

    Segurança da exclusão:
        A cláusula "AND perfil_id != 1" impede que um Gerente seja
        apagado pelo painel. O ON DELETE CASCADE definido no script.sql
        garante que contas e transações do usuário excluído sejam
        removidas automaticamente pelo banco (integridade referencial).
    """
    while True:
        print("\n" + "=" * 45)
        print("    PAINEL DO GERENTE - CONTROLE DO BANCO")
        print("=" * 45)
        print(" (1) Listar Todos os Usuários Cadastrados (Read)")
        print(" (2) Atualizar Nome de um Usuário (Update)")
        print(" (3) Excluir Usuário e Conta do Banco (Delete)")
        print(" (0) Fazer Logout Administrativo")
        print("=" * 45)

        opcao = input("Escolha uma opção: ").strip()
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)

        if opcao == "1":
            # READ: lista id, nome, e-mail e perfil de todos os usuários
            print("\n=== LISTA DE USUÁRIOS NO BANCO ===")
            cursor.execute("SELECT id, nome, email, perfil_id FROM usuarios")
            usuarios = cursor.fetchall()
            for u in usuarios:
                perfil = "Gerente" if u['perfil_id'] == 1 else "Cliente"
                print(f"ID: {u['id']} | Nome: {u['nome']} | E-mail: {u['email']} | Perfil: {perfil}")

        elif opcao == "2":
            # UPDATE: altera o nome de um usuário identificado pelo id
            print("\n=== ATUALIZAR USUÁRIO ===")
            try:
                uid = int(input("Digite o ID do usuário que deseja alterar: "))
                novo_nome = input("Digite o novo nome completo: ").strip()
                if novo_nome != "":
                    cursor.execute("UPDATE usuarios SET nome = %s WHERE id = %s", (novo_nome, uid))
                    conn.commit()
                    print("[OK] Nome do usuário modificado com sucesso!")
                else:
                    print("[ERRO] O nome não pode ser vazio.")
            except ValueError:
                print("[ERRO] ID inválido.")

        elif opcao == "3":
            # DELETE: remove usuário (exceto Gerentes) — CASCADE limpa o resto
            print("\n=== EXCLUIR CONTA E USUÁRIO ===")
            try:
                uid = int(input("Digite o ID do usuário que deseja DELETAR: "))
                # O ON DELETE CASCADE no banco apaga conta e transações juntas
                cursor.execute("DELETE FROM usuarios WHERE id = %s AND perfil_id != 1", (uid,))
                conn.commit()
                if cursor.rowcount > 0:
                    print("[OK] Usuário e todas as suas contas associadas foram removidos.")
                else:
                    print("[ERRO] Usuário não encontrado ou você tentou apagar um Gerente.")
            except ValueError:
                print("[ERRO] ID inválido.")

        elif opcao == "0":
            print("\nSaindo do painel administrativo...")
            cursor.close()
            conn.close()
            break
        else:
            print("[ERRO] Opção inválida.")

        cursor.close()
        conn.close()


def main():
    """
    Laço principal do aplicativo (Tela de Menu Principal).

    Estados possíveis:
        * user_logado is None  -> visitante: só pode Cadastrar, Logar ou Sair.
        * user_logado é Usuario -> cliente autenticado: Saldo, Extrato,
          Transferência e Logout ficam liberados (regra: essas telas
          EXIGEM login prévio — por isso nem aparecem antes dele).

    Fluxo do login:
        Após autenticar, se o perfil for Gerente (perfil_id == 1), o
        sistema abre direto o painel administrativo e, ao sair dele,
        desloga o gerente (user_logado = None).
    """
    print("\nBem-vindo(a) ao Sistema Financeiro!")
    user_logado = None  # controla a sessão: None = ninguém logado

    while True:
        print("\n" + "=" * 45)
        print("    SISTEMA FINANCEIRO - CONTA DIGITAL")
        print("=" * 45)

        # ---------- ESTADO 1: NINGUÉM LOGADO ----------
        if not user_logado:
            print(" (1) Cadastro")
            print(" (2) Login")
            print(" (0) Sair do aplicativo")
            print("=" * 45)
            opcao = input("Escolha uma opção: ").strip()

            if opcao == "1":
                # Cria um objeto Usuario e delega o cadastro à classe
                u = Usuario()
                u.cadastrar()
            elif opcao == "2":
                print("\n=== TELA DE LOGIN ===")
                email = input("E-mail: ").strip().lower()
                senha = input("Senha: ").strip()

                u = Usuario()
                if u.login(email, senha):
                    user_logado = u  # sessão aberta
                    # Gerente vai direto para o CRUD administrativo
                    if user_logado.perfil_id == 1:
                        menu_gerente()
                        user_logado = None  # desloga o gerente ao sair
            elif opcao == "0":
                print("\nAté logo!")
                break
            else:
                print("\n[ERRO] Opção inválida. Tente novamente.")

        # ---------- ESTADO 2: CLIENTE LOGADO ----------
        else:
            print(" (3) Saldo")
            print(" (4) Extrato")
            print(" (5) Transferencia (deposito / saque)")
            print(" (0) Fazer Logout (Sair da Conta)")
            print("=" * 45)
            opcao = input("Escolha uma opção: ").strip()

            # Instancia a conta do usuário logado (associação Usuario -> Conta)
            conta = ContaBancaria(user_logado.id)

            if opcao == "3":
                conta.mostrar_saldo()
            elif opcao == "4":
                conta.mostrar_extrato()
            elif opcao == "5":
                conta.realizar_transacao()
            elif opcao == "0":
                print(f"\nLogout efetuado da conta de {user_logado.nome}.")
                user_logado = None  # encerra a sessão
            else:
                print("\n[ERRO] Opção inválida. Tente novamente.")


# Só executa main() quando o arquivo é rodado diretamente
# (python main.py), e não quando é importado por outro módulo.
if __name__ == "__main__":
    main()
