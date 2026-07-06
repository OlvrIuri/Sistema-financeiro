# Sistema Financeiro — Conta Bancária Digital (POO 2)

Projeto da disciplina de Programação Orientada a Objetos 2.

## Conteúdo
| Arquivo | Descrição |
|---|---|
| `main.py` | Menus, controle de sessão e painel do Gerente (CRUD) |
| `Usuario.py` | Classe Usuario — cadastro e login |
| `ContaBancaria.py` | Classe ContaBancaria — saldo, transações e extrato |
| `conexao.py` | Conexão com o MySQL |
| `script.sql` | Criação das tabelas e dados iniciais |
| `MER.png` | Diagrama Entidade-Relacionamento |
| `GUIA_DO_CODIGO.md` | Guia interno de leitura para o grupo |
| `DIVISAO_APRESENTACAO.md` | Divisão das falas entre os 6 integrantes |
| `Apresentacao_Sistema_Financeiro.pdf` | Slides para o professor |

## Como rodar
1. Iniciar o MySQL (USBWebserver, porta 3307, senha `usbw`)
2. `CREATE DATABASE sistema_financeiro;` e executar o `script.sql`
3. `pip install mysql-connector-python`
4. `python main.py`

Gerente de teste: `gerente@banco.com` / senha `1234`
